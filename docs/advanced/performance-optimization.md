# Performance Optimization

This document provides comprehensive guidance on optimizing MockLoop MCP performance across different deployment scenarios, from development environments to high-scale production systems.

## Overview

MockLoop MCP performance optimization involves multiple layers:

- **Application Layer**: Code optimization, async processing, caching
- **Database Layer**: Query optimization, indexing, connection pooling
- **Infrastructure Layer**: Resource allocation, load balancing, scaling
- **Network Layer**: Connection management, compression, CDN usage
- **Monitoring Layer**: Performance metrics, profiling, alerting

## Performance Metrics

### Key Performance Indicators

```python
class PerformanceMetrics:
    """Core performance metrics for MockLoop MCP."""
    
    def __init__(self):
        self.request_metrics = RequestMetrics()
        self.database_metrics = DatabaseMetrics()
        self.system_metrics = SystemMetrics()
        
    @dataclass
    class RequestMetrics:
        requests_per_second: float = 0.0
        avg_response_time_ms: float = 0.0
        p95_response_time_ms: float = 0.0
        p99_response_time_ms: float = 0.0
        error_rate_percent: float = 0.0
        concurrent_requests: int = 0
        
    @dataclass
    class DatabaseMetrics:
        queries_per_second: float = 0.0
        avg_query_time_ms: float = 0.0
        connection_pool_usage: float = 0.0
        cache_hit_rate: float = 0.0
        
    @dataclass
    class SystemMetrics:
        cpu_usage_percent: float = 0.0
        memory_usage_percent: float = 0.0
        disk_io_rate: float = 0.0
        network_io_rate: float = 0.0

class PerformanceCollector:
    """Collects and aggregates performance metrics."""
    
    def __init__(self, config: MetricsConfig):
        self.config = config
        self.metrics = PerformanceMetrics()
        self.collectors = [
            RequestMetricsCollector(),
            DatabaseMetricsCollector(),
            SystemMetricsCollector()
        ]
        
    async def collect_metrics(self) -> PerformanceMetrics:
        """Collect current performance metrics."""
        
        # Collect from all sources
        for collector in self.collectors:
            await collector.collect(self.metrics)
            
        return self.metrics
    
    async def start_monitoring(self, interval: int = 30):
        """Start continuous performance monitoring."""
        while True:
            metrics = await self.collect_metrics()
            await self.store_metrics(metrics)
            await self.check_thresholds(metrics)
            await asyncio.sleep(interval)
```

### Performance Benchmarking

```python
class PerformanceBenchmark:
    """Benchmarks MockLoop MCP performance."""
    
    def __init__(self, config: BenchmarkConfig):
        self.config = config
        self.results = []
        
    async def run_load_test(self, scenario: LoadTestScenario) -> BenchmarkResult:
        """Run load test scenario."""
        
        # Setup test environment
        await self.setup_test_environment(scenario)
        
        # Generate load
        tasks = []
        for i in range(scenario.concurrent_users):
            task = asyncio.create_task(
                self.simulate_user_load(scenario.user_pattern)
            )
            tasks.append(task)
        
        # Collect metrics during test
        metrics_task = asyncio.create_task(
            self.collect_test_metrics(scenario.duration)
        )
        
        # Wait for completion
        await asyncio.gather(*tasks)
        metrics = await metrics_task
        
        # Analyze results
        result = self.analyze_results(metrics)
        self.results.append(result)
        
        return result
    
    async def simulate_user_load(self, pattern: UserPattern) -> None:
        """Simulate user load pattern."""
        
        async with httpx.AsyncClient() as client:
            for request in pattern.requests:
                start_time = time.time()
                
                try:
                    response = await client.request(
                        method=request.method,
                        url=request.url,
                        headers=request.headers,
                        json=request.body
                    )
                    
                    response_time = (time.time() - start_time) * 1000
                    
                    # Record metrics
                    await self.record_request_metric(
                        response_time, response.status_code
                    )
                    
                except Exception as e:
                    # Record error
                    await self.record_error_metric(str(e))
                
                # Wait between requests
                if pattern.think_time > 0:
                    await asyncio.sleep(pattern.think_time)
```

## Application Layer Optimization

### Asynchronous Processing

```python
class AsyncOptimizations:
    """Asynchronous processing optimizations."""
    
    def __init__(self, config: AsyncConfig):
        self.config = config
        self.semaphore = asyncio.Semaphore(config.max_concurrent_requests)
        self.request_queue = asyncio.Queue(maxsize=config.queue_size)
        
    async def process_request_async(self, request: Request) -> Response:
        """Process request with async optimizations."""
        
        async with self.semaphore:
            # Process request
            response = await self.handle_request(request)
            
            # Async logging (fire and forget)
            asyncio.create_task(self.log_request_async(request, response))
            
            # Async webhook delivery
            asyncio.create_task(self.deliver_webhooks_async(request, response))
            
            # Async metrics collection
            asyncio.create_task(self.collect_metrics_async(request, response))
            
            return response
    
    async def batch_process_logs(self, batch_size: int = 100) -> None:
        """Process logs in batches for better performance."""
        
        batch = []
        
        while True:
            try:
                # Collect batch
                while len(batch) < batch_size:
                    log_entry = await asyncio.wait_for(
                        self.log_queue.get(), timeout=1.0
                    )
                    batch.append(log_entry)
                
                # Process batch
                await self.write_log_batch(batch)
                batch.clear()
                
            except asyncio.TimeoutError:
                # Process partial batch
                if batch:
                    await self.write_log_batch(batch)
                    batch.clear()
    
    async def write_log_batch(self, logs: List[LogEntry]) -> None:
        """Write log batch to database."""
        
        async with self.database.transaction():
            for log_entry in logs:
                await self.database.insert_log(log_entry)
```

### Response Caching

```python
class ResponseCache:
    """Multi-level response caching system."""
    
    def __init__(self, config: CacheConfig):
        self.config = config
        self.memory_cache = MemoryCache(config.memory)
        self.redis_cache = RedisCache(config.redis) if config.redis.enabled else None
        self.cache_stats = CacheStats()
        
    async def get_cached_response(self, cache_key: str) -> Optional[CachedResponse]:
        """Get response from cache hierarchy."""
        
        # Try memory cache first (fastest)
        response = await self.memory_cache.get(cache_key)
        if response:
            self.cache_stats.memory_hits += 1
            return response
        
        # Try Redis cache (distributed)
        if self.redis_cache:
            response = await self.redis_cache.get(cache_key)
            if response:
                self.cache_stats.redis_hits += 1
                # Populate memory cache
                await self.memory_cache.set(cache_key, response)
                return response
        
        self.cache_stats.misses += 1
        return None
    
    async def cache_response(self, cache_key: str, response: Response, ttl: int) -> None:
        """Cache response in all levels."""
        
        cached_response = CachedResponse(
            status_code=response.status_code,
            headers=dict(response.headers),
            body=response.body,
            timestamp=time.time(),
            ttl=ttl
        )
        
        # Cache in memory
        await self.memory_cache.set(cache_key, cached_response, ttl)
        
        # Cache in Redis
        if self.redis_cache:
            await self.redis_cache.set(cache_key, cached_response, ttl)
    
    def generate_cache_key(self, request: Request) -> str:
        """Generate cache key for request."""
        
        # Include relevant request components
        key_components = [
            request.method,
            request.url.path,
            str(sorted(request.query_params.items())),
            request.headers.get("accept", ""),
            request.headers.get("content-type", "")
        ]
        
        # Hash for consistent key length
        key_string = "|".join(key_components)
        return hashlib.sha256(key_string.encode()).hexdigest()[:32]

class CacheMiddleware:
    """Middleware for response caching."""
    
    def __init__(self, cache: ResponseCache):
        self.cache = cache
        
    async def __call__(self, request: Request, call_next):
        # Check if request is cacheable
        if not self.is_cacheable(request):
            return await call_next(request)
        
        # Generate cache key
        cache_key = self.cache.generate_cache_key(request)
        
        # Try to get cached response
        cached_response = await self.cache.get_cached_response(cache_key)
        if cached_response and not cached_response.is_expired():
            return cached_response.to_response()
        
        # Process request
        response = await call_next(request)
        
        # Cache response if appropriate
        if self.should_cache_response(response):
            ttl = self.get_cache_ttl(request, response)
            await self.cache.cache_response(cache_key, response, ttl)
        
        return response
    
    def is_cacheable(self, request: Request) -> bool:
        """Check if request is cacheable."""
        return (
            request.method == "GET" and
            "no-cache" not in request.headers.get("cache-control", "") and
            not request.url.path.startswith("/admin/")
        )
```

### Connection Pooling

```python
class OptimizedConnectionManager:
    """Optimized connection management."""
    
    def __init__(self, config: ConnectionConfig):
        self.config = config
        self.db_pool = self.create_database_pool()
        self.http_pool = self.create_http_pool()
        
    def create_database_pool(self) -> DatabasePool:
        """Create optimized database connection pool."""
        
        return DatabasePool(
            database_url=self.config.database_url,
            min_connections=self.config.db_min_connections,
            max_connections=self.config.db_max_connections,
            max_idle_time=self.config.db_max_idle_time,
            max_lifetime=self.config.db_max_lifetime,
            retry_attempts=self.config.db_retry_attempts,
            retry_delay=self.config.db_retry_delay,
            health_check_interval=self.config.db_health_check_interval
        )
    
    def create_http_pool(self) -> HTTPPool:
        """Create optimized HTTP connection pool."""
        
        return HTTPPool(
            max_connections=self.config.http_max_connections,
            max_keepalive_connections=self.config.http_max_keepalive,
            keepalive_expiry=self.config.http_keepalive_expiry,
            timeout=self.config.http_timeout,
            retries=self.config.http_retries
        )
    
    async def execute_query_optimized(self, query: str, params: tuple = None) -> QueryResult:
        """Execute database query with optimizations."""
        
        async with self.db_pool.acquire() as connection:
            # Use prepared statements for better performance
            if query not in connection.prepared_statements:
                await connection.prepare_statement(query)
            
            # Execute with parameters
            return await connection.execute_prepared(query, params)
    
    async def make_http_request_optimized(self, request: HTTPRequest) -> HTTPResponse:
        """Make HTTP request with optimizations."""
        
        async with self.http_pool.acquire() as session:
            # Reuse connections when possible
            return await session.request(
                method=request.method,
                url=request.url,
                headers=request.headers,
                data=request.data,
                timeout=request.timeout
            )
```

## Database Layer Optimization

### Query Optimization

```python
class QueryOptimizer:
    """Database query optimization utilities."""
    
    def __init__(self, database: DatabaseConnection):
        self.database = database
        self.query_cache = {}
        self.execution_stats = {}
        
    async def optimize_log_queries(self) -> None:
        """Optimize common log queries."""
        
        # Create composite indexes for common query patterns
        await self.database.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_composite 
            ON request_logs(server_id, timestamp, method)
        """)
        
        await self.database.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_path_method 
            ON request_logs(path, method) 
            WHERE response_status < 400
        """)
        
        await self.database.execute("""
            CREATE INDEX IF NOT EXISTS idx_request_logs_status_time 
            ON request_logs(response_status, timestamp) 
            WHERE timestamp > datetime('now', '-7 days')
        """)
    
    async def analyze_query_performance(self, query: str) -> QueryAnalysis:
        """Analyze query performance."""
        
        # Get query execution plan
        explain_query = f"EXPLAIN QUERY PLAN {query}"
        plan = await self.database.execute(explain_query)
        
        # Measure execution time
        start_time = time.time()
        await self.database.execute(query)
        execution_time = (time.time() - start_time) * 1000
        
        # Analyze plan
        analysis = QueryAnalysis(
            query=query,
            execution_time_ms=execution_time,
            execution_plan=plan,
            recommendations=self.generate_recommendations(plan)
        )
        
        return analysis
    
    def generate_recommendations(self, execution_plan: List[dict]) -> List[str]:
        """Generate optimization recommendations."""
        
        recommendations = []
        
        for step in execution_plan:
            detail = step.get('detail', '').lower()
            
            if 'scan' in detail and 'index' not in detail:
                recommendations.append(
                    f"Consider adding index for table scan: {step.get('table', 'unknown')}"
                )
            
            if 'temp b-tree' in detail:
                recommendations.append(
                    "Query uses temporary B-tree, consider adding appropriate index"
                )
            
            if 'nested loop' in detail:
                recommendations.append(
                    "Nested loop join detected, verify join conditions have indexes"
                )
        
        return recommendations

class DatabaseOptimizations:
    """Database-specific optimizations."""
    
    def __init__(self, database: DatabaseConnection):
        self.database = database
        
    async def optimize_sqlite(self) -> None:
        """SQLite-specific optimizations."""
        
        # Enable WAL mode for better concurrency
        await self.database.execute("PRAGMA journal_mode = WAL")
        
        # Optimize synchronous mode
        await self.database.execute("PRAGMA synchronous = NORMAL")
        
        # Increase cache size
        await self.database.execute("PRAGMA cache_size = 10000")
        
        # Use memory for temporary storage
        await self.database.execute("PRAGMA temp_store = MEMORY")
        
        # Optimize page size
        await self.database.execute("PRAGMA page_size = 4096")
        
        # Enable query planner optimizations
        await self.database.execute("PRAGMA optimize")
    
    async def optimize_postgresql(self) -> None:
        """PostgreSQL-specific optimizations."""
        
        # Update table statistics
        await self.database.execute("ANALYZE")
        
        # Configure connection settings
        await self.database.execute("SET work_mem = '256MB'")
        await self.database.execute("SET maintenance_work_mem = '512MB'")
        await self.database.execute("SET effective_cache_size = '2GB'")
        
        # Enable parallel query execution
        await self.database.execute("SET max_parallel_workers_per_gather = 4")
        
    async def optimize_mysql(self) -> None:
        """MySQL-specific optimizations."""
        
        # Optimize buffer pool
        await self.database.execute("SET GLOBAL innodb_buffer_pool_size = 1073741824")
        
        # Configure query cache
        await self.database.execute("SET GLOBAL query_cache_size = 268435456")
        await self.database.execute("SET GLOBAL query_cache_type = ON")
        
        # Optimize connection handling
        await self.database.execute("SET GLOBAL max_connections = 200")
```

### Data Partitioning

```python
class DataPartitioning:
    """Database partitioning for performance."""
    
    def __init__(self, database: DatabaseConnection):
        self.database = database
        
    async def setup_log_partitioning(self) -> None:
        """Setup partitioning for request logs."""
        
        if self.database.type == "postgresql":
            await self.setup_postgresql_partitioning()
        elif self.database.type == "mysql":
            await self.setup_mysql_partitioning()
    
    async def setup_postgresql_partitioning(self) -> None:
        """Setup PostgreSQL table partitioning."""
        
        # Create partitioned table
        await self.database.execute("""
            CREATE TABLE request_logs_partitioned (
                LIKE request_logs INCLUDING ALL
            ) PARTITION BY RANGE (timestamp)
        """)
        
        # Create monthly partitions
        current_date = datetime.now()
        for i in range(12):  # Create 12 months of partitions
            partition_date = current_date + relativedelta(months=i)
            partition_name = f"request_logs_{partition_date.strftime('%Y_%m')}"
            start_date = partition_date.replace(day=1)
            end_date = start_date + relativedelta(months=1)
            
            await self.database.execute(f"""
                CREATE TABLE {partition_name} PARTITION OF request_logs_partitioned
                FOR VALUES FROM ('{start_date}') TO ('{end_date}')
            """)
    
    async def setup_mysql_partitioning(self) -> None:
        """Setup MySQL table partitioning."""
        
        # Create partitioned table
        await self.database.execute("""
            CREATE TABLE request_logs_partitioned (
                LIKE request_logs
            )
            PARTITION BY RANGE (YEAR(timestamp) * 100 + MONTH(timestamp)) (
                PARTITION p202401 VALUES LESS THAN (202402),
                PARTITION p202402 VALUES LESS THAN (202403),
                PARTITION p202403 VALUES LESS THAN (202404),
                PARTITION p202404 VALUES LESS THAN (202405),
                PARTITION p202405 VALUES LESS THAN (202406),
                PARTITION p202406 VALUES LESS THAN (202407),
                PARTITION p202407 VALUES LESS THAN (202408),
                PARTITION p202408 VALUES LESS THAN (202409),
                PARTITION p202409 VALUES LESS THAN (202410),
                PARTITION p202410 VALUES LESS THAN (202411),
                PARTITION p202411 VALUES LESS THAN (202412),
                PARTITION p202412 VALUES LESS THAN (202501)
            )
        """)
    
    async def maintain_partitions(self) -> None:
        """Maintain partition tables."""
        
        # Drop old partitions
        await self.drop_old_partitions()
        
        # Create future partitions
        await self.create_future_partitions()
    
    async def drop_old_partitions(self) -> None:
        """Drop partitions older than retention period."""
        
        retention_months = 6
        cutoff_date = datetime.now() - relativedelta(months=retention_months)
        
        if self.database.type == "postgresql":
            # Get old partitions
            result = await self.database.execute("""
                SELECT schemaname, tablename 
                FROM pg_tables 
                WHERE tablename LIKE 'request_logs_%' 
                AND tablename < 'request_logs_' || to_char(%s, 'YYYY_MM')
            """, (cutoff_date,))
            
            # Drop old partitions
            for schema, table in result:
                await self.database.execute(f"DROP TABLE {schema}.{table}")
```

## Infrastructure Optimization

### Load Balancing

```python
class LoadBalancer:
    """Load balancer for MockLoop MCP instances."""
    
    def __init__(self, config: LoadBalancerConfig):
        self.config = config
        self.servers = []
        self.health_checker = HealthChecker()
        self.algorithms = {
            "round_robin": RoundRobinAlgorithm(),
            "least_connections": LeastConnectionsAlgorithm(),
            "weighted_round_robin": WeightedRoundRobinAlgorithm(),
            "ip_hash": IPHashAlgorithm()
        }
        
    async def add_server(self, server: ServerInfo) -> None:
        """Add server to load balancer."""
        
        # Verify server health
        if await self.health_checker.check_health(server):
            self.servers.append(server)
            await self.update_server_weights()
    
    async def remove_server(self, server_id: str) -> None:
        """Remove server from load balancer."""
        
        self.servers = [s for s in self.servers if s.id != server_id]
        await self.update_server_weights()
    
    async def select_server(self, request: Request) -> Optional[ServerInfo]:
        """Select server for request."""
        
        # Filter healthy servers
        healthy_servers = [
            s for s in self.servers 
            if s.status == "healthy"
        ]
        
        if not healthy_servers:
            return None
        
        # Use configured algorithm
        algorithm = self.algorithms[self.config.algorithm]
        return await algorithm.select_server(healthy_servers, request)
    
    async def update_server_weights(self) -> None:
        """Update server weights based on performance."""
        
        for server in self.servers:
            metrics = await self.get_server_metrics(server)
            
            # Calculate weight based on performance
            cpu_factor = 1.0 - (metrics.cpu_usage / 100.0)
            memory_factor = 1.0 - (metrics.memory_usage / 100.0)
            response_time_factor = max(0.1, 1.0 - (metrics.avg_response_time / 1000.0))
            
            server.weight = cpu_factor * memory_factor * response_time_factor

class RoundRobinAlgorithm:
    """Round-robin load balancing algorithm."""
    
    def __init__(self):
        self.current_index = 0
    
    async def select_server(self, servers: List[ServerInfo], request: Request) -> ServerInfo:
        """Select server using round-robin."""
        
        server = servers[self.current_index % len(servers)]
        self.current_index += 1
        return server

class LeastConnectionsAlgorithm:
    """Least connections load balancing algorithm."""
    
    async def select_server(self, servers: List[ServerInfo], request: Request) -> ServerInfo:
        """Select server with least connections."""
        
        return min(servers, key=lambda s: s.active_connections)

class WeightedRoundRobinAlgorithm:
    """Weighted round-robin load balancing algorithm."""
    
    def __init__(self):
        self.current_weights = {}
    
    async def select_server(self, servers: List[ServerInfo], request: Request) -> ServerInfo:
        """Select server using weighted round-robin."""
        
        # Initialize weights
        for server in servers:
            if server.id not in self.current_weights:
                self.current_weights[server.id] = 0
        
        # Find server with highest current weight
        best_server = None
        best_weight = -1
        
        total_weight = sum(s.weight for s in servers)
        
        for server in servers:
            self.current_weights[server.id] += server.weight
            
            if self.current_weights[server.id] > best_weight:
                best_weight = self.current_weights[server.id]
                best_server = server
        
        # Reduce weight
        if best_server:
            self.current_weights[best_server.id] -= total_weight
        
        return best_server
```

### Auto-Scaling

```python
class AutoScaler:
    """Automatic scaling for MockLoop MCP."""
    
    def __init__(self, config: AutoScalingConfig):
        self.config = config
        self.metrics_collector = MetricsCollector()
        self.scaling_decisions = []
        
    async def monitor_and_scale(self) -> None:
        """Monitor metrics and make scaling decisions."""
        
        while True:
            # Collect current metrics
            metrics = await self.metrics_collector.collect_metrics()
            
            # Make scaling decision
            decision = await self.make_scaling_decision(metrics)
            
            if decision.action != "none":
                await self.execute_scaling_decision(decision)
                self.scaling_decisions.append(decision)
            
            await asyncio.sleep(self.config.check_interval)
    
    async def make_scaling_decision(self, metrics: PerformanceMetrics) -> ScalingDecision:
        """Make scaling decision based on metrics."""
        
        current_instances = await self.get_current_instance_count()
        
        # Check scale-up conditions
        if self.should_scale_up(metrics, current_instances):
            target_instances = min(
                current_instances + self.config.scale_up_step,
                self.config.max_instances
            )
            return ScalingDecision("scale_up", target_instances, metrics)
        
        # Check scale-down conditions
        if self.should_scale_down(metrics, current_instances):
            target_instances = max(
                current_instances - self.config.scale_down_step,
                self.config.min_instances
            )
            return ScalingDecision("scale_down", target_instances, metrics)
        
        return ScalingDecision("none", current_instances, metrics)
    
    def should_scale_up(self, metrics: PerformanceMetrics, current_instances: int) -> bool:
        """Check if should scale up."""
        
        return (
            metrics.system_metrics.cpu_usage_percent > self.config.cpu_scale_up_threshold or
            metrics.system_metrics.memory_usage_percent > self.config.memory_scale_up_threshold or
            metrics.request_metrics.avg_response_time_ms > self.config.response_time_scale_up_threshold
        ) and current_instances < self.config.max_instances
    
    def should_scale_down(self, metrics: PerformanceMetrics, current_instances: int) -> bool:
        """Check if should scale down."""
        
        return (
            metrics.system_metrics.cpu_usage_percent < self.config.cpu_scale_down_threshold and
            metrics.system_metrics.memory_usage_percent < self.config.memory_scale_down_threshold and
            metrics.request_metrics.avg_response_time_ms < self.config.response_time_scale_down_threshold
        ) and current_instances > self.config.min_instances
    
    async def execute_scaling_decision(self, decision: ScalingDecision) -> None:
        """Execute scaling decision."""
        
        if decision.action == "scale_up":
            await self.scale_up(decision.target_instances)
        elif decision.action == "scale_down":
            await self.scale_down(decision.target_instances)
    
    async def scale_up(self, target_instances: int) -> None:
        """Scale up to target instance count."""
        
        current_instances = await self.get_current_instance_count()
        instances_to_add = target_instances - current_instances
        
        for i in range(instances_to_add):
            await self.launch_instance()
    
    async def scale_down(self, target_instances: int) -> None:
        """Scale down to target instance count."""
        
        current_instances = await self.get_current_instance_count()
        instances_to_remove = current_instances - target_instances
        
        # Remove least loaded instances
        instances = await self.get_instance_list()
        instances_by_load = sorted(instances, key=lambda i: i.load)
        
        for i in range(instances_to_remove):
            await self.terminate_instance(instances_by_load[i])
```

## Memory Optimization

### Memory Management

```python
class MemoryOptimizer:
    """Memory optimization utilities."""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.memory_pools = {}
        self.gc_scheduler = GarbageCollectionScheduler()
        
    async def optimize_memory_usage(self) -> None:
        """Optimize memory usage."""
        
        # Configure garbage collection
        await self.configure_garbage_collection()
        
        # Setup memory pools
        await self.setup_memory_pools()
        
        # Monitor memory usage
        await self.start_memory_monitoring()
    
    async def configure_garbage_collection(self) -> None:
        """Configure garbage collection for optimal performance."""
        
        import gc
        
        # Tune garbage collection thresholds
        gc.set_threshold(
            self.config.gc_threshold_0,
            self.config.gc_threshold_1,
            self.config.gc_threshold_2
        )
        
        # Schedule periodic garbage collection
        await self.gc_scheduler.schedule_periodic_gc(
            interval=self.config.gc_interval
        )
    
    async def setup_memory_pools(self) -> None:
        """Setup memory pools for frequently allocated objects."""
        
        # Pool for request objects
        self.memory_pools["requests"] = ObjectPool(
            factory=lambda: Request(),
            max_size=self.config.request_pool_size
        )
        
        # Pool for response objects
        self.memory_pools["responses"] = ObjectPool(
            factory=lambda: Response(),
            max_size=self.config.response_pool_size
        )
        
        # Pool for log entries
        self.memory_pools["log_entries"] = ObjectPool(
            factory=lambda: LogEntry(),
            max_size=self.config.log_entry_pool_size
        )
    
    async def get_pooled_object(self, object_type: str):
        """Get object from memory pool."""
        
        pool = self.memory_pools.get(object_type)
        if pool:
            return await pool.acquire()
        
        # Fallback to regular allocation
        if object_type == "requests":
            return Request()
        elif object_type == "responses":
            return Response()
        elif object_type == "log_entries":
            return LogEntry()
    
    async def return_pooled_object(self, object_type: str, obj) ->