from typing import List

from alembic_utils.pg_function import PGFunction

drop_all_policies_on_table = PGFunction(
    schema="public",
    signature="drop_all_policies_on_table(target_schema text,target_table_name text)",
    definition="""
RETURNS void LANGUAGE plpgsql AS $$
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
                sql_text := format('DROP POLICY "%s" on %I.%I', 
                    policy_name, target_schema, target_table_name);
                RAISE NOTICE '%', sql_text;
                EXECUTE sql_text;
            END LOOP;
END $$;
""",
)


def get_functions() -> List[PGFunction]:
    return []
