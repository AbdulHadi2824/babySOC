import sqlite3
import psutil
import time
from constraints import DB_FILE


def setup_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS processes (pid INTEGER PRIMARY KEY, name TEXT, captured_at TEXT)")
    conn.commit()
    conn.close()

def collect_processes():
    rows = []
    for proc in psutil.process_iter(["pid", "name"]):
        rows.append((proc.info["pid"], proc.info["name"]))
    return rows

def save_processes(rows, captured_at):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM processes")

    for row in rows:
        conn.execute(
            "INSERT INTO processes (pid, name, captured_at) VALUES (?, ?, ?)",
            (row[0], row[1], captured_at)
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
    captured_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    rows = collect_processes()
    save_processes(rows, captured_at)
    print("captured", len(rows), "processes at", captured_at)