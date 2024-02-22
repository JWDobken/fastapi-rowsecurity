from typing import List

from alembic_utils.pg_policy import PGPolicy


def get_policies(Base) -> List[PGPolicy]:
    policy_lists = []
    for mapper in Base.registry.mappers:
        if not hasattr(mapper.class_, "__rls_policies__"):
            continue
        table_name = mapper.tables[0].fullname
        schema_name = mapper.tables[0].schema or "public"
        # Set the default row-level security policy
        # policies.append((text(f"ALTER TABLE {table_name} ENABLE ROW LEVEL SECURITY;")))
        # policies.append((text(f"ALTER TABLE {table_name} FORCE ROW LEVEL SECURITY;")))
        for ix, permission in enumerate(mapper.class_.__rls_policies__()):
            table_policies = [permission.policy] if isinstance(permission.policy, str) else permission.policy
            for pol in table_policies:
                policy_name = f"{table_name}_{permission.__class__.__name__}_{pol}_policy_{ix}".lower()
                policy_lists.append(
                    PGPolicy(
                        schema=schema_name,
                        signature=policy_name,
                        on_entity=table_name,
                        definition=f"""
                        AS {permission.__class__.__name__.upper()}
                        FOR {pol}
                        USING ({permission.principal})
                    """,
                    )
                )
    return policy_lists
