"""Process related utilities"""

from datetime import datetime, timezone
from os import getpid

from psutil import Process


def realtime(pid: int = -1) -> float:
    """Returns the process' real time duration. If the pid is less than
    0, the time for the current process is returned."""
    if pid < 0:
        pid = getpid()
    start = Process(pid).create_time()
    start_time = datetime.fromtimestamp(start, timezone.utc)
    real_time = datetime.now(tz=timezone.utc) - start_time
    return real_time.total_seconds()
