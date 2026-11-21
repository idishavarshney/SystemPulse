"""SystemPulse local monitor API.

Run this process on the computer you want to monitor. It binds to loopback only,
so it is not exposed to your LAN or the public internet.
"""
from datetime import datetime, timezone
import os
import platform
import socket
import time

import psutil
from flask import Flask, jsonify, request, render_template

app = Flask(__name__)
BOOT_TIME = psutil.boot_time()
# Prime psutil's non-blocking CPU sampler so the first reading is meaningful.
psutil.cpu_percent(interval=None)

DEFAULT_ALLOWED_ORIGINS = {
    "https://systempulse-mocha.vercel.app",
    "https://systempulse-ankushs-projects-72be89bb.vercel.app",
    "https://systempulse-git-main-ankushs-projects-72be89bb.vercel.app",
    "http://127.0.0.1:5000",
    "http://localhost:5000",
}
ALLOWED_ORIGINS = DEFAULT_ALLOWED_ORIGINS | {
    origin.strip().rstrip("/")
    for origin in os.environ.get("SYSTEMPULSE_ALLOWED_ORIGINS", "").split(",")
    if origin.strip()
}


@app.before_request
def handle_preflight():
    # Chromium may send a Private Network Access preflight before an HTTPS
    # dashboard is allowed to call a loopback HTTP monitor.
    if request.method == "OPTIONS":
        return ("", 204)


@app.after_request
def add_local_api_headers(response):
    origin = request.headers.get("Origin", "").rstrip("/")
    if origin in ALLOWED_ORIGINS:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Vary"] = "Origin"
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = request.headers.get("Access-Control-Request-Headers", "Content-Type")
        # Required by Chromium when a public HTTPS page accesses loopback.
        if request.headers.get("Access-Control-Request-Private-Network") == "true":
            response.headers["Access-Control-Allow-Private-Network"] = "true"
    response.headers["Cache-Control"] = "no-store"
    return response


def system_stats():
    memory = psutil.virtual_memory()
    if platform.system() == "Windows":
        disk_path = os.environ.get("SystemDrive", "C:") + "\\"
    else:
        disk_path = "/"
    try:
        disk = psutil.disk_usage(disk_path)
    except (OSError, PermissionError):
        disk = psutil.disk_usage("/")
    return {
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent,
        "memory_used": memory.used,
        "memory_total": memory.total,
        "disk_percent": disk.percent,
        "disk_used": disk.used,
        "disk_total": disk.total,
        "uptime_seconds": max(0, int(time.time() - BOOT_TIME)),
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "cpu_cores": psutil.cpu_count(logical=True) or 0,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }


def process_list():
    items = []
    for proc in psutil.process_iter(["pid", "name", "status", "memory_percent"]):
        try:
            info = proc.info
            items.append({
                "pid": info.get("pid"),
                "name": info.get("name") or "Unknown",
                "status": info.get("status") or "unknown",
                "cpu_percent": proc.cpu_percent(interval=None),
                "memory_percent": round(info.get("memory_percent") or 0, 2),
            })
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            continue
    return sorted(items, key=lambda item: item["cpu_percent"], reverse=True)


@app.get("/")
def index():
    return render_template("index.html")


@app.get("/api/health")
def api_health():
    return jsonify({
        "status": "online",
        "hostname": socket.gethostname(),
        "os": f"{platform.system()} {platform.release()}",
        "agent": "SystemPulse local monitor",
    })


@app.get("/api/system")
def api_system():
    return jsonify(system_stats())


@app.get("/api/processes")
def api_processes():
    return jsonify(process_list())


@app.get("/api/performance")
def api_performance():
    memory = psutil.virtual_memory()
    return jsonify({
        "cpu_percent": psutil.cpu_percent(interval=None),
        "memory_percent": memory.percent,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    })


if __name__ == "__main__":
    # Loopback-only: the monitor is intentionally not reachable from other devices.
    print("\nSystemPulse local monitor is starting...")
    print("Open the Vercel dashboard after this server is running.")
    print("Local health check: http://127.0.0.1:5000/api/health")
    app.run(host="127.0.0.1", port=5000, debug=False, threaded=True)
