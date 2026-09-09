import signal
import subprocess
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parent
stopping = threading.Event()


def stop(signum, frame):
    stopping.set()


signal.signal(signal.SIGTERM, stop)
signal.signal(signal.SIGINT, stop)


def supervise(name, command):
    while not stopping.is_set():
        print(f"Starting {name}", flush=True)
        process = subprocess.Popen(command, cwd=ROOT)

        while process.poll() is None:
            if stopping.wait(1):
                process.terminate()
                try:
                    process.wait(timeout=15)
                except subprocess.TimeoutExpired:
                    process.kill()
                    process.wait()
                return

        print(
            f"{name} stopped: {process.returncode}. "
            "Restarting in 5 seconds.",
            flush=True,
        )
        stopping.wait(5)


services = [
    (
        "payment server",
        [
            sys.executable, "-m", "gunicorn",
            "--bind", "0.0.0.0:80",
            "--workers", "1",
            "--threads", "4",
            "--access-logfile", "-",
            "--error-logfile", "-",
            "server:app",
        ],
    ),
    ("telegram bot", [sys.executable, "-u", "bot.py"]),
]

threads = [
    threading.Thread(target=supervise, args=service)
    for service in services
]

for thread in threads:
    thread.start()

for thread in threads:
    thread.join()
