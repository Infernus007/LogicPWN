from typing import List, Union, Optional
import requests
from logicpwn.core.runner.runner import send_request
from logicpwn.core.utils import check_indicators
from logicpwn.core.cache.cache_utils import cached
from logicpwn.core.logging import log_info, log_warning, log_error
from tenacity import retry, stop_after_attempt, wait_exponential
from urllib.parse import urlparse
import re
import time
import asyncio
from .models import AccessTestResult, AccessDetectorConfig
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner

# --- Validation and Sanitization ---
def _validate_endpoint_template(template: str) -> None:
    try:
        parsed = urlparse(template.format(id='test'))
        if parsed.scheme not in ['http', 'https']:
            raise ValueError("Only HTTP/HTTPS schemes allowed in endpoint_template")
    except Exception:
        raise ValueError("Invalid endpoint_template or URL format")

def _validate_inputs(endpoint_template: str, test_ids: List[Union[str, int]], success_indicators: List[str], failure_indicators: List[str]):
    _validate_endpoint_template(endpoint_template)
    if not endpoint_template or '{id}' not in endpoint_template:
        raise ValueError("endpoint_template must contain '{id}' placeholder")
    if not test_ids:
        raise ValueError("test_ids cannot be empty")
    if not success_indicators:
        raise ValueError("success_indicators cannot be empty")
    if not failure_indicators:
        raise ValueError("failure_indicators cannot be empty")

def _sanitize_test_id(test_id: Union[str, int]) -> Union[str, int]:
    if isinstance(test_id, str):
        return re.sub(r'[^a-zA-Z0-9_-]', '', test_id)
    return test_id

# --- Baseline and Retry ---
@cached(ttl=600, key_func=lambda endpoint_url, id_value, timeout: f"{endpoint_url}|{id_value}|{timeout}")
def _get_unauth_baseline(endpoint_url: str, id_value: Union[str, int], request_timeout: int) -> Optional[requests.Response]:
    try:
        session = requests.Session()
        response = send_request(session, {
            "url": endpoint_url,
            "method": "GET",
            "timeout": request_timeout
        })
        return response
    except Exception as e:
        log_warning(f"Baseline unauthenticated request failed for {endpoint_url}: {e}")
        return None

@retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=2, max=10))
def _make_request_with_retry(session, request_config):
    return send_request(session, request_config)

# --- Core Logic Helpers ---
def _determine_vulnerability(id_tested, access_granted, config: AccessDetectorConfig) -> bool:
    if not access_granted:
        return False
    if config.authorized_ids is not None:
        return id_tested not in config.authorized_ids
    if config.current_user_id is not None:
        return id_tested != config.current_user_id
    if config.unauthorized_ids is not None:
        return id_tested in config.unauthorized_ids
    return False

def _should_have_access(id_tested, config: AccessDetectorConfig) -> bool:
    if config.authorized_ids is not None:
        return id_tested in config.authorized_ids
    if config.current_user_id is not None:
        return id_tested == config.current_user_id
    if config.unauthorized_ids is not None:
        return id_tested not in config.unauthorized_ids
    return False

def _check_unauthenticated_baseline(
    result: AccessTestResult,
    success_indicators: List[str],
    failure_indicators: List[str],
    config: AccessDetectorConfig
) -> AccessTestResult:
    if not config.compare_unauthenticated:
        return result
    try:
        unauth_response = _get_unauth_baseline(
            result.endpoint_url,
            result.id_tested,
            config.request_timeout
        )
        if unauth_response is not None:
            is_success, matched = check_indicators(unauth_response.text, success_indicators)
            is_failure, failed = check_indicators(unauth_response.text, failure_indicators)
            if is_success and not is_failure:
                result.vulnerability_detected = True
                result.error_message = (result.error_message or "") + " | Unauthenticated access possible"
        else:
            log_warning(f"No unauth baseline for {result.endpoint_url}")
    except Exception as e:
        log_warning(f"Failed to get unauth baseline for {result.endpoint_url}: {e}")
    return result

def _test_single_id(
    session: requests.Session,
    endpoint_url: str,
    id_value: Union[str, int],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig
) -> AccessTestResult:
    if config.rate_limit:
        time.sleep(config.rate_limit)
    log_info(f"Testing access to {endpoint_url} for ID {id_value}")
    try:
        response = _make_request_with_retry(session, {
            "url": endpoint_url,
            "method": "GET",
            "timeout": request_timeout
        })
        is_success, matched = check_indicators(response.text, success_indicators)
        is_failure, failed = check_indicators(response.text, failure_indicators)
        access_granted = is_success and not is_failure
        expected_access = _should_have_access(id_value, config)
        vuln = _determine_vulnerability(id_value, access_granted, config)
        result = AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=response.status_code,
            access_granted=access_granted,
            vulnerability_detected=vuln,
            response_indicators=matched + failed,
            expected_access=expected_access
        )
        return _check_unauthenticated_baseline(result, success_indicators, failure_indicators, config)
    except requests.exceptions.Timeout:
        log_warning(f"Timeout for {endpoint_url}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message="Timeout"
        )
    except requests.exceptions.ConnectionError:
        log_warning(f"Connection error for {endpoint_url}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message="Connection error"
        )
    except Exception as e:
        log_error(f"Request failed for {endpoint_url}: {e}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message=str(e)
        )

async def _test_single_id_async(
    runner: AsyncRequestRunner,
    endpoint_url: str,
    id_value: Union[str, int],
    success_indicators: List[str],
    failure_indicators: List[str],
    request_timeout: int,
    config: AccessDetectorConfig
) -> AccessTestResult:
    if config.rate_limit:
        await asyncio.sleep(config.rate_limit)
    log_info(f"[Async] Testing access to {endpoint_url} for ID {id_value}")
    try:
        result = await runner.send_request(
            url=endpoint_url,
            method="GET",
            timeout=request_timeout
        )
        is_success, matched = check_indicators(result.body, success_indicators)
        is_failure, failed = check_indicators(result.body, failure_indicators)
        access_granted = is_success and not is_failure
        expected_access = _should_have_access(id_value, config)
        vuln = _determine_vulnerability(id_value, access_granted, config)
        result_obj = AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=result.status_code,
            access_granted=access_granted,
            vulnerability_detected=vuln,
            response_indicators=matched + failed,
            expected_access=expected_access
        )
        return _check_unauthenticated_baseline(result_obj, success_indicators, failure_indicators, config)
    except Exception as e:
        log_warning(f"Async request failed for {endpoint_url}: {e}")
        return AccessTestResult(
            id_tested=id_value,
            endpoint_url=endpoint_url,
            status_code=0,
            access_granted=False,
            vulnerability_detected=False,
            response_indicators=[],
            error_message=str(e)
        ) 