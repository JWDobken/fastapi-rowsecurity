<!-- These are examples of badges you might want to add to your README:
     please update the URLs accordingly

[![Built Status](https://api.cirrus-ci.com/github/jwdobken/fastapi-rowsecurity.svg?branch=main)](https://cirrus-ci.com/github/<USER>/fastapi-rowsecurity)
[![ReadTheDocs](https://readthedocs.org/projects/fastapi-rowsecurity/badge/?version=latest)](https://fastapi-rowsecurity.readthedocs.io/en/stable/)
[![Coveralls](https://img.shields.io/coveralls/github/<USER>/fastapi-rowsecurity/main.svg)](https://coveralls.io/r/<USER>/fastapi-rowsecurity)
[![PyPI-Server](https://img.shields.io/pypi/v/fastapi-rowsecurity.svg)](https://pypi.org/project/fastapi-rowsecurity/)
[![Conda-Forge](https://img.shields.io/conda/vn/conda-forge/fastapi-rowsecurity.svg)](https://anaconda.org/conda-forge/fastapi-rowsecurity)
[![Monthly Downloads](https://pepy.tech/badge/fastapi-rowsecurity/month)](https://pepy.tech/project/fastapi-rowsecurity)
[![Twitter](https://img.shields.io/twitter/url/http/shields.io.svg?style=social&label=Twitter)](https://twitter.com/fastapi-rowsecurity)
-->

# FastAPI Row Security 🚣‍♂️

Row-Level Security (RLS) in SQLAlchemy for PostgreSQL with [Row Security Policies](https://www.postgresql.org/docs/current/ddl-rowsecurity.html):

- Restrict access to specific rows 🔒 based on user permissions, minimizing unauthorized data exposure.
- Managing who sees what becomes a breeze 😎, without solely relying on application-level permissions.
- Perfect for Scalability and Multi-Tenancy: keep the data playground organized 🏢, ensuring each tenant plays in their own sandbox.

> **Warning**
> Understand that the [database superuser](https://www.postgresql.org/docs/current/role-attributes.html) bypasses all permission checks, except the right to log in. This is a dangerous privilege and should not be used in combination with RLS.

## Installation

Use pip to install from PyPI:

```cmd
pip install fastapi-rowsecurity
```

## Basic Usage

In your SQLAlchemy model, create a `classmethod` named `__rls_policies__` that returns a list of `Permissive` or `Restrictive` policies:

```py
from fastapi_rowsecurity import Permissive, set_rls_policies
from fastapi_rowsecurity.principals import Authenticated, UserOwner

Base = declarative_base()
set_rls_policies(Base) # <- create all policies


class Item(Base):
    __tablename__ = "items"

    id = Column(Integer, primary_key=True)
    title = Column(String, index=True)
    owner_id = Column(Integer, ForeignKey("users.id"))
    owner = relationship("User", back_populates="items")

    @classmethod
    def __rls_policies__(cls):
        return [
            Permissive(principal=Authenticated, policy="SELECT"),
            Permissive(principal=UserOwner, policy=["INSERT", "UPDATE", "DELETE"]),
        ]
```

The above implies that any authenticated user can read all items; but can only insert, update or delete owned items.

- `principal`: any Boolean expression as a string;
- `policy`: any of `ALL`/`SELECT`/`INSERT`/`UPDATE`/`DELETE`.

Next, attach the `current_user_id` (or other [runtime parameters](https://www.postgresql.org/docs/current/sql-set.html) that you need) to the user session:

```py
# ... def get_session() -> Session:
session.execute(text(f"SET app.current_user_id = {current_user_id}"))
```

Find a simple example in the ![tests](./tests/simple_model.py).

## Backlog first release

- [ ] Change policies when model changes (prio!!)
- [ ] Documentation

then ...

- [ ] Support for Alembic
- [ ] How to deal with `BYPASSRLS` such as table owners?
- [ ] When item is tried to delete, no error is raised?

## Final note

At the moment this module is work-in-progress and therefore experimental. All feedback and ideas are 100% welcome! So feel free to contribute or reach out to me!
