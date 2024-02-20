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

## Installation

Use pip to install from PyPI:

```cmd
pip install fastapi-rowsecurity
```

## Basic Usage

> WARNING!! The [database superuser](https://www.postgresql.org/docs/current/role-attributes.html) bypasses all permission checks, except the right to log in. This is a dangerous privilege and should not be used in combination with RLS.

...

## Disable `BYPASSRLS`

In PostgreSQL, the BYPASSRLS privilege allows a role to bypass row-level security (RLS) policies. This is a powerful privilege that allows users to access data without being subject to the restrictions imposed by RLS policies. Disabling BYPASSRLS is crucial for maintaining the integrity of your row-level security policies.

To revoke the BYPASSRLS privilege from all roles, you can execute the following SQL statement:

```sql
REVOKE BYPASSRLS ON DATABASE your_database_name FROM PUBLIC;
```

Replace your_database_name with the name of your database.

This statement revokes the BYPASSRLS privilege from the PUBLIC role, which effectively removes it from all roles in the database.

Make sure you have appropriate privileges to execute this command, typically superuser privileges or ownership of the database.

get all roles that have

```sql
SELECT * FROM pg_roles WHERE rolbypass = TRUE;
ALTER ROLE jwdobken WITH NOBYPASSRLS;
```

BYPASSRLS | NOBYPASSRLS – determine if the role is to bypass the row-level security (RLS) policy.
