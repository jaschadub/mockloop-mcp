# Database Migrations

This document provides comprehensive guidance on managing database schema changes in MockLoop MCP through the migration system. The migration system ensures safe, versioned, and reversible database schema updates.

## Overview

MockLoop MCP uses a robust migration system to manage database schema changes across different environments. The system supports:

- **Versioned Migrations**: Each migration has a unique version number
- **Reversible Changes**: All migrations can be rolled back
- **Environment Safety**: Migrations work across SQLite, PostgreSQL, and MySQL
- **Dependency Management**: Migrations can depend on other migrations
- **Validation**: Schema validation before and after migrations
- **Backup Integration**: Automatic backups before major changes

## Migration System Architecture

### Migration Structure

```python
from abc import ABC, abstractmethod
from typing import Optional, List
import logging

class Migration(ABC):
    """Base class for all database migrations."""
    
    version: int
    description: str
    dependencies: List[int] = []
    
    @abstractmethod
    def up(self, connection: DatabaseConnection) -> None:
        """Apply the migration."""
        pass
    
    @abstractmethod
    def down(self, connection: DatabaseConnection) -> None:
        """Reverse the migration."""
        pass
    
    def validate(self, connection: DatabaseConnection) -> bool:
        """Validate migration can be applied."""
        return True
    
    def backup_required(self) -> bool:
        """Whether this migration requires a backup."""
        return False

class MigrationManager:
    """Manages database migrations."""
    
    def __init__(self, database_url: str, migrations_path: str):
        self.database = DatabaseConnection(database_url)
        self.migrations_path = migrations_path
        self.logger = logging.getLogger(__name__)
        
    async def get_current_version(self) -> int:
        """Get current database schema version."""
        
    async def get_pending_migrations(self) -> List[Migration]:
        """Get list of pending migrations."""
        
    async def apply_migration(self, migration: Migration) -> bool:
        """Apply a single migration."""
        
    async def rollback_migration(self, migration: Migration) -> bool:
        """Rollback a single migration."""
        
    async def migrate_to_version(self, target_version: int) -> bool:
        """Migrate to specific version."""
```

### Migration Discovery

```python
class MigrationDiscovery:
    """Discovers and loads migration files."""
    
    def __init__(self, migrations_path: str):
        self.migrations_path = Path(migrations_path)
        
    def discover_migrations(self) -> List[Migration]:
        """Discover all migration files."""
        migrations = []
        
        for file_path in self.migrations_path.glob("*.py"):
            if file_path.name.startswith("migration_"):
                migration = self.load_migration(file_path)
                if migration:
                    migrations.append(migration)
        
        return sorted(migrations, key=lambda m: m.version)
    
    def load_migration(self, file_path: Path) -> Optional[Migration]:
        """Load migration from file."""
        try:
            spec = importlib.util.spec_from_file_location("migration", file_path)
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find migration class
            for attr_name in dir(module):
                attr = getattr(module, attr_name)
                if (isinstance(attr, type) and 
                    issubclass(attr, Migration) and 
                    attr != Migration):
                    return attr()
                    
        except Exception as e:
            self.logger.error(f"Failed to load migration {file_path}: {e}")
            
        return None
```

## Creating Migrations

### Migration File Structure

Migration files follow a specific naming convention and structure:

```python
# migrations/migration_001_initial_schema.py
from mockloop_mcp.database.migration import Migration
from mockloop_mcp.database.connection import DatabaseConnection

class InitialSchema(Migration):
    version = 1
    description = "Create initial database schema"
    
    def up(self, connection: DatabaseConnection) -> None:
        """Create initial tables."""
        
        # Create request_logs table
        connection.execute("""
            CREATE TABLE request_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                method VARCHAR(10) NOT NULL,
                path TEXT NOT NULL,
                query_params TEXT,
                headers TEXT,
                request_body TEXT,
                response_status INTEGER NOT NULL,
                response_headers TEXT,
                response_body TEXT,
                response_time_ms INTEGER,
                server_id VARCHAR(255),
                client_ip VARCHAR(45),
                user_agent TEXT,
                request_id VARCHAR(255),
                scenario_name VARCHAR(255),
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        connection.execute("""
            CREATE INDEX idx_request_logs_timestamp ON request_logs(timestamp)
        """)
        
        connection.execute("""
            CREATE INDEX idx_request_logs_server_id ON request_logs(server_id)
        """)
        
        # Create mock_servers table
        connection.execute("""
            CREATE TABLE mock_servers (
                id VARCHAR(255) PRIMARY KEY,
                name VARCHAR(255) NOT NULL,
                spec_path TEXT NOT NULL,
                spec_content TEXT,
                output_directory TEXT NOT NULL,
                port INTEGER,
                status VARCHAR(50) NOT NULL DEFAULT 'stopped',
                pid INTEGER,
                config TEXT,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                started_at DATETIME,
                stopped_at DATETIME
            )
        """)
        
        # Create schema_version table
        connection.execute("""
            CREATE TABLE schema_version (
                version INTEGER PRIMARY KEY,
                description TEXT,
                applied_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Insert initial version
        connection.execute("""
            INSERT INTO schema_version (version, description) 
            VALUES (1, 'Initial schema')
        """)
    
    def down(self, connection: DatabaseConnection) -> None:
        """Drop all tables."""
        connection.execute("DROP TABLE IF EXISTS request_logs")
        connection.execute("DROP TABLE IF EXISTS mock_servers")
        connection.execute("DROP TABLE IF EXISTS schema_version")
```

### Adding New Tables

```python
# migrations/migration_002_add_scenarios.py
class AddScenariosTable(Migration):
    version = 2
    description = "Add scenarios table for mock response management"
    dependencies = [1]  # Depends on initial schema
    
    def up(self, connection: DatabaseConnection) -> None:
        """Add scenarios table."""
        
        connection.execute("""
            CREATE TABLE scenarios (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(255) NOT NULL,
                server_id VARCHAR(255) NOT NULL,
                description TEXT,
                config TEXT NOT NULL,
                is_active BOOLEAN NOT NULL DEFAULT FALSE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                created_by VARCHAR(255),
                
                FOREIGN KEY (server_id) REFERENCES mock_servers(id) ON DELETE CASCADE,
                UNIQUE(name, server_id)
            )
        """)
        
        # Add indexes
        connection.execute("""
            CREATE INDEX idx_scenarios_name ON scenarios(name)
        """)
        
        connection.execute("""
            CREATE INDEX idx_scenarios_server_id ON scenarios(server_id)
        """)
        
        connection.execute("""
            CREATE INDEX idx_scenarios_is_active ON scenarios(is_active)
        """)
        
        # Update schema version
        connection.execute("""
            INSERT INTO schema_version (version, description) 
            VALUES (2, 'Add scenarios table')
        """)
    
    def down(self, connection: DatabaseConnection) -> None:
        """Remove scenarios table."""
        connection.execute("DROP TABLE IF EXISTS scenarios")
        connection.execute("DELETE FROM schema_version WHERE version = 2")
```

### Modifying Existing Tables

```python
# migrations/migration_003_add_webhook_support.py
class AddWebhookSupport(Migration):
    version = 3
    description = "Add webhook tables and modify request_logs"
    dependencies = [2]
    
    def backup_required(self) -> bool:
        """This migration modifies existing data."""
        return True
    
    def up(self, connection: DatabaseConnection) -> None:
        """Add webhook support."""
        
        # Add webhook_url column to request_logs
        connection.execute("""
            ALTER TABLE request_logs 
            ADD COLUMN webhook_url TEXT
        """)
        
        # Create webhooks table
        connection.execute("""
            CREATE TABLE webhooks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                server_id VARCHAR(255) NOT NULL,
                name VARCHAR(255) NOT NULL,
                url TEXT NOT NULL,
                method VARCHAR(10) NOT NULL DEFAULT 'POST',
                headers TEXT,
                events TEXT NOT NULL,
                secret_key VARCHAR(255),
                is_active BOOLEAN NOT NULL DEFAULT TRUE,
                created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (server_id) REFERENCES mock_servers(id) ON DELETE CASCADE
            )
        """)
        
        # Create webhook_deliveries table
        connection.execute("""
            CREATE TABLE webhook_deliveries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                webhook_id INTEGER NOT NULL,
                event_type VARCHAR(255) NOT NULL,
                payload TEXT NOT NULL,
                response_status INTEGER,
                response_body TEXT,
                delivery_time_ms INTEGER,
                attempt_number INTEGER NOT NULL DEFAULT 1,
                success BOOLEAN NOT NULL DEFAULT FALSE,
                error_message TEXT,
                delivered_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                
                FOREIGN KEY (webhook_id) REFERENCES webhooks(id) ON DELETE CASCADE
            )
        """)
        
        # Add indexes
        connection.execute("""
            CREATE INDEX idx_webhooks_server_id ON webhooks(server_id)
        """)
        
        connection.execute("""
            CREATE INDEX idx_webhook_deliveries_webhook_id ON webhook_deliveries(webhook_id)
        """)
        
        # Update schema version
        connection.execute("""
            INSERT INTO schema_version (version, description) 
            VALUES (3, 'Add webhook support')
        """)
    
    def down(self, connection: DatabaseConnection) -> None:
        """Remove webhook support."""
        
        # Drop webhook tables
        connection.execute("DROP TABLE IF EXISTS webhook_deliveries")
        connection.execute("DROP TABLE IF EXISTS webhooks")
        
        # Remove webhook_url column (SQLite doesn't support DROP COLUMN)
        if connection.database_type == "sqlite":
            # Recreate table without webhook_url column
            connection.execute("""
                CREATE TABLE request_logs_new (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    method VARCHAR(10) NOT NULL,
                    path TEXT NOT NULL,
                    query_params TEXT,
                    headers TEXT,
                    request_body TEXT,
                    response_status INTEGER NOT NULL,
                    response_headers TEXT,
                    response_body TEXT,
                    response_time_ms INTEGER,
                    server_id VARCHAR(255),
                    client_ip VARCHAR(45),
                    user_agent TEXT,
                    request_id VARCHAR(255),
                    scenario_name VARCHAR(255),
                    created_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
                    updated_at DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            connection.execute("""
                INSERT INTO request_logs_new 
                SELECT id, timestamp, method, path, query_params, headers, 
                       request_body, response_status, response_headers, 
                       response_body, response_time_ms, server_id, client_ip, 
                       user_agent, request_id, scenario_name, created_at, updated_at
                FROM request_logs
            """)
            
            connection.execute("DROP TABLE request_logs")
            connection.execute("ALTER TABLE request_logs_new RENAME TO request_logs")
            
            # Recreate indexes
            connection.execute("CREATE INDEX idx_request_logs_timestamp ON request_logs(timestamp)")
            connection.execute("CREATE INDEX idx_request_logs_server_id ON request_logs(server_id)")
        else:
            # PostgreSQL/MySQL support DROP COLUMN
            connection.execute("ALTER TABLE request_logs DROP COLUMN webhook_url")
        
        connection.execute("DELETE FROM schema_version WHERE version = 3")
```

## Database-Specific Migrations

### SQLite Migrations

```python
class SQLiteMigration(Migration):
    """Base class for SQLite-specific migrations."""
    
    def recreate_table_without_column(self, connection: DatabaseConnection, 
                                    table_name: str, column_to_remove: str) -> None:
        """Helper to remove column from SQLite table."""
        
        # Get table schema
        result = connection.execute(f"PRAGMA table_info({table_name})")
        columns = [row for row in result if row[1] != column_to_remove]
        
        # Create new table
        column_defs = []
        for col in columns:
            col_def = f"{col[1]} {col[2]}"
            if col[3]:  # NOT NULL
                col_def += " NOT NULL"
            if col[4]:  # DEFAULT
                col_def += f" DEFAULT {col[4]}"
            if col[5]:  # PRIMARY KEY
                col_def += " PRIMARY KEY"
            column_defs.append(col_def)
        
        new_table_sql = f"""
            CREATE TABLE {table_name}_new (
                {', '.join(column_defs)}
            )
        """
        connection.execute(new_table_sql)
        
        # Copy data
        column_names = [col[1] for col in columns]
        connection.execute(f"""
            INSERT INTO {table_name}_new ({', '.join(column_names)})
            SELECT {', '.join(column_names)} FROM {table_name}
        """)
        
        # Replace table
        connection.execute(f"DROP TABLE {table_name}")
        connection.execute(f"ALTER TABLE {table_name}_new RENAME TO {table_name}")
```

### PostgreSQL Migrations

```python
class PostgreSQLMigration(Migration):
    """Base class for PostgreSQL-specific migrations."""
    
    def create_enum(self, connection: DatabaseConnection, enum_name: str, values: List[str]) -> None:
        """Create PostgreSQL enum type."""
        values_str = "', '".join(values)
        connection.execute(f"CREATE TYPE {enum_name} AS ENUM ('{values_str}')")
    
    def add_column_with_default(self, connection: DatabaseConnection, 
                               table_name: str, column_def: str, default_value: str) -> None:
        """Add column with default value efficiently."""
        connection.execute(f"ALTER TABLE {table_name} ADD COLUMN {column_def}")
        connection.execute(f"UPDATE {table_name} SET {column_def.split()[0]} = {default_value}")
```

### MySQL Migrations

```python
class MySQLMigration(Migration):
    """Base class for MySQL-specific migrations."""
    
    def modify_column(self, connection: DatabaseConnection, 
                     table_name: str, column_name: str, new_definition: str) -> None:
        """Modify column definition in MySQL."""
        connection.execute(f"ALTER TABLE {table_name} MODIFY COLUMN {column_name} {new_definition}")
    
    def add_index_if_not_exists(self, connection: DatabaseConnection, 
                               table_name: str, index_name: str, columns: str) -> None:
        """Add index only if it doesn't exist."""
        connection.execute(f"""
            CREATE INDEX {index_name} ON {table_name} ({columns})
        """)
```

## Migration Management

### Running Migrations

```bash
# Apply all pending migrations
mockloop db migrate

# Migrate to specific version
mockloop db migrate --version 5

# Check migration status
mockloop db status

# Show pending migrations
mockloop db pending

# Validate migrations without applying
mockloop db validate
```

### Migration CLI Commands

```python
class MigrationCLI:
    """Command-line interface for migrations."""
    
    def __init__(self, migration_manager: MigrationManager):
        self.manager = migration_manager
    
    async def migrate(self, target_version: Optional[int] = None) -> None:
        """Apply migrations."""
        if target_version:
            await self.manager.migrate_to_version(target_version)
        else:
            await self.manager.migrate_to_latest()
    
    async def rollback(self, target_version: int) -> None:
        """Rollback to specific version."""
        current_version = await self.manager.get_current_version()
        
        if target_version >= current_version:
            print(f"Target version {target_version} is not lower than current version {current_version}")
            return
        
        # Confirm rollback
        if not self.confirm_rollback(current_version, target_version):
            return
        
        await self.manager.rollback_to_version(target_version)
    
    async def status(self) -> None:
        """Show migration status."""
        current_version = await self.manager.get_current_version()
        pending_migrations = await self.manager.get_pending_migrations()
        
        print(f"Current database version: {current_version}")
        print(f"Pending migrations: {len(pending_migrations)}")
        
        for migration in pending_migrations:
            print(f"  - Version {migration.version}: {migration.description}")
    
    def confirm_rollback(self, current_version: int, target_version: int) -> bool:
        """Confirm rollback operation."""
        print(f"WARNING: This will rollback from version {current_version} to {target_version}")
        print("This operation may result in data loss.")
        response = input("Are you sure you want to continue? (yes/no): ")
        return response.lower() == "yes"
```

### Automated Migration Testing

```python
class MigrationTester:
    """Tests migration up and down operations."""
    
    def __init__(self, database_url: str):
        self.database_url = database_url
        self.test_database_url = self.create_test_database_url()
    
    async def test_migration(self, migration: Migration) -> TestResult:
        """Test a migration's up and down operations."""
        
        # Create test database
        test_db = DatabaseConnection(self.test_database_url)
        
        try:
            # Apply migration
            migration.up(test_db)
            
            # Validate schema
            up_validation = await self.validate_schema_after_up(test_db, migration)
            
            # Test rollback
            migration.down(test_db)
            
            # Validate rollback
            down_validation = await self.validate_schema_after_down(test_db, migration)
            
            return TestResult(
                migration_version=migration.version,
                up_success=up_validation.success,
                down_success=down_validation.success,
                errors=up_validation.errors + down_validation.errors
            )
            
        finally:
            # Cleanup test database
            await self.cleanup_test_database(test_db)
    
    async def test_all_migrations(self) -> List[TestResult]:
        """Test all migrations."""
        discovery = MigrationDiscovery("./migrations")
        migrations = discovery.discover_migrations()
        
        results = []
        for migration in migrations:
            result = await self.test_migration(migration)
            results.append(result)
            
        return results
```

## Data Migrations

### Migrating Existing Data

```python
class DataMigration(Migration):
    """Base class for data migrations."""
    
    def migrate_data_in_batches(self, connection: DatabaseConnection, 
                               query: str, batch_size: int = 1000) -> None:
        """Migrate data in batches to avoid memory issues."""
        
        offset = 0
        while True:
            batch_query = f"{query} LIMIT {batch_size} OFFSET {offset}"
            rows = connection.execute(batch_query).fetchall()
            
            if not rows:
                break
                
            self.process_batch(connection, rows)
            offset += batch_size
    
    def process_batch(self, connection: DatabaseConnection, rows: List[tuple]) -> None:
        """Process a batch of rows."""
        raise NotImplementedError

# Example data migration
class MigrateRequestLogFormat(DataMigration):
    version = 4
    description = "Migrate request log format from JSON to structured columns"
    dependencies = [3]
    
    def backup_required(self) -> bool:
        return True
    
    def up(self, connection: DatabaseConnection) -> None:
        """Migrate request log data format."""
        
        # Add new columns
        connection.execute("ALTER TABLE request_logs ADD COLUMN parsed_headers TEXT")
        connection.execute("ALTER TABLE request_logs ADD COLUMN parsed_query_params TEXT")
        
        # Migrate existing data
        self.migrate_data_in_batches(
            connection,
            "SELECT id, headers, query_params FROM request_logs WHERE parsed_headers IS NULL"
        )
        
        # Update schema version
        connection.execute("""
            INSERT INTO schema_version (version, description) 
            VALUES (4, 'Migrate request log format')
        """)
    
    def process_batch(self, connection: DatabaseConnection, rows: List[tuple]) -> None:
        """Process batch of request logs."""
        for row_id, headers_json, query_params_json in rows:
            try:
                # Parse and restructure data
                parsed_headers = self.parse_headers(headers_json)
                parsed_query_params = self.parse_query_params(query_params_json)
                
                # Update row
                connection.execute("""
                    UPDATE request_logs 
                    SET parsed_headers = ?, parsed_query_params = ?
                    WHERE id = ?
                """, (parsed_headers, parsed_query_params, row_id))
                
            except Exception as e:
                self.logger.error(f"Failed to migrate row {row_id}: {e}")
    
    def parse_headers(self, headers_json: str) -> str:
        """Parse headers JSON into structured format."""
        # Implementation for parsing headers
        pass
    
    def parse_query_params(self, query_params_json: str) -> str:
        """Parse query parameters JSON into structured format."""
        # Implementation for parsing query parameters
        pass
    
    def down(self, connection: DatabaseConnection) -> None:
        """Rollback data migration."""
        connection.execute("ALTER TABLE request_logs DROP COLUMN parsed_headers")
        connection.execute("ALTER TABLE request_logs DROP COLUMN parsed_query_params")
        connection.execute("DELETE FROM schema_version WHERE version = 4")
```

## Migration Best Practices

### 1. Migration Safety

```python
class SafeMigration(Migration):
    """Template for safe migrations."""
    
    def validate(self, connection: DatabaseConnection) -> bool:
        """Validate migration can be safely applied."""
        
        # Check database constraints
        if not self.check_constraints(connection):
            return False
        
        # Check data integrity
        if not self.check_data_integrity(connection):
            return False
        
        # Check disk space
        if not self.check_disk_space(connection):
            return False
        
        return True
    
    def check_constraints(self, connection: DatabaseConnection) -> bool:
        """Check database constraints."""
        # Verify foreign key constraints
        # Check unique constraints
        # Validate data types
        return True
    
    def check_data_integrity(self, connection: DatabaseConnection) -> bool:
        """Check data integrity before migration."""
        # Verify data consistency
        # Check for orphaned records
        # Validate data formats
        return True
    
    def check_disk_space(self, connection: DatabaseConnection) -> bool:
        """Check available disk space."""
        # Estimate migration space requirements
        # Check available disk space
        return True
```

### 2. Backup Integration

```python
class BackupManager:
    """Manages database backups for migrations."""
    
    def __init__(self, database_url: str, backup_path: str):
        self.database_url = database_url
        self.backup_path = Path(backup_path)
        
    async def create_backup(self, migration_version: int) -> str:
        """Create database backup before migration."""
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"backup_v{migration_version}_{timestamp}.sql"
        backup_file = self.backup_path / backup_filename
        
        # Create backup based on database type
        if self.database_url.startswith("sqlite"):
            await self.backup_sqlite(backup_file)
        elif self.database_url.startswith("postgresql"):
            await self.backup_postgresql(backup_file)
        elif self.database_url.startswith("mysql"):
            await self.backup_mysql(backup_file)
        
        return str(backup_file)
    
    async def restore_backup(self, backup_file: str) -> bool:
        """Restore database from backup."""
        # Implementation for restoring backup
        pass
```

### 3. Migration Monitoring

```python
class MigrationMonitor:
    """Monitors migration progress and performance."""
    
    def __init__(self):
        self.start_time = None
        self.metrics = {}
    
    def start_migration(self, migration: Migration) -> None:
        """Start monitoring migration."""
        self.start_time = time.time()
        self.metrics = {
            "version": migration.version,
            "description": migration.description,
            "start_time": self.start_time
        }
    
    def end_migration(self, success: bool) -> None:
        """End monitoring migration."""
        end_time = time.time()
        self.metrics.update({
            "end_time": end_time,
            "duration": end_time - self.start_time,
            "success": success
        })
        
        # Log metrics
        self.log_metrics()
    
    def log_metrics(self) -> None:
        """Log migration metrics."""
        logger.info(f"Migration {self.metrics['version']} completed", extra=self.metrics)
```

## Troubleshooting Migrations

### Common Issues

#### 1. Failed Migration Recovery

```python
class MigrationRecovery:
    """Handles migration failure recovery."""
    
    async def recover_from_failed_migration(self, migration_version: int) -> bool:
        """Recover from failed migration."""
        
        # Check migration state
        state = await self.check_migration_state(migration_version)
        
        if state == "partial":
            # Attempt to complete migration
            return await self.complete_partial_migration(migration_version)
        elif state == "failed":
            # Rollback failed migration
            return await self.rollback_failed_migration(migration_version)
        
        return False
    
    async def check_migration_state(self, migration_version: int) -> str:
        """Check the state of a migration."""
        # Check schema_version table
        # Verify expected schema changes
        # Check for partial data migration
        pass
```

#### 2. Schema Validation

```python
class SchemaValidator:
    """Validates database schema after migrations."""
    
    def __init__(self, connection: DatabaseConnection):
        self.connection = connection
    
    async def validate_schema(self, expected_version: int) -> ValidationResult:
        """Validate database schema matches expected version."""
        
        # Check schema version
        current_version = await self.get_schema_version()
        if current_version != expected_version:
            return ValidationResult(False, f"Version mismatch: {current_version} != {expected_version}")
        
        # Validate table structure
        table_validation = await self.validate_tables()
        if not table_validation.success:
            return table_validation
        
        # Validate indexes
        index_validation = await self.validate_indexes()
        if not index_validation.success:
            return index_validation
        
        # Validate constraints
        constraint_validation = await self.validate_constraints()
        if not constraint_validation.success:
            return constraint_validation
        
        return ValidationResult(True, "Schema validation passed")
```

### Migration Debugging

```bash
# Enable debug logging
export MOCKLOOP_LOG_LEVEL=debug

# Run migration with verbose output
mockloop db migrate --verbose

# Check migration history
mockloop db history

# Validate current schema
mockloop db validate-schema

# Show migration details
mockloop db show-migration --version 3
```

## See Also

- **[Database Schema](../api/database-schema.md)**: Complete database schema reference
- **[Configuration Options](../api/configuration.md)**: Database configuration options
- **[Architecture](architecture.md)**: System architecture overview
- **[Troubleshooting](troubleshooting.md)**: General troubleshooting guide