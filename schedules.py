import csv
import time
import sqlite3
import subprocess

from constraints import DB_FILE

def setup_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS schedules (task_name TEXT, next_run TEXT, status TEXT, captured_at TEXT)")
    conn.commit()
    conn.close()

def collect_schedules():
    result = subprocess.run(
        ["schtasks", "/query", "/fo", "CSV"],
        capture_output=True
    )
    text = result.stdout.decode("utf-8", errors="replace")

    rows = []
    reader = csv.reader(text.splitlines())

    for fields in reader:
        if len(fields) < 3:
            continue
        if fields[0] == "TaskName":
            continue
        rows.append((fields[0], fields[1], fields[2]))

    return rows


def save_schedules(rows, captured_at):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM schedules")

    for row in rows:
        conn.execute(
            "INSERT INTO schedules (task_name, next_run, status, captured_at) VALUES (?, ?, ?, ?)",
            (row[0], row[1], row[2], captured_at)
        )

    conn.commit()
    conn.close()


if __name__ == "__main__":
    setup_db()
    captured_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    rows = collect_schedules()
    save_schedules(rows, captured_at)
    print("captured", len(rows), "scheduled tasks at", captured_at)
