import os
import psutil

# Temporary memory-usage instrumentation to diagnose a segmentation fault
# on Streamlit Community Cloud's free tier (1 GB RAM limit). Prints to
# stdout, visible in the "Manage app" log panel on Streamlit Cloud. Not
# wired into any UI, purely additive logging -- safe to remove once the
# memory picture is clear.
def log_mem(label: str) -> None:
    rss_mb = psutil.Process(os.getpid()).memory_info().rss / (1024 * 1024)
    print(f"[MEM] {label}: {rss_mb:.1f} MB RSS")
