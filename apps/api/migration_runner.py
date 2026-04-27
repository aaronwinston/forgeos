"""Migration runner for executing pending Alembic migrations."""

import logging
from pathlib import Path
from alembic.config import Config as AlembicConfig
from alembic import command
from config import settings

logger = logging.getLogger(__name__)


def run_pending_migrations() -> None:
    """Execute pending migrations from the migrations directory.
    
    This is called during application startup to ensure the database schema
    is up to date with the latest migrations.
    """
    # Get the path to the migrations directory
    migrations_dir = Path(__file__).parent / "migrations"
    alembic_ini = Path(__file__).parent / "alembic.ini"
    
    if not alembic_ini.exists():
        logger.warning(f"Alembic config not found at {alembic_ini}, skipping migrations")
        return
    
    if not migrations_dir.exists():
        logger.warning(f"Migrations directory not found at {migrations_dir}, skipping migrations")
        return
    
    try:
        # Create Alembic config
        config = AlembicConfig(str(alembic_ini))
        
        # Run pending migrations
        logger.info("Running pending database migrations...")
        command.upgrade(config, "head")
        logger.info("Database migrations completed successfully")
    except Exception as e:
        logger.error(f"Failed to run database migrations: {e}")
        raise
