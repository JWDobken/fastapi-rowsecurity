from enum import Enum
from typing import List, Literal, Union

from pydantic import BaseModel
from sqlalchemy import text


class Command(str, Enum):
    # policies: https://www.postgresql.org/docs/current/sql-createpolicy.html
    all = "ALL"
    select = "SELECT"
    insert = "INSERT"
    update = "UPDATE"
    delete = "DELETE"


class Policy(BaseModel):
    definition: str
    expr: str
    cmd: Union[Command, List[Command]]

    def get_sql_policies(self, table_name: str, name_suffix: str = "0"):
        commands = [self.cmd] if isinstance(self.cmd, str) else self.cmd
        policy_lists = []
        for cmd in commands:
            policy_name = (
                f"{table_name}_{self.definition}" f"_{cmd}_policy_{name_suffix}".lower()
            )
            if cmd in ["ALL", "SELECT", "UPDATE", "DELETE"]:
                policy_lists.append(
                    text(
                        f"""
                        CREATE POLICY {policy_name} ON {table_name}
                        AS {self.definition}
                        FOR {cmd}
                        USING ({self.expr})
                        """
                    )
                )
            elif cmd in ["INSERT"]:
                policy_lists.append(
                    text(
                        f"""
                        CREATE POLICY {policy_name} ON {table_name}
                        AS {self.definition}
                        FOR {cmd}
                        WITH CHECK ({self.expr})
                        """
                    )
                )
            else:
                raise ValueError(f'Unknown policy command"{cmd}"')
        return policy_lists


class Permissive(Policy):
    definition: Literal["PERMISSIVE"] = "PERMISSIVE"


class Restrictive(Policy):
    definition: Literal["RESTRICTIVE"] = "RESTRICTIVE"
