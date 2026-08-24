import psutil
import sqlite3
from constraints import DB_FILE
import time

def setup_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS connections (local_addr TEXT, local_port INTEGER, remote_addr TEXT, remote_port INTEGER, status TEXT, pid INTEGER, captured_at TEXT)")
    conn.commit()
    conn.close()

def collect_connections():
    rows = []

    for conn in psutil.net_connections(kind="inet"):
        local_addr = conn.laddr.ip
        local_port = conn.laddr.port

        if conn.raddr:
            remote_addr = conn.raddr.ip
            remote_port = conn.raddr.port
        else:
            remote_addr = None
            remote_port = None

        rows.append((local_addr, local_port, remote_addr, remote_port, conn.status, conn.pid))

    return rows

def save_connections(rows, captured_at):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM connections")

    for row in rows:
        conn.execute(
            "INSERT INTO connections (local_addr, local_port, remote_addr, remote_port, status, pid, captured_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
            (row[0], row[1], row[2], row[3], row[4], row[5], captured_at)
        )

    conn.commit()
    conn.close()

if __name__ == "__main__":
    setup_db()
    captured_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    rows = collect_connections()
    save_connections(rows, captured_at)
    print("captured", len(rows), "connections at", captured_at)