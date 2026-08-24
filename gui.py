import time
import sqlite3
import tkinter as tk
from tkinter import ttk

import netwatch
import schedules
import processes

from constraints import DB_FILE


def run_netwatch():
    netwatch.setup_db()
    captured_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    rows = netwatch.collect_connections()
    netwatch.save_connections(rows, captured_at)


def run_schedules():
    schedules.setup_db()
    captured_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    rows = schedules.collect_schedules()
    schedules.save_schedules(rows, captured_at)


def run_processes():
    processes.setup_db()
    captured_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    rows = processes.collect_processes()
    processes.save_processes(rows, captured_at)


def run_scan():
    scan_button.config(state="disabled")
    progress["value"] = 0

    steps = [
        ("networks", run_netwatch),
        ("schedules", run_schedules),
        ("processes", run_processes),
    ]

    for i in range(len(steps)):
        name, func = steps[i]
        status.config(text="Scanning " + name + "...")
        root.update()

        func()

        progress["value"] = (i + 1) * 100 / len(steps)
        root.update()

    status.config(text="Scan complete")
    scan_button.config(state="normal")
    show_results()


def fetch_rows(query):
    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute(query).fetchall()
    conn.close()
    return rows


def make_tab(notebook, title, columns, query):
    frame = ttk.Frame(notebook)
    notebook.add(frame, text=title)

    tree = ttk.Treeview(frame, columns=columns, show="headings")
    for name in columns:
        tree.heading(name, text=name)
        tree.column(name, width=140)

    scroll = ttk.Scrollbar(frame, orient="vertical", command=tree.yview)
    tree.configure(yscrollcommand=scroll.set)

    tree.pack(side="left", fill="both", expand=True)
    scroll.pack(side="right", fill="y")

    for row in fetch_rows(query):
        tree.insert("", "end", values=row)


def show_results():
    window = tk.Toplevel(root)
    window.title("Scan Results")
    window.geometry("950x500")

    notebook = ttk.Notebook(window)
    notebook.pack(fill="both", expand=True)

    make_tab(
        notebook, "CPU",
        ("pid", "name", "captured_at"),
        "SELECT pid, name, captured_at FROM processes"
    )
    make_tab(
        notebook, "Networks",
        ("local_addr", "local_port", "remote_addr", "remote_port", "status", "pid", "captured_at"),
        "SELECT local_addr, local_port, remote_addr, remote_port, status, pid, captured_at FROM connections"
    )
    make_tab(
        notebook, "Schedules",
        ("task_name", "next_run", "status", "captured_at"),
        "SELECT task_name, next_run, status, captured_at FROM schedules"
    )


if __name__ == "__main__":
    root = tk.Tk()
    root.title("babySOC Scanner")
    root.geometry("400x160")

    status = tk.Label(root, text="Ready")
    status.pack(pady=10)

    progress = ttk.Progressbar(root, length=300, maximum=100)
    progress.pack(pady=5)

    scan_button = tk.Button(root, text="Scan", command=run_scan)
    scan_button.pack(pady=10)

    root.mainloop()