from typing import Type

from sqlalchemy import event
from sqlalchemy.ext.declarative import DeclarativeMeta

from .policies import get_policies


def set_rls_policies(Base: Type[DeclarativeMeta]):
    @event.listens_for(Base.metadata, "after_create")
    def receive_after_create(target, connection, tables, **kw):
        policies = get_policies(Base)
        for ent in policies:
            connection.execute(ent.to_sql_statement_create())
        connection.commit()
