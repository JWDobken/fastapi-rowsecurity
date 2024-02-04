import logging
from enum import Enum
from typing import List, Union

from pydantic import BaseModel
from sqlalchemy import text

# constants

Allow = "PERMISSIVE"  # acl "allow" action
Deny = "RESTRICTIVE"  # acl "deny" action

Everyone = "true"  # user principal for everyone
Authenticated = "true"  # authenticated user principal (not correct yet)
#
UserOwnerInt = "owner_id = current_setting('app.current_user_id')::integer"
UserOwnerUuid = "owner_id = current_setting('app.current_user_id')::uuid"


class Policy(str, Enum):
    # policies: https://www.postgresql.org/docs/current/sql-createpolicy.html
    all = "ALL"
    select = "SELECT"
    insert = "INSERT"
    update = "UPDATE"
    delete = "DELETE"


class Permissive(BaseModel):
    principal: str
    policy: Union[Policy, List[Policy]]


class Restrictive(BaseModel):
    principal: str
    policy: Union[Policy, List[Policy]]


# functions


def create_policy_functions(connection):
    drop_all_policies = """
        CREATE OR REPLACE FUNCTION drop_all_policies_on_table(
            target_schema text,
            target_table_name text
        ) RETURNS void LANGUAGE plpgsql AS $$
        DECLARE 
            policy_name text;
            sql_text    text;
        BEGIN 
            FOR policy_name IN (
                SELECT policyname 
                FROM pg_policies 
                WHERE schemaname = target_schema AND tablename = target_table_name
            )
            LOOP
                sql_text := format('DROP POLICY "%s" on %I.%I', policy_name, target_schema, target_table_name);
                RAISE NOTICE '%', sql_text;
                EXECUTE sql_text;
            END LOOP;
        END $$;
        """
    connection.execute(text(drop_all_policies))


# policies
__permissions__ = {"view": ["SELECT"], "edit": ["INSERT", "UPDATE"], "delete": ["DELETE"], "all": ["ALL"]}


def create_policies(mapper, connection, force: bool):
    logging.debug(f"Create policies for {mapper.entity}")
    table_name = mapper.tables[0].name
    schema_name = mapper.tables[0].schema or "public"

    # Policy function for filtering rows based on user_id
    policy_functions = []
    for ix, permission in enumerate(mapper.class_.__rls_policies__()):
        for pol in list([permission.policy] if isinstance(permission.policy, str) else permission.policy):
            policy_name = f"{table_name}_{permission.__class__.__name__}_{pol}_policy_{ix}".lower()
            using_check = "USING" if pol in ["SELECT", "DELETE"] else "WITH CHECK"
            policy_functions.append(
                text(
                    f"""
                CREATE POLICY {policy_name} ON {table_name}
                AS {permission.__class__.__name__.upper()}
                FOR {pol}
                {using_check} ({permission.principal});
                """
                )
            )

    # Set the default row-level security policy
    default_policy = text(
        f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;",
    )
    force_policy = text(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;")

    # Execute DDL statements
    connection.execute(text(f"SELECT drop_all_policies_on_table('{schema_name}', '{table_name}');"))
    for policy_function in policy_functions:
        connection.execute(policy_function)
    connection.execute(default_policy)
    connection.execute(force_policy)


def delete_policies(mapper, connection):
    logging.debug(f"Delete policies for {mapper.entity}")
    table_name = mapper.tables[0].name
    schema_name = mapper.tables[0].schema or "public"
    connection.execute(
        text(
            f"""SELECT drop_all_policies_on_table('{schema_name}', '{table_name}');
            ALTER TABLE {table_name} DISABLE ROW LEVEL SECURITY;""",
        )
    )


def set_rls_policies(base, connection, force: bool = True):
    create_policy_functions(connection)
    for mapper in base.registry.mappers:
        if hasattr(mapper.class_, "__rls_policies__"):
            create_policies(mapper, connection, force)
        else:
            delete_policies(mapper, connection)
    connection.commit()
