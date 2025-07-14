from typing import List, Union, Optional
from dataclasses import dataclass, field

@dataclass
class AccessTestResult:
    id_tested: Union[str, int]
    endpoint_url: str
    status_code: int
    access_granted: bool
    vulnerability_detected: bool
    response_indicators: List[str] = field(default_factory=list)
    error_message: Optional[str] = None
    expected_access: Optional[bool] = None

@dataclass
class AccessDetectorConfig:
    max_concurrent_requests: int = 10
    request_timeout: int = 30
    retry_attempts: int = 3
    compare_unauthenticated: bool = True
    current_user_id: Optional[Union[str, int]] = None
    authorized_ids: Optional[List[Union[str, int]]] = None
    unauthorized_ids: Optional[List[Union[str, int]]] = None
    rate_limit: Optional[float] = None  # seconds between requests 