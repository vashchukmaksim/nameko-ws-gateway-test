import os
import sys
# to import from src dir
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.conf import DeclarativeBase
import src.models

from logging.config import fileConfig

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

uri = 'postgresql://{}:{}@{}:{}/{}'.format(
    os.environ.get('POSTGRES_DB_USERNAME', 'dev_user'),
    os.environ.get('POSTGRES_DB_PASSWORD', '0000'),
    os.environ.get('POSTGRES_DB_HOST', 'localhost'),
    os.environ.get('POSTGRES_DB_PORT', '5432'),
    os.environ.get('POSTGRES_DB_NAME', 'tg')
)

# Use SSL mode for production migration
if os.environ.get('POSTGRES_DB_USERNAME', 'dev_user') != 'dev_user':
    uri += '?sslmode=require'

# Update sqlalchemy URI using environment variables
config.set_main_option('sqlalchemy.url', uri)

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = DeclarativeBase.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.

def include_object(object, name, type_, reflected, compare_to):
    if type_ == "table" and object.schema != target_metadata.schema:
        return False
    else:
        return True


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        version_table_schema=target_metadata.schema,
        include_schemas=True,
        include_object=include_object
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            version_table_schema=target_metadata.schema,
            include_schemas=True,
            include_object=include_object
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
