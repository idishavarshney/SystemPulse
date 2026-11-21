# SystemPulse

A cross-platform system monitoring dashboard for **your actual computer**. The dashboard can be opened from the public Vercel website, while a small local Python monitor reads CPU, RAM, disk, uptime and running processes from your own Windows, Ubuntu/Linux or macOS device.

## How it works

- **Dashboard:** hosted at https://systempulse-mocha.vercel.app
- **Local monitor:** runs on your computer at `127.0.0.1:5000`
- The dashboard connects directly from your browser to the local monitor. It does not use Vercel's server metrics as a substitute.
- The local monitor binds to loopback only; other devices on your network cannot connect to it.
- Monitoring is read-only. SystemPulse does not terminate processes, change services or upload process data to a cloud database.

> Keep the local monitor running while using the hosted dashboard. If it is stopped, the dashboard shows a disconnected state instead of displaying misleading cloud-server metrics.

## Requirements

- Python 3.9 or newer
- pip
- Internet access for the hosted dashboard and its Chart.js/Google Fonts assets

## Windows (PowerShell)

The easiest method is to download the ZIP from GitHub, extract it, and double-click **`start-systempulse.bat`**. It creates the virtual environment, installs dependencies and starts the monitor. Keep the terminal window open.

Manual setup (PowerShell in the project folder):

```powershell
py -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe app.py
```

If you prefer activating the environment:

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python app.py
```

If PowerShell blocks activation, use the direct `.venv\Scripts\python.exe` commands above. Keep this terminal window open.

## Ubuntu / Linux

The easiest method is to make the launcher executable and run it from the project folder:

```bash
chmod +x start-systempulse.sh
./start-systempulse.sh
```

Manual setup:

```bash
sudo apt update
sudo apt install -y python3 python3-venv python3-pip
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

Keep the terminal open while monitoring.

## macOS

Use the same launcher as Linux:

```bash
chmod +x start-systempulse.sh
./start-systempulse.sh
```

Manual setup:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
.venv/bin/python -m pip install -r requirements.txt
.venv/bin/python app.py
```

If macOS does not have Python 3 installed, install Python 3 first, then run the commands above.

## Open the dashboard

1. Start the local monitor using the commands for your operating system.
2. Confirm the terminal says it is running at `http://127.0.0.1:5000`.
3. Open https://systempulse-mocha.vercel.app in the same computer and browser.
4. The header should show **Connected** and your computer's hostname.
5. Leave the Python process running. It refreshes every three seconds.

You can also open http://127.0.0.1:5000 to use the dashboard locally.

## Troubleshooting

- **Disconnected / retrying:** make sure `python app.py` is still running, then click Retry connection.
- **Browser permission prompt:** allow the page to access the local network/device if your browser asks.
- **Connection still fails:** use the current production URL above (not a stale preview URL), restart the local monitor, and refresh the dashboard.
- **Port 5000 is already in use:** close the other application using that port before starting SystemPulse.
- **Missing process details:** some operating-system processes are protected. Run with normal user permissions first; elevated permissions may expose more details but are not required for normal use.
- **Chart not visible:** numeric metrics and process monitoring still work; check that your browser can load the Chart.js CDN.

## API

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/health` | Local monitor connection check |
| GET | `/api/system` | CPU, memory, disk, uptime and device details |
| GET | `/api/processes` | Current process list |
| GET | `/api/performance` | CPU and memory history sample |

## Security and privacy

- The local server listens only on `127.0.0.1`, not on `0.0.0.0`.
- Cross-origin browser requests are allowed only from the production SystemPulse origin and local dashboard origins by default.
- The app is read-only and does not provide process-kill or service-control endpoints.
- The dashboard reads metrics directly from the browser's local monitor. No cloud database or telemetry upload is configured.

## Run automated tests

```bash
python -m pip install -r requirements.txt
python -m unittest discover -s tests -v
```

GitHub Actions also runs these API and CORS checks on pushes to `main` and pull requests.

## License

MIT. See [LICENSE](LICENSE).
