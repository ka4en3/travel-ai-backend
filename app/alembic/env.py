# alembic/env.py

from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine
import asyncio

from logging.config import fileConfig

from sqlalchemy import engine_from_config, pool
from sqlalchemy.engine import Connection
from alembic import context

# import settings and metadata
from utils.config import settings
from db.base import Base

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config


config.set_main_option("sqlalchemy.url", settings.db_async_url)
# !!! DEBUG !!!
print("DB URL:", config.get_main_option("sqlalchemy.url"))
# !!! DEBUG !!!


# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# !!! DEBUG !!!
print("Tables in metadata:")
for table_name in target_metadata.tables.keys():
    print(f" - {table_name}")
# !!! DEBUG !!!

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline():
    """Run migrations in 'offline' mode."""
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    """Run migrations in 'online' mode."""
    try:
        connectable = create_async_engine(
            config.get_main_option("sqlalchemy.url"),
            poolclass=pool.NullPool,
        )

        async def do_run_migrations():
            try:
                async with connectable.connect() as connection:

                    def do_migrations(sync_conn):
                        try:
                            context.configure(
                                connection=sync_conn,
                                target_metadata=target_metadata,
                                compare_type=True,
                                compare_server_default=True,
                                transaction_per_migration=True,
                            )
                            context.run_migrations()

                            # !Explicitly commit the transaction!
                            # sync_conn.commit()

                            print("Migrations executed successfully!")
                        except Exception as e:
                            print(f"Error in do_migrations: {e}")
                            raise

                    await connection.run_sync(do_migrations)
            except Exception as e:
                print(f"Error in do_run_migrations: {e}")
                raise

        asyncio.run(do_run_migrations())
    except Exception as e:
        print(f"Error in run_migrations_online: {e}")
        raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
