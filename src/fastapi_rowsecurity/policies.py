from typing import List

from alembic_utils.pg_policy import PGPolicy

from .rls_entity import EnableRowLevelSecurity, ForceRowLevelSecurity


def get_policies(Base) -> List[PGPolicy]:
    policy_lists = []
    for mapper in Base.registry.mappers:
        if not hasattr(mapper.class_, "__rls_policies__"):
            continue
        table_name = mapper.tables[0].fullname
        schema_name = mapper.tables[0].schema or "public"
        # Set the default row-level security policy
        policy_lists.append(EnableRowLevelSecurity(schema=schema_name, on_entity=table_name))
        policy_lists.append(ForceRowLevelSecurity(schema=schema_name, on_entity=table_name))
        for ix, permission in enumerate(mapper.class_.__rls_policies__()):
            table_policies = [permission.policy] if isinstance(permission.policy, str) else permission.policy
            for pol in table_policies:
                policy_name = f"{table_name}_{permission.__class__.__name__}_{pol}_policy_{ix}".lower()
                if pol in ["ALL", "SELECT", "UPDATE", "DELETE"]:
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
                elif pol in ["INSERT"]:
                    policy_lists.append(
                        PGPolicy(
                            schema=schema_name,
                            signature=policy_name,
                            on_entity=table_name,
                            definition=f"""
                            AS {permission.__class__.__name__.upper()}
                            FOR {pol}
                            WITH CHECK ({permission.principal})
                        """,
                        )
                    )
                else:
                    raise ValueError(f'Unknown policy "{pol}"')
    return policy_lists
