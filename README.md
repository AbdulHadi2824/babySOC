# babySOC

A small, Windows-focused Security Operations Center (SOC) toolkit for learning host-monitoring fundamentals. It collects three kinds of host telemetry — network connections, running processes, and scheduled tasks — into a local SQLite database, and separately watches a folder of files for tampering via SHA-256 hashing. A Tkinter GUI ties the collectors together into a one-click "scan".

## Features

- **Network connection snapshot** (`netwatch.py`) — captures active TCP/UDP connections (local/remote address, port, status, owning PID) via `psutil`.
- **Process snapshot** (`processes.py`) — captures the running process list (PID, name) via `psutil`.
- **Scheduled task snapshot** (`schedules.py`) — captures Windows Task Scheduler entries via `schtasks /query`.
- **File integrity monitor** (`monitor.py`) — baselines SHA-256 hashes of `.txt` files in `tests/`, then polls on an interval to detect tampering (content changes), new files, and deletions.
- **GUI** (`gui.py`) — a Tkinter app with a single "Scan" button that runs the network/process/schedule collectors and displays results in a tabbed results window.

## Project layout

```
babySOC/
├── gui.py            # Tkinter front-end; runs all collectors and shows results
├── monitor.py         # File integrity monitor (hashing + tamper/deletion detection)
├── netwatch.py         # Network connections collector
├── processes.py        # Running processes collector
├── schedules.py         # Windows scheduled tasks collector
├── constraints.py       # Shared config (paths, poll interval)
├── tests/            # Sample files watched by monitor.py
├── hashes/            # Legacy per-file .sha256 hash outputs
├── hashes.txt          # Legacy baseline hash log
├── hashes.db           # SQLite database (connections, processes, schedules, hashes tables)
└── requirements.txt
```

## Requirements

- Windows (uses `schtasks` for scheduled-task collection)
- Python 3.11+
- [psutil](https://pypi.org/project/psutil/)

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

### GUI scan

Runs the network, process, and schedule collectors in one pass and opens a results window with a tab per data source.

```bash
python gui.py
```

### Individual collectors

Each collector can also be run standalone; it (re)creates its table if needed, collects one snapshot, and stores it in `hashes.db`.

```bash
python netwatch.py
python processes.py
python schedules.py
```

### File integrity monitor

Baselines the `.txt` files in `tests/`, then checks for changes every `INTERVAL` seconds (see `constraints.py`), logging tampering, new files, and deletions to the console and persisting hash state to `hashes.db`.

```bash
python monitor.py
```

Press `Ctrl+C` to stop.

## Configuration

Shared settings live in `constraints.py`:

| Constant    | Purpose                                      |
|-------------|-----------------------------------------------|
| `TESTS_DIR` | Directory watched by the file integrity monitor |
| `INTERVAL`  | Seconds between integrity checks                |
| `DB_FILE`   | SQLite database file used by all collectors     |

## Data storage

All collectors write to the same SQLite database (`hashes.db`), each owning its own table:

- `connections` — local/remote address & port, status, PID, capture time
- `processes` — PID, name, capture time
- `schedules` — task name, next run time, status, capture time
- `hashes` — filename, SHA-256 digest, last-tampered timestamp

Each collector clears and repopulates its table on every run, so `hashes.db` always reflects the most recent snapshot.
