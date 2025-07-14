from typing import List, Union, Optional
import requests
from concurrent.futures import ThreadPoolExecutor, as_completed
from logicpwn.core.performance.performance_monitor import monitor_performance
from logicpwn.core.runner.async_runner_core import AsyncRequestRunner
import asyncio
from .models import AccessTestResult, AccessDetectorConfig
from .utils import (
    _validate_inputs, _sanitize_test_id, _test_single_id, _test_single_id_async
)

@monitor_performance("idor_detection_batch")
def detect_idor_flaws(
    session: requests.Session,
    endpoint_template: str,
    test_ids: List[Union[str, int]],
    success_indicators: List[str],
    failure_indicators: List[str],
    config: Optional[AccessDetectorConfig] = None
) -> List[AccessTestResult]:
    config = config or AccessDetectorConfig()
    _validate_inputs(endpoint_template, test_ids, success_indicators, failure_indicators)
    results: List[AccessTestResult] = []
    with ThreadPoolExecutor(max_workers=config.max_concurrent_requests) as executor:
        futures = []
        for test_id in test_ids:
            sanitized_id = _sanitize_test_id(test_id)
            url = endpoint_template.format(id=sanitized_id)
            futures.append(executor.submit(
                _test_single_id,
                session,
                url,
                sanitized_id,
                success_indicators,
                failure_indicators,
                config.request_timeout,
                config
            ))
        for future in as_completed(futures):
            results.append(future.result())
    return results

async def detect_idor_flaws_async(
    endpoint_template: str,
    test_ids: List[Union[str, int]],
    success_indicators: List[str],
    failure_indicators: List[str],
    config: Optional[AccessDetectorConfig] = None
) -> List[AccessTestResult]:
    config = config or AccessDetectorConfig()
    _validate_inputs(endpoint_template, test_ids, success_indicators, failure_indicators)
    results: List[AccessTestResult] = []
    async with AsyncRequestRunner(max_concurrent=config.max_concurrent_requests, timeout=config.request_timeout) as runner:
        tasks = []
        for test_id in test_ids:
            sanitized_id = _sanitize_test_id(test_id)
            url = endpoint_template.format(id=sanitized_id)
            tasks.append(_test_single_id_async(
                runner,
                url,
                sanitized_id,
                success_indicators,
                failure_indicators,
                config.request_timeout,
                config
            ))
        results = await asyncio.gather(*tasks)
    return results 