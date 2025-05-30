# Security Considerations

This document provides comprehensive security guidance for MockLoop MCP deployments, covering authentication, authorization, data protection, network security, and compliance considerations.

## Overview

Security in MockLoop MCP involves multiple layers:

- **Authentication**: Verifying user and system identities
- **Authorization**: Controlling access to resources and operations
- **Data Protection**: Securing data at rest and in transit
- **Network Security**: Protecting network communications
- **Audit and Compliance**: Logging and monitoring for security compliance
- **Vulnerability Management**: Identifying and mitigating security risks

## Authentication

### Multi-Factor Authentication

```python
class MultiFactorAuthentication:
    """Multi-factor authentication implementation."""
    
    def __init__(self, config: MFAConfig):
        self.config = config
        self.totp_generator = TOTPGenerator()
        self.sms_provider = SMSProvider(config.sms)
        self.email_provider = EmailProvider(config.email)
        
    async def authenticate_user(self, credentials: UserCredentials) -> AuthResult:
        """Authenticate user with multiple factors."""
        
        # First factor: username/password
        primary_auth = await self.verify_primary_credentials(credentials)
        if not primary_auth.success:
            return AuthResult(False, "Invalid credentials")
        
        user = primary_auth.user
        
        # Check if MFA is required
        if not user.mfa_enabled:
            return AuthResult(True, "Authentication successful", user)
        
        # Second factor: TOTP, SMS, or email
        mfa_result = await self.verify_second_factor(user, credentials.mfa_token)
        if not mfa_result.success:
            return AuthResult(False, "Invalid MFA token")
        
        return AuthResult(True, "MFA authentication successful", user)
    
    async def verify_primary_credentials(self, credentials: UserCredentials) -> AuthResult:
        """Verify username and password."""
        
        user = await self.get_user_by_username(credentials.username)
        if not user:
            return AuthResult(False, "User not found")
        
        # Verify password hash
        if not self.verify_password_hash(credentials.password, user.password_hash):
            # Log failed attempt
            await self.log_failed_login_attempt(user.id, credentials.client_ip)
            return AuthResult(False, "Invalid password")
        
        # Check account status
        if not user.is_active:
            return AuthResult(False, "Account disabled")
        
        # Check for account lockout
        if await self.is_account_locked(user.id):
            return AuthResult(False, "Account locked due to failed attempts")
        
        return AuthResult(True, "Primary authentication successful", user)
    
    async def verify_second_factor(self, user: User, mfa_token: str) -> AuthResult:
        """Verify second factor authentication."""
        
        if user.mfa_method == "totp":
            return await self.verify_totp_token(user, mfa_token)
        elif user.mfa_method == "sms":
            return await self.verify_sms_token(user, mfa_token)
        elif user.mfa_method == "email":
            return await self.verify_email_token(user, mfa_token)
        
        return AuthResult(False, "Unknown MFA method")
    
    async def verify_totp_token(self, user: User, token: str) -> AuthResult:
        """Verify TOTP token."""
        
        # Get user's TOTP secret
        totp_secret = await self.get_user_totp_secret(user.id)
        
        # Verify token with time window tolerance
        if self.totp_generator.verify_token(totp_secret, token, window=1):
            return AuthResult(True, "TOTP verification successful")
        
        return AuthResult(False, "Invalid TOTP token")
```

### API Key Management

```python
class APIKeyManager:
    """Manages API keys for authentication."""
    
    def __init__(self, config: APIKeyConfig):
        self.config = config
        self.key_store = APIKeyStore(config.storage)
        self.rate_limiter = RateLimiter(config.rate_limits)
        
    async def generate_api_key(self, user_id: str, permissions: List[str], 
                              expires_at: Optional[datetime] = None) -> APIKey:
        """Generate new API key for user."""
        
        # Generate secure random key
        key_value = self.generate_secure_key()
        
        # Create API key record
        api_key = APIKey(
            id=generate_uuid(),
            user_id=user_id,
            key_hash=self.hash_key(key_value),
            permissions=permissions,
            created_at=datetime.utcnow(),
            expires_at=expires_at,
            last_used_at=None,
            is_active=True
        )
        
        # Store in database
        await self.key_store.store_api_key(api_key)
        
        # Return key with plaintext value (only time it's available)
        api_key.key_value = key_value
        return api_key
    
    async def validate_api_key(self, key_value: str, required_permission: str = None) -> ValidationResult:
        """Validate API key and check permissions."""
        
        # Hash the provided key
        key_hash = self.hash_key(key_value)
        
        # Look up API key
        api_key = await self.key_store.get_api_key_by_hash(key_hash)
        if not api_key:
            return ValidationResult(False, "Invalid API key")
        
        # Check if key is active
        if not api_key.is_active:
            return ValidationResult(False, "API key is disabled")
        
        # Check expiration
        if api_key.expires_at and api_key.expires_at < datetime.utcnow():
            return ValidationResult(False, "API key has expired")
        
        # Check rate limits
        if not await self.rate_limiter.check_rate_limit(api_key.id):
            return ValidationResult(False, "Rate limit exceeded")
        
        # Check permissions
        if required_permission and required_permission not in api_key.permissions:
            return ValidationResult(False, f"Missing permission: {required_permission}")
        
        # Update last used timestamp
        await self.key_store.update_last_used(api_key.id)
        
        return ValidationResult(True, "API key valid", api_key)
    
    def generate_secure_key(self) -> str:
        """Generate cryptographically secure API key."""
        
        # Generate 32 bytes of random data
        random_bytes = secrets.token_bytes(32)
        
        # Encode as base64 with URL-safe characters
        key_value = base64.urlsafe_b64encode(random_bytes).decode('ascii')
        
        # Add prefix for identification
        return f"mlcp_{key_value}"
    
    def hash_key(self, key_value: str) -> str:
        """Hash API key for secure storage."""
        
        # Use SHA-256 with salt
        salt = self.config.key_salt.encode('utf-8')
        key_bytes = key_value.encode('utf-8')
        
        hash_obj = hashlib.sha256(salt + key_bytes)
        return hash_obj.hexdigest()

class APIKeyMiddleware:
    """Middleware for API key authentication."""
    
    def __init__(self, api_key_manager: APIKeyManager):
        self.api_key_manager = api_key_manager
        
    async def __call__(self, request: Request, call_next):
        # Skip authentication for public endpoints
        if self.is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Extract API key from header
        api_key = request.headers.get("X-API-Key")
        if not api_key:
            return Response(
                status_code=401,
                content={"error": "API key required"}
            )
        
        # Validate API key
        validation_result = await self.api_key_manager.validate_api_key(api_key)
        if not validation_result.success:
            return Response(
                status_code=401,
                content={"error": validation_result.message}
            )
        
        # Add user context to request
        request.state.user = validation_result.api_key.user_id
        request.state.permissions = validation_result.api_key.permissions
        
        return await call_next(request)
```

### JWT Authentication

```python
class JWTAuthenticator:
    """JWT-based authentication system."""
    
    def __init__(self, config: JWTConfig):
        self.config = config
        self.secret_key = config.secret_key
        self.algorithm = config.algorithm
        self.expiration_time = config.expiration_hours * 3600
        
    async def generate_token(self, user: User) -> str:
        """Generate JWT token for user."""
        
        now = datetime.utcnow()
        payload = {
            "sub": user.id,
            "username": user.username,
            "email": user.email,
            "roles": user.roles,
            "permissions": user.permissions,
            "iat": now,
            "exp": now + timedelta(seconds=self.expiration_time),
            "iss": self.config.issuer,
            "aud": self.config.audience
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        # Store token for revocation checking
        await self.store_active_token(user.id, token, payload["exp"])
        
        return token
    
    async def validate_token(self, token: str) -> TokenValidationResult:
        """Validate JWT token."""
        
        try:
            # Decode and verify token
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                audience=self.config.audience,
                issuer=self.config.issuer
            )
            
            # Check if token is revoked
            if await self.is_token_revoked(token):
                return TokenValidationResult(False, "Token has been revoked")
            
            # Get user information
            user_id = payload["sub"]
            user = await self.get_user_by_id(user_id)
            
            if not user or not user.is_active:
                return TokenValidationResult(False, "User not found or inactive")
            
            return TokenValidationResult(True, "Token valid", user, payload)
            
        except jwt.ExpiredSignatureError:
            return TokenValidationResult(False, "Token has expired")
        except jwt.InvalidTokenError as e:
            return TokenValidationResult(False, f"Invalid token: {str(e)}")
    
    async def revoke_token(self, token: str) -> bool:
        """Revoke JWT token."""
        
        try:
            # Decode token to get expiration
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}  # Don't verify expiration for revocation
            )
            
            # Add to revocation list
            await self.add_to_revocation_list(token, payload["exp"])
            return True
            
        except jwt.InvalidTokenError:
            return False
    
    async def refresh_token(self, token: str) -> Optional[str]:
        """Refresh JWT token if valid and not expired."""
        
        validation_result = await self.validate_token(token)
        if not validation_result.success:
            return None
        
        # Generate new token
        new_token = await self.generate_token(validation_result.user)
        
        # Revoke old token
        await self.revoke_token(token)
        
        return new_token
```

## Authorization

### Role-Based Access Control (RBAC)

```python
class RoleBasedAccessControl:
    """Role-based access control system."""
    
    def __init__(self, config: RBACConfig):
        self.config = config
        self.role_store = RoleStore(config.storage)
        self.permission_cache = PermissionCache(config.cache)
        
    async def check_permission(self, user_id: str, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource."""
        
        # Get user permissions from cache or database
        permissions = await self.get_user_permissions(user_id)
        
        # Check direct permissions
        if self.has_direct_permission(permissions, resource, action):
            return True
        
        # Check role-based permissions
        user_roles = await self.get_user_roles(user_id)
        for role in user_roles:
            role_permissions = await self.get_role_permissions(role.id)
            if self.has_direct_permission(role_permissions, resource, action):
                return True
        
        return False
    
    def has_direct_permission(self, permissions: List[Permission], resource: str, action: str) -> bool:
        """Check if permissions list contains required permission."""
        
        for permission in permissions:
            if self.permission_matches(permission, resource, action):
                return True
        
        return False
    
    def permission_matches(self, permission: Permission, resource: str, action: str) -> bool:
        """Check if permission matches resource and action."""
        
        # Exact match
        if permission.resource == resource and permission.action == action:
            return True
        
        # Wildcard matching
        if permission.resource == "*" or permission.action == "*":
            return True
        
        # Pattern matching
        if self.matches_pattern(permission.resource, resource) and \
           self.matches_pattern(permission.action, action):
            return True
        
        return False
    
    def matches_pattern(self, pattern: str, value: str) -> bool:
        """Check if value matches pattern (supports wildcards)."""
        
        import fnmatch
        return fnmatch.fnmatch(value, pattern)
    
    async def assign_role_to_user(self, user_id: str, role_id: str) -> bool:
        """Assign role to user."""
        
        # Verify role exists
        role = await self.role_store.get_role(role_id)
        if not role:
            return False
        
        # Assign role
        await self.role_store.assign_user_role(user_id, role_id)
        
        # Clear permission cache for user
        await self.permission_cache.clear_user_permissions(user_id)
        
        return True
    
    async def create_role(self, role_data: RoleData) -> Role:
        """Create new role with permissions."""
        
        role = Role(
            id=generate_uuid(),
            name=role_data.name,
            description=role_data.description,
            permissions=role_data.permissions,
            created_at=datetime.utcnow()
        )
        
        await self.role_store.store_role(role)
        return role

# Predefined roles and permissions
class DefaultRoles:
    """Default roles and permissions for MockLoop MCP."""
    
    ADMIN = Role(
        name="admin",
        description="Full system administrator",
        permissions=[
            Permission("*", "*"),  # All permissions
        ]
    )
    
    DEVELOPER = Role(
        name="developer", 
        description="Developer with server management access",
        permissions=[
            Permission("servers", "create"),
            Permission("servers", "read"),
            Permission("servers", "update"),
            Permission("servers", "delete"),
            Permission("scenarios", "*"),
            Permission("logs", "read"),
            Permission("webhooks", "*")
        ]
    )
    
    VIEWER = Role(
        name="viewer",
        description="Read-only access to servers and logs",
        permissions=[
            Permission("servers", "read"),
            Permission("scenarios", "read"),
            Permission("logs", "read")
        ]
    )
    
    API_USER = Role(
        name="api_user",
        description="API access for external integrations",
        permissions=[
            Permission("servers", "read"),
            Permission("scenarios", "read"),
            Permission("scenarios", "switch"),
            Permission("mock_data", "update")
        ]
    )

class AuthorizationMiddleware:
    """Middleware for authorization checking."""
    
    def __init__(self, rbac: RoleBasedAccessControl):
        self.rbac = rbac
        
    async def __call__(self, request: Request, call_next):
        # Skip authorization for public endpoints
        if self.is_public_endpoint(request.url.path):
            return await call_next(request)
        
        # Get user from request (set by authentication middleware)
        user_id = getattr(request.state, "user", None)
        if not user_id:
            return Response(
                status_code=401,
                content={"error": "Authentication required"}
            )
        
        # Determine required permission
        resource, action = self.extract_permission_requirements(request)
        
        # Check authorization
        if not await self.rbac.check_permission(user_id, resource, action):
            return Response(
                status_code=403,
                content={"error": f"Insufficient permissions for {action} on {resource}"}
            )
        
        return await call_next(request)
    
    def extract_permission_requirements(self, request: Request) -> Tuple[str, str]:
        """Extract resource and action from request."""
        
        path = request.url.path
        method = request.method
        
        # Map HTTP methods to actions
        method_action_map = {
            "GET": "read",
            "POST": "create", 
            "PUT": "update",
            "PATCH": "update",
            "DELETE": "delete"
        }
        
        action = method_action_map.get(method, "unknown")
        
        # Extract resource from path
        if path.startswith("/admin/api/v1/servers"):
            resource = "servers"
        elif path.startswith("/admin/api/v1/scenarios"):
            resource = "scenarios"
        elif path.startswith("/admin/api/v1/logs"):
            resource = "logs"
        elif path.startswith("/admin/api/v1/webhooks"):
            resource = "webhooks"
        else:
            resource = "unknown"
        
        return resource, action
```

## Data Protection

### Encryption at Rest

```python
class DataEncryption:
    """Data encryption for sensitive information."""
    
    def __init__(self, config: EncryptionConfig):
        self.config = config
        self.cipher_suite = self.create_cipher_suite()
        self.key_manager = KeyManager(config.key_management)
        
    def create_cipher_suite(self) -> Fernet:
        """Create encryption cipher suite."""
        
        # Get encryption key from key manager
        encryption_key = self.key_manager.get_encryption_key()
        
        # Create Fernet cipher
        return Fernet(encryption_key)
    
    def encrypt_sensitive_data(self, data: str) -> str:
        """Encrypt sensitive data."""
        
        if not data:
            return data
        
        # Convert to bytes
        data_bytes = data.encode('utf-8')
        
        # Encrypt
        encrypted_bytes = self.cipher_suite.encrypt(data_bytes)
        
        # Return base64 encoded string
        return base64.b64encode(encrypted_bytes).decode('ascii')
    
    def decrypt_sensitive_data(self, encrypted_data: str) -> str:
        """Decrypt sensitive data."""
        
        if not encrypted_data:
            return encrypted_data
        
        try:
            # Decode from base64
            encrypted_bytes = base64.b64decode(encrypted_data.encode('ascii'))
            
            # Decrypt
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            
            # Return string
            return decrypted_bytes.decode('utf-8')
            
        except Exception as e:
            raise DecryptionError(f"Failed to decrypt data: {str(e)}")

class SecureStorage:
    """Secure storage for sensitive configuration data."""
    
    def __init__(self, encryption: DataEncryption):
        self.encryption = encryption
        self.sensitive_fields = {
            "password", "secret", "key", "token", "credential"
        }
    
    async def store_configuration(self, config: dict) -> dict:
        """Store configuration with sensitive data encrypted."""
        
        encrypted_config = {}
        
        for key, value in config.items():
            if self.is_sensitive_field(key) and isinstance(value, str):
                # Encrypt sensitive fields
                encrypted_config[key] = self.encryption.encrypt_sensitive_data(value)
                encrypted_config[f"{key}_encrypted"] = True
            else:
                encrypted_config[key] = value
        
        return encrypted_config
    
    async def load_configuration(self, encrypted_config: dict) -> dict:
        """Load configuration with sensitive data decrypted."""
        
        decrypted_config = {}
        
        for key, value in encrypted_config.items():
            if key.endswith("_encrypted"):
                continue  # Skip encryption flags
            
            if encrypted_config.get(f"{key}_encrypted", False):
                # Decrypt sensitive fields
                decrypted_config[key] = self.encryption.decrypt_sensitive_data(value)
            else:
                decrypted_config[key] = value
        
        return decrypted_config
    
    def is_sensitive_field(self, field_name: str) -> bool:
        """Check if field contains sensitive data."""
        
        field_lower = field_name.lower()
        return any(sensitive in field_lower for sensitive in self.sensitive_fields)
```

### Data Masking and Anonymization

```python
class DataMasking:
    """Data masking for logs and exports."""
    
    def __init__(self, config: MaskingConfig):
        self.config = config
        self.masking_rules = self.load_masking_rules()
        
    def load_masking_rules(self) -> List[MaskingRule]:
        """Load data masking rules."""
        
        return [
            MaskingRule(
                field_pattern=r".*password.*",
                mask_type="replace",
                replacement="[MASKED]"
            ),
            MaskingRule(
                field_pattern=r".*email.*",
                mask_type="partial",
                visible_chars=3,
                mask_char="*"
            ),
            MaskingRule(
                field_pattern=r".*phone.*",
                mask_type="format",
                format_pattern="XXX-XXX-{last4}"
            ),
            MaskingRule(
                field_pattern=r".*credit_card.*",
                mask_type="format", 
                format_pattern="****-****-****-{last4}"
            )
        ]
    
    def mask_data(self, data: dict) -> dict:
        """Apply masking rules to data."""
        
        masked_data = {}
        
        for key, value in data.items():
            if isinstance(value, dict):
                # Recursively mask nested objects
                masked_data[key] = self.mask_data(value)
            elif isinstance(value, list):
                # Mask list items
                masked_data[key] = [
                    self.mask_data(item) if isinstance(item, dict) else self.mask_value(key, item)
                    for item in value
                ]
            else:
                # Apply masking rules
                masked_data[key] = self.mask_value(key, value)
        
        return masked_data
    
    def mask_value(self, field_name: str, value: Any) -> Any:
        """Apply masking to a single value."""
        
        if not isinstance(value, str):
            return value
        
        for rule in self.masking_rules:
            if re.match(rule.field_pattern, field_name, re.IGNORECASE):
                return self.apply_masking_rule(rule, value)
        
        return value
    
    def apply_masking_rule(self, rule: MaskingRule, value: str) -> str:
        """Apply specific masking rule."""
        
        if rule.mask_type == "replace":
            return rule.replacement
        
        elif rule.mask_type == "partial":
            if len(value) <= rule.visible_chars:
                return rule.mask_char * len(value)
            
            visible_part = value[:rule.visible_chars]
            masked_part = rule.mask_char * (len(value) - rule.visible_chars)
            return visible_part + masked_part
        
        elif rule.mask_type == "format":
            if "{last4}" in rule.format_pattern:
                last4 = value[-4:] if len(value) >= 4 else value
                return rule.format_pattern.replace("{last4}", last4)
        
        return value

class LogSanitizer:
    """Sanitizes logs to remove sensitive information."""
    
    def __init__(self, data_masking: DataMasking):
        self.data_masking = data_masking
        self.sensitive_patterns = [
            (r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b', '[EMAIL]'),  # Email
            (r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b', '[CARD]'),  # Credit card
            (r'\b\d{3}-\d{2}-\d{4}\b', '[SSN]'),  # SSN
            (r'\b(?:\d{1,3}\.){3}\d{1,3}\b', '[IP]'),  # IP address
        ]
    
    def sanitize_log_entry(self, log_entry: LogEntry) -> LogEntry:
        """Sanitize log entry."""
        
        sanitized_entry = log_entry.copy()
        
        # Sanitize request headers
        if sanitized_entry.headers:
            sanitized_entry.headers = self.data_masking.mask_data(
                json.loads(sanitized_entry.headers)
            )
        
        # Sanitize request body
        if sanitized_entry.request_body:
            sanitized_entry.request_body = self.sanitize_text(sanitized_entry.request_body)
        
        # Sanitize response body
        if sanitized_entry.response_body:
            sanitized_entry.response_body = self.sanitize_text(sanitized_entry.response_body)
        
        return sanitized_entry
    
    def sanitize_text(self, text: str) -> str:
        """Sanitize text content."""
        
        sanitized = text
        
        for pattern, replacement in self.sensitive_patterns:
            sanitized = re.sub(pattern, replacement, sanitized)
        
        return sanitized
```

## Network Security

### TLS/SSL Configuration

```python
class TLSConfiguration:
    """TLS/SSL configuration for secure communications."""
    
    def __init__(self, config: TLSConfig):
        self.config = config
        self.ssl_context = self.create_ssl_context()
        
    def create_ssl_context(self) -> ssl.SSLContext:
        """Create SSL context with secure configuration."""
        
        # Create SSL context
        context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        
        # Load certificate and private key
        context.load_cert_chain(
            certfile=self.config.cert_file,
            keyfile=self.config.key_file
        )
        
        # Configure security options
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.maximum_version = ssl.TLSVersion.TLSv1_3
        
        # Disable weak ciphers
        context.set_ciphers('ECDHE+AESGCM:ECDHE+CHACHA20:DHE+AESGCM:DHE+CHACHA20:!aNULL:!MD5:!DSS')
        
        # Configure certificate verification
        if self.config.verify_mode == "required":
            context.verify_mode = ssl.CERT_REQUIRED
        elif self.config.verify_mode == "optional":
            context.verify_mode = ssl.CERT_OPTIONAL
        else:
            context.verify_mode = ssl.CERT_NONE
        
        # Load CA certificates if provided
        if self.config.ca_file:
            context.load_verify_locations(cafile=self.config.ca_file)
        
        return context
    
    def create_secure_server(self, app, host: str, port: int) -> None:
        """Create secure HTTPS server."""
        
        import uvicorn
        
        uvicorn.run(
            app,
            host=host,
            port=port,
            ssl_keyfile=self.config.key_file,
            ssl_certfile=self.config.cert_file,
            ssl_ca_certs=self.config.ca_file,
            ssl_version=ssl.PROTOCOL_TLS_SERVER,
            ssl_cert_reqs=ssl.CERT_NONE if self.config.verify_mode == "none" else ssl.CERT_REQUIRED
        )

class SecurityHeaders:
    """Security headers middleware."""
    
    def __init__(self, config: SecurityHeadersConfig):
        self.config = config
        
    async def __call__(self, request: Request, call_next):
        response = await call_next(request)
        
        # Add security headers
        self.add_security_headers(response)
        
        return response
    
    def add_security_headers(self, response: Response) -> None:
        """Add security headers to response."""
        
        # Strict Transport Security
        if self.config.hsts_enabled:
            response.headers["Strict-Transport-Security"] = (
                f"max-age={self.config.hsts_max_age}; "
                f"includeSubDomains; preload"
            )
        
        # Content Security Policy
        if self.config.csp_policy:
            response.headers["Content-Security-Policy"] = self.config.csp_policy
        
        # X-Frame-Options
        response.headers["X-Frame-Options"] = "DENY"
        
        # X-Content-Type-Options
        response.headers["X-Content-Type-Options"] = "nosniff"
        
        # X-XSS-Protection
        response.headers["X-XSS-Protection"] = "1; mode=block"
        
        # Referrer Policy
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        # Permissions Policy
        response.headers["Permissions-Policy"] = (
            "geolocation=(), microphone=(), camera=()"
        )
```

### Rate Limiting and DDoS Protection

```python
class AdvancedRateLimiter:
    """Advanced rate limiting with DDoS protection."""
    
    def __init__(self, config: RateLimitConfig):
        self.config = config
        self.redis_client = redis.Redis(
            host=config.redis_host,
            port=config.redis_port,
            db=config.redis_db
        )
        self.suspicious_ips = set()
        
    async def check_rate_limit(self, client_ip: str, endpoint: str) -> RateLimitResult:
        """Check rate limit for client and endpoint."""
        
        # Check if IP is suspicious
        if client_ip in self.suspicious_ips:
            return RateLimitResult(False, "IP blocked due to suspicious activity")
        
        # Get rate limit rules for endpoint
        rules = self.get_rate_limit_rules(endpoint)
        
        for rule in rules:
            if not await self