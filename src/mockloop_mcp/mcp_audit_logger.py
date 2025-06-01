"""
MCP Audit Logger Module for regulatory compliance and model training data source tracking.

This module provides comprehensive logging of all MCP operations including:
- Prompt invocations with input parameters and generated outputs
- Resource access with metadata and content hashes
- Tool executions with parameters, results, and execution time
- Context operations (set, get, update) with state changes

Supports structured logging (JSON format) for easy parsing and compliance reporting.
Includes data lineage tracking for model training source attribution.
"""

import hashlib
import json
import logging
import time
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Optional, Union
import sqlite3
from contextlib import contextmanager
from dataclasses import dataclass, asdict
from enum import Enum


class MCPOperationType(Enum):
    """Types of MCP operations that can be logged."""
    PROMPT_INVOCATION = "prompt_invocation"
    RESOURCE_ACCESS = "resource_access"
    TOOL_EXECUTION = "tool_execution"
    CONTEXT_OPERATION = "context_operation"


class MCPLogLevel(Enum):
    """Log levels for MCP operations."""
    DEBUG = "debug"
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


@dataclass
class MCPAuditEntry:
    """Structured audit log entry for MCP operations."""

    # Core identification
    entry_id: str
    session_id: str
    user_id: str | None
    timestamp: str
    operation_type: str

    # Operation details
    operation_name: str
    operation_version: str | None
    input_parameters: dict[str, Any]
    output_data: dict[str, Any] | None

    # Performance metrics
    execution_time_ms: float | None
    memory_usage_mb: float | None
    cpu_usage_percent: float | None

    # Data lineage and compliance
    data_sources: list[str]
    content_hash: str | None
    data_classification: str | None
    retention_policy: str | None

    # Context and metadata
    context_state_before: dict[str, Any] | None
    context_state_after: dict[str, Any] | None
    error_details: str | None
    compliance_tags: list[str]

    # Regulatory tracking
    gdpr_applicable: bool = False
    ccpa_applicable: bool = False
    data_subject_id: str | None = None
    processing_purpose: str | None = None
    legal_basis: str | None = None


class MCPAuditLogger:
    """
    Comprehensive MCP audit logger for regulatory compliance and model training tracking.

    Features:
    - Structured JSON logging for all MCP operations
    - Data lineage tracking for model training source attribution
    - GDPR/CCPA compliance support
    - Performance metrics collection
    - Configurable retention policies
    - Secure content hashing
    """

    def __init__(
        self,
        db_path: str,
        log_file_path: str | None = None,
        session_id: str | None = None,
        user_id: str | None = None,
        enable_performance_tracking: bool = True,
        enable_content_hashing: bool = True,
        default_retention_days: int = 2555,  # 7 years for compliance
        log_level: MCPLogLevel = MCPLogLevel.INFO
    ):
        """
        Initialize the MCP audit logger.

        Args:
            db_path: Path to SQLite database for audit logs
            log_file_path: Optional path to JSON log file
            session_id: Current session identifier
            user_id: Current user identifier
            enable_performance_tracking: Whether to collect performance metrics
            enable_content_hashing: Whether to hash content for integrity
            default_retention_days: Default retention period in days
            log_level: Minimum log level to record
        """
        self.db_path = Path(db_path)
        self.log_file_path = Path(log_file_path) if log_file_path else None
        self.session_id = session_id or str(uuid.uuid4())
        self.user_id = user_id
        self.enable_performance_tracking = enable_performance_tracking
        self.enable_content_hashing = enable_content_hashing
        self.default_retention_days = default_retention_days
        self.log_level = log_level

        # Initialize database
        self._init_database()

        # Setup file logger if specified
        if self.log_file_path:
            self._setup_file_logger()

    def _init_database(self) -> None:
        """Initialize the audit log database schema."""
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Create audit logs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcp_audit_logs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT UNIQUE NOT NULL,
                    session_id TEXT NOT NULL,
                    user_id TEXT,
                    timestamp TEXT NOT NULL,
                    operation_type TEXT NOT NULL,
                    operation_name TEXT NOT NULL,
                    operation_version TEXT,
                    input_parameters TEXT,
                    output_data TEXT,
                    execution_time_ms REAL,
                    memory_usage_mb REAL,
                    cpu_usage_percent REAL,
                    data_sources TEXT,
                    content_hash TEXT,
                    data_classification TEXT,
                    retention_policy TEXT,
                    context_state_before TEXT,
                    context_state_after TEXT,
                    error_details TEXT,
                    compliance_tags TEXT,
                    gdpr_applicable BOOLEAN DEFAULT 0,
                    ccpa_applicable BOOLEAN DEFAULT 0,
                    data_subject_id TEXT,
                    processing_purpose TEXT,
                    legal_basis TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    expires_at TIMESTAMP
                )
            """)

            # Create indexes for performance
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mcp_audit_session
                ON mcp_audit_logs(session_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mcp_audit_timestamp
                ON mcp_audit_logs(timestamp)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mcp_audit_operation
                ON mcp_audit_logs(operation_type, operation_name)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mcp_audit_user
                ON mcp_audit_logs(user_id)
            """)
            cursor.execute("""
                CREATE INDEX IF NOT EXISTS idx_mcp_audit_expires
                ON mcp_audit_logs(expires_at)
            """)

            # Create data lineage table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcp_data_lineage (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL,
                    source_type TEXT NOT NULL,
                    source_identifier TEXT NOT NULL,
                    source_metadata TEXT,
                    transformation_applied TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entry_id) REFERENCES mcp_audit_logs (entry_id)
                )
            """)

            # Create compliance events table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS mcp_compliance_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    entry_id TEXT NOT NULL,
                    event_type TEXT NOT NULL,
                    regulation TEXT NOT NULL,
                    compliance_status TEXT NOT NULL,
                    details TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (entry_id) REFERENCES mcp_audit_logs (entry_id)
                )
            """)

            conn.commit()

    def _setup_file_logger(self) -> None:
        """Setup JSON file logger for audit entries."""
        self.file_logger = logging.getLogger(f"mcp_audit_{self.session_id}")
        self.file_logger.setLevel(logging.INFO)

        # Create file handler
        handler = logging.FileHandler(self.log_file_path)
        handler.setLevel(logging.INFO)

        # JSON formatter
        formatter = logging.Formatter('%(message)s')
        handler.setFormatter(formatter)

        self.file_logger.addHandler(handler)

    @contextmanager
    def _get_db_connection(self):
        """Get database connection with proper error handling."""
        conn = None
        try:
            conn = sqlite3.connect(str(self.db_path))
            conn.row_factory = sqlite3.Row
            yield conn
        except Exception:
            if conn:
                conn.rollback()
            raise
        finally:
            if conn:
                conn.close()

    def _calculate_content_hash(self, content: Any) -> str:
        """Calculate SHA-256 hash of content for integrity verification."""
        if not self.enable_content_hashing:
            return ""

        try:
            content_str = json.dumps(content, sort_keys=True, default=str)
            return hashlib.sha256(content_str.encode()).hexdigest()
        except Exception:
            return ""

    def _get_performance_metrics(self) -> dict[str, float | None]:
        """Get current performance metrics if enabled."""
        if not self.enable_performance_tracking:
            return {"memory_usage_mb": None, "cpu_usage_percent": None}

        try:
            import psutil
            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024
            cpu_percent = process.cpu_percent()
            return {"memory_usage_mb": memory_mb, "cpu_usage_percent": cpu_percent}
        except ImportError:
            return {"memory_usage_mb": None, "cpu_usage_percent": None}

    def log_prompt_invocation(
        self,
        prompt_name: str,
        input_parameters: dict[str, Any],
        generated_output: dict[str, Any] | None = None,
        execution_time_ms: float | None = None,
        data_sources: list[str] | None = None,
        compliance_tags: list[str] | None = None,
        **kwargs
    ) -> str:
        """
        Log MCP prompt invocation with input parameters and generated outputs.

        Args:
            prompt_name: Name of the prompt being invoked
            input_parameters: Input parameters passed to the prompt
            generated_output: Generated output from the prompt
            execution_time_ms: Execution time in milliseconds
            data_sources: List of data sources used
            compliance_tags: Compliance-related tags
            **kwargs: Additional metadata

        Returns:
            Entry ID of the logged operation
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate content hash
        content_hash = self._calculate_content_hash({
            "input": input_parameters,
            "output": generated_output
        })

        # Get performance metrics
        perf_metrics = self._get_performance_metrics()

        # Create audit entry
        audit_entry = MCPAuditEntry(
            entry_id=entry_id,
            session_id=self.session_id,
            user_id=self.user_id,
            timestamp=timestamp,
            operation_type=MCPOperationType.PROMPT_INVOCATION.value,
            operation_name=prompt_name,
            operation_version=kwargs.get("version"),
            input_parameters=input_parameters,
            output_data=generated_output,
            execution_time_ms=execution_time_ms,
            memory_usage_mb=perf_metrics["memory_usage_mb"],
            cpu_usage_percent=perf_metrics["cpu_usage_percent"],
            data_sources=data_sources or [],
            content_hash=content_hash,
            data_classification=kwargs.get("data_classification"),
            retention_policy=kwargs.get("retention_policy"),
            context_state_before=kwargs.get("context_before"),
            context_state_after=kwargs.get("context_after"),
            error_details=kwargs.get("error_details"),
            compliance_tags=compliance_tags or [],
            gdpr_applicable=kwargs.get("gdpr_applicable", False),
            ccpa_applicable=kwargs.get("ccpa_applicable", False),
            data_subject_id=kwargs.get("data_subject_id"),
            processing_purpose=kwargs.get("processing_purpose"),
            legal_basis=kwargs.get("legal_basis")
        )

        self._store_audit_entry(audit_entry)
        return entry_id

    def log_resource_access(
        self,
        resource_uri: str,
        access_type: str,
        metadata: dict[str, Any] | None = None,
        content_preview: str | None = None,
        data_sources: list[str] | None = None,
        compliance_tags: list[str] | None = None,
        **kwargs
    ) -> str:
        """
        Log MCP resource access with metadata and content hashes.

        Args:
            resource_uri: URI of the accessed resource
            access_type: Type of access (read, write, delete, etc.)
            metadata: Resource metadata
            content_preview: Preview of accessed content
            data_sources: List of data sources
            compliance_tags: Compliance-related tags
            **kwargs: Additional metadata

        Returns:
            Entry ID of the logged operation
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate content hash
        content_hash = self._calculate_content_hash({
            "uri": resource_uri,
            "metadata": metadata,
            "preview": content_preview
        })

        # Get performance metrics
        perf_metrics = self._get_performance_metrics()

        # Create audit entry
        audit_entry = MCPAuditEntry(
            entry_id=entry_id,
            session_id=self.session_id,
            user_id=self.user_id,
            timestamp=timestamp,
            operation_type=MCPOperationType.RESOURCE_ACCESS.value,
            operation_name=f"resource_access_{access_type}",
            operation_version=kwargs.get("version"),
            input_parameters={"uri": resource_uri, "access_type": access_type},
            output_data={"metadata": metadata, "content_preview": content_preview},
            execution_time_ms=kwargs.get("execution_time_ms"),
            memory_usage_mb=perf_metrics["memory_usage_mb"],
            cpu_usage_percent=perf_metrics["cpu_usage_percent"],
            data_sources=data_sources or [resource_uri],
            content_hash=content_hash,
            data_classification=kwargs.get("data_classification"),
            retention_policy=kwargs.get("retention_policy"),
            context_state_before=kwargs.get("context_before"),
            context_state_after=kwargs.get("context_after"),
            error_details=kwargs.get("error_details"),
            compliance_tags=compliance_tags or [],
            gdpr_applicable=kwargs.get("gdpr_applicable", False),
            ccpa_applicable=kwargs.get("ccpa_applicable", False),
            data_subject_id=kwargs.get("data_subject_id"),
            processing_purpose=kwargs.get("processing_purpose", "resource_access"),
            legal_basis=kwargs.get("legal_basis")
        )

        self._store_audit_entry(audit_entry)
        return entry_id

    def log_tool_execution(
        self,
        tool_name: str,
        input_parameters: dict[str, Any],
        execution_result: dict[str, Any] | None = None,
        execution_time_ms: float | None = None,
        data_sources: list[str] | None = None,
        compliance_tags: list[str] | None = None,
        **kwargs
    ) -> str:
        """
        Log MCP tool execution with parameters, results, and execution time.

        Args:
            tool_name: Name of the executed tool
            input_parameters: Input parameters passed to the tool
            execution_result: Result returned by the tool
            execution_time_ms: Execution time in milliseconds
            data_sources: List of data sources used
            compliance_tags: Compliance-related tags
            **kwargs: Additional metadata

        Returns:
            Entry ID of the logged operation
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate content hash
        content_hash = self._calculate_content_hash({
            "tool": tool_name,
            "input": input_parameters,
            "result": execution_result
        })

        # Get performance metrics
        perf_metrics = self._get_performance_metrics()

        # Create audit entry
        audit_entry = MCPAuditEntry(
            entry_id=entry_id,
            session_id=self.session_id,
            user_id=self.user_id,
            timestamp=timestamp,
            operation_type=MCPOperationType.TOOL_EXECUTION.value,
            operation_name=tool_name,
            operation_version=kwargs.get("version"),
            input_parameters=input_parameters,
            output_data=execution_result,
            execution_time_ms=execution_time_ms,
            memory_usage_mb=perf_metrics["memory_usage_mb"],
            cpu_usage_percent=perf_metrics["cpu_usage_percent"],
            data_sources=data_sources or [],
            content_hash=content_hash,
            data_classification=kwargs.get("data_classification"),
            retention_policy=kwargs.get("retention_policy"),
            context_state_before=kwargs.get("context_before"),
            context_state_after=kwargs.get("context_after"),
            error_details=kwargs.get("error_details"),
            compliance_tags=compliance_tags or [],
            gdpr_applicable=kwargs.get("gdpr_applicable", False),
            ccpa_applicable=kwargs.get("ccpa_applicable", False),
            data_subject_id=kwargs.get("data_subject_id"),
            processing_purpose=kwargs.get("processing_purpose", "tool_execution"),
            legal_basis=kwargs.get("legal_basis")
        )

        self._store_audit_entry(audit_entry)
        return entry_id

    def log_context_operation(
        self,
        operation_type: str,
        context_key: str,
        state_before: dict[str, Any] | None = None,
        state_after: dict[str, Any] | None = None,
        data_sources: list[str] | None = None,
        compliance_tags: list[str] | None = None,
        **kwargs
    ) -> str:
        """
        Log MCP context operations (set, get, update) with state changes.

        Args:
            operation_type: Type of context operation (set, get, update, delete)
            context_key: Key being operated on
            state_before: Context state before operation
            state_after: Context state after operation
            data_sources: List of data sources
            compliance_tags: Compliance-related tags
            **kwargs: Additional metadata

        Returns:
            Entry ID of the logged operation
        """
        entry_id = str(uuid.uuid4())
        timestamp = datetime.now(timezone.utc).isoformat()

        # Calculate content hash
        content_hash = self._calculate_content_hash({
            "operation": operation_type,
            "key": context_key,
            "before": state_before,
            "after": state_after
        })

        # Get performance metrics
        perf_metrics = self._get_performance_metrics()

        # Create audit entry
        audit_entry = MCPAuditEntry(
            entry_id=entry_id,
            session_id=self.session_id,
            user_id=self.user_id,
            timestamp=timestamp,
            operation_type=MCPOperationType.CONTEXT_OPERATION.value,
            operation_name=f"context_{operation_type}",
            operation_version=kwargs.get("version"),
            input_parameters={"key": context_key, "operation": operation_type},
            output_data={"state_change": state_after is not None},
            execution_time_ms=kwargs.get("execution_time_ms"),
            memory_usage_mb=perf_metrics["memory_usage_mb"],
            cpu_usage_percent=perf_metrics["cpu_usage_percent"],
            data_sources=data_sources or [],
            content_hash=content_hash,
            data_classification=kwargs.get("data_classification"),
            retention_policy=kwargs.get("retention_policy"),
            context_state_before=state_before,
            context_state_after=state_after,
            error_details=kwargs.get("error_details"),
            compliance_tags=compliance_tags or [],
            gdpr_applicable=kwargs.get("gdpr_applicable", False),
            ccpa_applicable=kwargs.get("ccpa_applicable", False),
            data_subject_id=kwargs.get("data_subject_id"),
            processing_purpose=kwargs.get("processing_purpose", "context_management"),
            legal_basis=kwargs.get("legal_basis")
        )

        self._store_audit_entry(audit_entry)
        return entry_id

    def _store_audit_entry(self, audit_entry: MCPAuditEntry) -> None:
        """Store audit entry in database and optionally in file."""
        # Calculate expiration date
        from datetime import timedelta
        expires_at = datetime.now(timezone.utc) + timedelta(days=self.default_retention_days)

        # Store in database
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            cursor.execute("""
                INSERT INTO mcp_audit_logs (
                    entry_id, session_id, user_id, timestamp, operation_type,
                    operation_name, operation_version, input_parameters, output_data,
                    execution_time_ms, memory_usage_mb, cpu_usage_percent,
                    data_sources, content_hash, data_classification, retention_policy,
                    context_state_before, context_state_after, error_details,
                    compliance_tags, gdpr_applicable, ccpa_applicable,
                    data_subject_id, processing_purpose, legal_basis, expires_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                audit_entry.entry_id,
                audit_entry.session_id,
                audit_entry.user_id,
                audit_entry.timestamp,
                audit_entry.operation_type,
                audit_entry.operation_name,
                audit_entry.operation_version,
                json.dumps(audit_entry.input_parameters),
                json.dumps(audit_entry.output_data) if audit_entry.output_data else None,
                audit_entry.execution_time_ms,
                audit_entry.memory_usage_mb,
                audit_entry.cpu_usage_percent,
                json.dumps(audit_entry.data_sources),
                audit_entry.content_hash,
                audit_entry.data_classification,
                audit_entry.retention_policy,
                json.dumps(audit_entry.context_state_before) if audit_entry.context_state_before else None,
                json.dumps(audit_entry.context_state_after) if audit_entry.context_state_after else None,
                audit_entry.error_details,
                json.dumps(audit_entry.compliance_tags),
                audit_entry.gdpr_applicable,
                audit_entry.ccpa_applicable,
                audit_entry.data_subject_id,
                audit_entry.processing_purpose,
                audit_entry.legal_basis,
                expires_at.isoformat()
            ))

            # Store data lineage
            for source in audit_entry.data_sources:
                cursor.execute("""
                    INSERT INTO mcp_data_lineage (
                        entry_id, source_type, source_identifier, source_metadata
                    ) VALUES (?, ?, ?, ?)
                """, (
                    audit_entry.entry_id,
                    "data_source",
                    source,
                    json.dumps({"timestamp": audit_entry.timestamp})
                ))

            conn.commit()

        # Store in file if configured
        if hasattr(self, 'file_logger'):
            log_entry = asdict(audit_entry)
            self.file_logger.info(json.dumps(log_entry, default=str))

    def query_audit_logs(
        self,
        start_time: str | None = None,
        end_time: str | None = None,
        operation_type: str | None = None,
        user_id: str | None = None,
        session_id: str | None = None,
        limit: int = 1000,
        offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Query audit logs with filtering options.

        Args:
            start_time: Start time filter (ISO format)
            end_time: End time filter (ISO format)
            operation_type: Filter by operation type
            user_id: Filter by user ID
            session_id: Filter by session ID
            limit: Maximum number of results
            offset: Number of results to skip

        Returns:
            List of audit log entries
        """
        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            query = "SELECT * FROM mcp_audit_logs WHERE 1=1"
            params = []

            if start_time:
                query += " AND timestamp >= ?"
                params.append(start_time)

            if end_time:
                query += " AND timestamp <= ?"
                params.append(end_time)

            if operation_type:
                query += " AND operation_type = ?"
                params.append(operation_type)

            if user_id:
                query += " AND user_id = ?"
                params.append(user_id)

            if session_id:
                query += " AND session_id = ?"
                params.append(session_id)

            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])

            cursor.execute(query, params)
            rows = cursor.fetchall()

            return [dict(row) for row in rows]

    def cleanup_expired_logs(self) -> int:
        """
        Clean up expired audit logs based on retention policies.

        Returns:
            Number of logs deleted
        """
        current_time = datetime.now(timezone.utc).isoformat()

        with self._get_db_connection() as conn:
            cursor = conn.cursor()

            # Delete expired logs
            cursor.execute("""
                DELETE FROM mcp_audit_logs
                WHERE expires_at < ?
            """, (current_time,))

            deleted_count = cursor.rowcount
            conn.commit()

            return deleted_count


def create_audit_logger(
    db_path: str,
    session_id: str | None = None,
    user_id: str | None = None,
    **kwargs
) -> MCPAuditLogger:
    """
    Factory function to create an MCP audit logger instance.

    Args:
        db_path: Path to SQLite database for audit logs
        session_id: Current session identifier
        user_id: Current user identifier
        **kwargs: Additional configuration options

    Returns:
        Configured MCPAuditLogger instance
    """
    return MCPAuditLogger(
        db_path=db_path,
        session_id=session_id,
        user_id=user_id,
        **kwargs
    )
