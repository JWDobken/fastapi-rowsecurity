from enum import Enum
from typing import List, Union

from pydantic import BaseModel


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
