from alembic_utils.on_entity_mixin import OnEntityMixin
from alembic_utils.replaceable_entity import ReplaceableEntity
from sqlalchemy import text as sql_text


class EnableRowLevelSecurity(OnEntityMixin, ReplaceableEntity):

    def __init__(self, schema: str, on_entity: str, **kwargs):
        super().__init__(schema=schema, on_entity=on_entity, definition="", signature="")

    def to_sql_statement_create(self):
        return sql_text(f"ALTER TABLE {self.on_entity} ENABLE ROW LEVEL SECURITY;")

    def to_sql_statement_drop(self):
        return sql_text(f"ALTER TABLE {self.on_entity} DISABLE ROW LEVEL SECURITY;")


class ForceRowLevelSecurity(OnEntityMixin, ReplaceableEntity):

    def __init__(self, schema: str, on_entity: str, **kwargs):
        super().__init__(schema=schema, on_entity=on_entity, definition="", signature="")

    def to_sql_statement_create(self):
        return sql_text(f"ALTER TABLE {self.on_entity} FORCE ROW LEVEL SECURITY;")

    def to_sql_statement_drop(self):
        return sql_text(f"ALTER TABLE {self.on_entity} DISABLE ROW LEVEL SECURITY;")
