import os
import logging
import psutil

# Temporary memory-usage instrumentation to diagnose a segmentation fault
# on Streamlit Community Cloud's free tier (1 GB RAM limit). Uses the
# logging module, not print() -- Streamlit Cloud's "Manage app" log panel
# only appears to capture output going through Python's logging system
# (that's how its own deprecation warnings show up), plain stdout prints
# were not showing up there. Not wired into any UI, purely additive
# logging -- safe to remove once the memory picture is clear.
_logger = logging.getLogger("pienza.mem_debug")


def log_mem(label: str) -> None:
    rss_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    _logger.warning(f"[MEM] {label}: {rss_mb:.1f} MB RSS")
