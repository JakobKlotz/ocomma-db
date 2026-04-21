# For Developers

Following steps are needed for initial development and database setup with 
`alembic`.

## `alembic` setup

Init the folder structure:

```bash
alembic init alembic
```

### Customize files

Create a dedicated `.env` for the database secrets and switch to `env.py`, 
add lines to load the variables. 

### Autogenerate revision

With `alembic` autogenerate the first revision from the `sqlalchemy` models:

```bash
alembic revision --autogenerate -m "db table structure"
```

### Extensions

Navigate to the first revision and ensure that the `postgis` extension is
enabled. Add following at the beginning of `upgrade()`:

```python
op.execute("CREATE EXTENSION IF NOT EXISTS postgis")
```

... and at the end to `downgrade()`:

```python
op.execute("DROP EXTENSION postgis")
```

---

> [!NOTE]
> By default, `postgis` images have the `postgis` extensions pre-initialized.

#### `postgis_topology` & `postgis_tiger_geocoder`

... these two extension also come pre-initialized with the image. Since both of
them are not used, they are dropped alongside their respective schemas.

Add these lines to the first `alembic` revision in `upgrade()`:

```python
op.execute("""
    DROP EXTENSION IF EXISTS postgis_tiger_geocoder CASCADE;
    DROP EXTENSION IF EXISTS postgis_topology CASCADE;
    DROP SCHEMA IF EXISTS tiger CASCADE;
    DROP SCHEMA IF EXISTS tiger_data CASCADE;
    DROP SCHEMA IF EXISTS topology CASCADE;
""")
```

### Apply revision

```bash
alembic upgrade head
```

### Helpers

Couple of commands that are often necessary:

Reset to base, with:

```bash
alembic downgrade base
```
