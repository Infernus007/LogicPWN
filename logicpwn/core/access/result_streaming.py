"""
Result streaming and pagination for memory-efficient access testing.

This module provides streaming capabilities and pagination to handle large result sets
without consuming excessive memory, preventing DoS through memory exhaustion.
"""

import asyncio
import gc
import json
import sys
from collections import deque
from collections.abc import AsyncGenerator, Generator
from dataclasses import asdict, dataclass
from enum import Enum
from typing import Any

from logicpwn.core.logging import log_error, log_info, log_warning

from .models import AccessTestResult


class StreamingMode(Enum):
    """Streaming modes for result processing."""

    MEMORY_EFFICIENT = "memory_efficient"  # Process and discard immediately
    BUFFERED = "buffered"  # Keep small buffer in memory
    PERSISTENT = "persistent"  # Keep all results (default behavior)


@dataclass
class StreamingConfig:
    """Configuration for result streaming."""

    mode: StreamingMode = StreamingMode.MEMORY_EFFICIENT
    buffer_size: int = 100  # Number of results to keep in memory
    memory_threshold_mb: int = 500  # Memory threshold to trigger cleanup
    auto_gc: bool = True  # Enable automatic garbage collection
    chunk_size: int = 50  # Number of results to process in each chunk
    export_format: str = "json"  # Format for streaming export (json, csv, etc.)


class ResultStreamer:
    """Handles streaming of access test results with memory management."""

    def __init__(self, config: StreamingConfig):
        self.config = config
        self.buffer: deque = deque(maxlen=config.buffer_size)
        self.total_processed = 0
        self.memory_warnings = 0
        self.export_handlers = {
            "json": self._export_json,
            "csv": self._export_csv,
            "xml": self._export_xml,
        }

    def add_result(self, result: AccessTestResult) -> None:
        """Add a result to the stream."""
        if self.config.mode == StreamingMode.MEMORY_EFFICIENT:
            # Process and export immediately, don't store
            self._process_result_immediate(result)
        elif self.config.mode == StreamingMode.BUFFERED:
            # Add to buffer, export when buffer is full
            self.buffer.append(result)
            if len(self.buffer) >= self.config.buffer_size:
                self._flush_buffer()
        else:  # PERSISTENT
            self.buffer.append(result)

        self.total_processed += 1

        # Check memory usage
        if self.total_processed % 50 == 0:  # Check every 50 results
            self._check_memory_usage()

    def add_results_batch(self, results: list[AccessTestResult]) -> None:
        """Add multiple results efficiently."""
        for result in results:
            self.add_result(result)

    def stream_results(self) -> Generator[AccessTestResult, None, None]:
        """Stream results one by one."""
        # Create a copy of the buffer to avoid modifying the original
        buffer_copy = list(self.buffer)
        self.buffer.clear()
        if self.config.auto_gc:
            gc.collect()

        yield from buffer_copy

    async def stream_results_async(self) -> AsyncGenerator[AccessTestResult, None]:
        """Async generator for streaming results."""
        # Create a copy of the buffer to avoid modifying the original
        buffer_copy = list(self.buffer)
        self.buffer.clear()
        if self.config.auto_gc:
            gc.collect()

        for result in buffer_copy:
            yield result
            # Allow other coroutines to run
            await asyncio.sleep(0)

    def get_results_page(
        self, page: int, page_size: int = 50
    ) -> list[AccessTestResult]:
        """Get a specific page of results."""
        start_idx = page * page_size
        end_idx = start_idx + page_size

        # Convert deque to list for slicing
        buffer_list = list(self.buffer)
        if start_idx < len(buffer_list):
            return buffer_list[start_idx:end_idx]
        return []

    def export_stream(self, output_file: str, format: str = None) -> None:
        """Export streamed results to file."""
        export_format = format or self.config.export_format

        if export_format not in self.export_handlers:
            raise ValueError(f"Unsupported export format: {export_format}")

        handler = self.export_handlers[export_format]
        handler(output_file)

    def _process_result_immediate(self, result: AccessTestResult) -> None:
        """Process result immediately without storing."""
        # Log important findings
        if result.vulnerability_detected:
            log_warning(
                f"Vulnerability detected for ID {result.id_tested}: {result.endpoint_url}"
            )

        # Could trigger immediate alerts, exports, etc.
        if result.error_message:
            log_error(
                f"Error in test for ID {result.id_tested}: {result.error_message}"
            )

    def _flush_buffer(self) -> None:
        """Flush the current buffer."""
        if not self.buffer:
            return

        log_info(f"Flushing buffer with {len(self.buffer)} results")

        # Process all results in buffer
        while self.buffer:
            result = self.buffer.popleft()
            self._process_result_immediate(result)

        # Force garbage collection if enabled
        if self.config.auto_gc:
            gc.collect()

    def _check_memory_usage(self) -> None:
        """Check current memory usage and trigger cleanup if needed."""
        try:
            import psutil

            process = psutil.Process()
            memory_mb = process.memory_info().rss / 1024 / 1024

            if memory_mb > self.config.memory_threshold_mb:
                self.memory_warnings += 1
                log_warning(
                    f"Memory usage ({memory_mb:.1f}MB) exceeds threshold ({self.config.memory_threshold_mb}MB)"
                )

                # Trigger cleanup
                self._emergency_cleanup()

        except ImportError:
            # Fallback to sys.getsizeof for basic memory tracking
            buffer_size = sum(sys.getsizeof(result) for result in self.buffer)
            if buffer_size > self.config.memory_threshold_mb * 1024 * 1024:
                log_warning("Buffer size exceeds memory threshold, triggering cleanup")
                self._emergency_cleanup()

    def _emergency_cleanup(self) -> None:
        """Emergency memory cleanup."""
        log_warning("Performing emergency memory cleanup")

        # Flush half the buffer
        flush_count = len(self.buffer) // 2
        for _ in range(flush_count):
            if self.buffer:
                result = self.buffer.popleft()
                self._process_result_immediate(result)

        # Force garbage collection
        gc.collect()

    def _export_json(self, output_file: str) -> None:
        """Export results to JSON format."""
        results_data = []
        # Create a copy to avoid modifying the buffer during export
        buffer_copy = list(self.buffer)
        for result in buffer_copy:
            results_data.append(asdict(result))

        with open(output_file, "w") as f:
            json.dump(results_data, f, indent=2, default=str)

    def _export_csv(self, output_file: str) -> None:
        """Export results to CSV format."""
        import csv

        if not self.buffer:
            return

        # Create a copy to avoid modifying the buffer during export
        buffer_copy = list(self.buffer)

        # Get field names from first result
        first_result = buffer_copy[0]
        fieldnames = asdict(first_result).keys()

        with open(output_file, "w", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()

            for result in buffer_copy:
                writer.writerow(asdict(result))

    def _export_xml(self, output_file: str) -> None:
        """Export results to XML format."""
        import xml.etree.ElementTree as ET

        root = ET.Element("access_test_results")

        # Create a copy to avoid modifying the buffer during export
        buffer_copy = list(self.buffer)

        for result in buffer_copy:
            result_elem = ET.SubElement(root, "result")
            result_dict = asdict(result)

            for key, value in result_dict.items():
                elem = ET.SubElement(result_elem, key)
                elem.text = str(value) if value is not None else ""

        tree = ET.ElementTree(root)
        tree.write(output_file, encoding="utf-8", xml_declaration=True)

    def get_statistics(self) -> dict[str, Any]:
        """Get streaming statistics."""
        # Count vulnerabilities and errors from the current buffer
        vulnerabilities = sum(
            1 for result in self.buffer if result.vulnerability_detected
        )
        errors = sum(1 for result in self.buffer if result.error_message)

        return {
            "total_processed": self.total_processed,
            "buffer_size": len(self.buffer),
            "vulnerabilities_found": vulnerabilities,
            "errors_encountered": errors,
            "memory_warnings": self.memory_warnings,
            "streaming_mode": self.config.mode.value,
        }

    def clear(self) -> None:
        """Clear all buffered results."""
        self.buffer.clear()
        if self.config.auto_gc:
            gc.collect()


class PaginatedResultManager:
    """Manages paginated access to large result sets."""

    def __init__(self, page_size: int = 50):
        self.page_size = page_size
        self.results: list[AccessTestResult] = []
        self.current_page = 0

    def add_results(self, results: list[AccessTestResult]) -> None:
        """Add results to the manager."""
        self.results.extend(results)

    def get_page(self, page: int) -> list[AccessTestResult]:
        """Get a specific page of results."""
        start_idx = page * self.page_size
        end_idx = start_idx + self.page_size
        return self.results[start_idx:end_idx]

    def get_current_page(self) -> list[AccessTestResult]:
        """Get the current page."""
        return self.get_page(self.current_page)

    def next_page(self) -> list[AccessTestResult]:
        """Move to next page and return results."""
        if self.has_next_page():
            self.current_page += 1
        return self.get_current_page()

    def previous_page(self) -> list[AccessTestResult]:
        """Move to previous page and return results."""
        if self.has_previous_page():
            self.current_page -= 1
        return self.get_current_page()

    def has_next_page(self) -> bool:
        """Check if there's a next page."""
        return (self.current_page + 1) * self.page_size < len(self.results)

    def has_previous_page(self) -> bool:
        """Check if there's a previous page."""
        return self.current_page > 0

    def get_total_pages(self) -> int:
        """Get total number of pages."""
        return (len(self.results) + self.page_size - 1) // self.page_size

    def get_page_info(self) -> dict[str, Any]:
        """Get pagination information."""
        return {
            "current_page": self.current_page,
            "total_pages": self.get_total_pages(),
            "page_size": self.page_size,
            "total_results": len(self.results),
            "has_next": self.has_next_page(),
            "has_previous": self.has_previous_page(),
        }


def create_memory_efficient_streamer(
    memory_threshold_mb: int = 500, buffer_size: int = 100, export_format: str = "json"
) -> ResultStreamer:
    """Create a memory-efficient result streamer."""
    config = StreamingConfig(
        mode=StreamingMode.MEMORY_EFFICIENT,
        memory_threshold_mb=memory_threshold_mb,
        buffer_size=buffer_size,
        export_format=export_format,
        auto_gc=True,
    )
    return ResultStreamer(config)


def create_buffered_streamer(
    buffer_size: int = 200, memory_threshold_mb: int = 1000
) -> ResultStreamer:
    """Create a buffered result streamer."""
    config = StreamingConfig(
        mode=StreamingMode.BUFFERED,
        buffer_size=buffer_size,
        memory_threshold_mb=memory_threshold_mb,
        auto_gc=True,
    )
    return ResultStreamer(config)


async def process_results_in_chunks(
    results: list[AccessTestResult],
    chunk_size: int = 50,
    processor_func: callable = None,
) -> None:
    """Process large result sets in chunks to manage memory."""
    total_chunks = (len(results) + chunk_size - 1) // chunk_size

    for i in range(0, len(results), chunk_size):
        chunk = results[i : i + chunk_size]
        chunk_num = (i // chunk_size) + 1

        log_info(f"Processing chunk {chunk_num}/{total_chunks} ({len(chunk)} results)")

        if processor_func:
            await processor_func(chunk)

        # Allow other coroutines to run and trigger GC
        await asyncio.sleep(0.1)
        gc.collect()


def monitor_memory_usage(func):
    """Decorator to monitor memory usage of functions."""

    def wrapper(*args, **kwargs):
        try:
            import psutil

            process = psutil.Process()
            memory_before = process.memory_info().rss / 1024 / 1024

            result = func(*args, **kwargs)

            memory_after = process.memory_info().rss / 1024 / 1024
            memory_diff = memory_after - memory_before

            if memory_diff > 100:  # Log if memory increased by more than 100MB
                log_warning(
                    f"Function {func.__name__} increased memory by {memory_diff:.1f}MB"
                )

            return result

        except ImportError:
            # Fallback without memory monitoring
            return func(*args, **kwargs)

    return wrapper
