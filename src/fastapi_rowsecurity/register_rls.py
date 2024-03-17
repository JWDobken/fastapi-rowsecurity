from typing import Type

from alembic.autogenerate import comparators, renderers
from alembic.operations import MigrateOperation, Operations
from sqlalchemy import event, text
from sqlalchemy.ext.declarative import DeclarativeMeta

from .create_policies import create_policies

############################
# OPERATIONS
############################


@Operations.register_operation("enable_rls")
class EnableRlsOp(MigrateOperation):
    """Enable RowLevelSecurity."""

    def __init__(self, tablename, schemaname=None):
        self.tablename = tablename
        self.schemaname = schemaname

    @classmethod
    def enable_rls(cls, operations, tablename, **kw):
        """Issue a "CREATE SEQUENCE" instruction."""

        op = EnableRlsOp(tablename, **kw)
        return operations.invoke(op)

    def reverse(self):
        # only needed to support autogenerate
        return DisableRlsOp(self.tablename, schemaname=self.schemaname)


@Operations.register_operation("disable_rls")
class DisableRlsOp(MigrateOperation):
    """Drop a SEQUENCE."""

    def __init__(self, tablename, schemaname=None):
        self.tablename = tablename
        self.schemaname = schemaname

    @classmethod
    def disable_rls(cls, operations, tablename, **kw):
        """Issue a "DROP SEQUENCE" instruction."""

        op = DisableRlsOp(tablename, **kw)
        return operations.invoke(op)

    def reverse(self):
        # only needed to support autogenerate
        return EnableRlsOp(self.tablename, schemaname=self.schemaname)


############################
# IMPLEMENTATION
############################


@Operations.implementation_for(EnableRlsOp)
def render_enable_rls(operations, operation):
    if operation.schemaname is not None:
        name = "%s.%s" % (operation.schemaname, operation.tablename)
    else:
        name = operation.tablename
    operations.execute("ALTER TABLE %s ENABLE ROW LEVEL SECURITY" % name)


@Operations.implementation_for(DisableRlsOp)
def drop_sequence(operations, operation):
    if operation.schemaname is not None:
        name = "%s.%s" % (operation.schemaname, operation.sequence_name)
    else:
        name = operation.tablename
    operations.execute("ALTER TABLE %s DISABLE ROW LEVEL SECURITY" % name)


############################
# RENDER
############################


@renderers.dispatch_for(EnableRlsOp)
def render_enable_rls(autogen_context, op):
    return "op.enable_rls(%r, **%r)" % (op.tablename, {"schemaname": op.schemaname})


@renderers.dispatch_for(DisableRlsOp)
def render_disable_rls(autogen_context, op):
    return "op.disable_rls(%r, **%r)" % (op.tablename, {"schemaname": op.schemaname})


############################
# COMPARATORS
############################


def check_table_exists(conn, schemaname, tablename) -> bool:
    result = conn.execute(
        text(
            f"""SELECT EXISTS (
    SELECT 1
    FROM information_schema.tables
    WHERE table_schema = '{schemaname if schemaname else "public"}'
    AND table_name = '{tablename}'
);"""
        )
    ).scalar()
    return result


def check_rls_enabled(conn, schemaname, tablename) -> bool:
    result = conn.execute(
        text(
            f"""select relrowsecurity
        from pg_class
        where oid = '{tablename}'::regclass;"""
        )
    ).scalar()
    return result


@comparators.dispatch_for("table")
def compare_table_level(
    autogen_context, modify_ops, schemaname, tablename, conn_table, metadata_table
):
    # STEP 1. check table exists and RLS is enabled
    table_exists = check_table_exists(autogen_context.connection, schemaname, tablename)
    rls_enabled_db = (
        check_rls_enabled(autogen_context.connection, schemaname, tablename)
        if table_exists
        else False
    )

    # STEP 2. check if RLS should be enabled
    rls_enabled_meta = tablename in metadata_table.metadata.info["rls_policies"]

    # STEP 3. apply
    if rls_enabled_meta and not rls_enabled_db:
        modify_ops.ops.append(EnableRlsOp(tablename=tablename, schemaname=schemaname))
    if rls_enabled_db and not rls_enabled_meta:
        modify_ops.ops.append(DisableRlsOp(tablename=tablename, schemaname=schemaname))


def set_metadata_info(Base: Type[DeclarativeMeta]):
    """RLS policies are first added to the Metadata before applied."""
    Base.metadata.info.setdefault("rls_policies", dict())
    for mapper in Base.registry.mappers:
        if not hasattr(mapper.class_, "__rls_policies__"):
            continue
        Base.metadata.info["rls_policies"][
            mapper.tables[0].fullname
        ] = mapper.class_.__rls_policies__
        # [
        #     p.model_dump(mode="json") for p in mapper.class_.__rls_policies__
        # ]


def register_rls(Base: Type[DeclarativeMeta]):

    # required for `alembic revision --autogenerate``
    set_metadata_info(Base)

    @event.listens_for(Base.metadata, "after_create")
    def receive_after_create(target, connection, tables, **kw):

        # required for `Base.metadata.create_all()`
        set_metadata_info(Base)
        create_policies(Base, connection)
