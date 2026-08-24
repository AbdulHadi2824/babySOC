import os
import time
import hashlib
import sqlite3

from constraints import TESTS_DIR, DB_FILE, INTERVAL



def setup_db():
    conn = sqlite3.connect(DB_FILE)
    conn.execute("CREATE TABLE IF NOT EXISTS hashes (filename TEXT PRIMARY KEY, digest TEXT, tampered_at TEXT)")
    conn.commit()
    conn.close()


def txt_files():
    names = []
    for filename in os.listdir(TESTS_DIR):
        if filename.endswith(".txt"):
            names.append(filename)
    names.sort()
    return names

def sha256_of_file(path):
    with open(path, "rb") as f:
        data = f.read()
    return hashlib.sha256(data).hexdigest()

def load_hashes():
    hashes = {}

    conn = sqlite3.connect(DB_FILE)
    rows = conn.execute("SELECT filename, digest FROM hashes")

    for row in rows:
        hashes[row[0]] = row[1]

    conn.close()
    return hashes

def save_hashes(hashes, tampered_at):
    conn = sqlite3.connect(DB_FILE)
    conn.execute("DELETE FROM hashes")

    for filename in sorted(hashes.keys()):
        conn.execute(
            "INSERT INTO hashes (filename, digest, tampered_at) VALUES (?, ?, ?)",
            (filename, hashes[filename], tampered_at.get(filename))
        )

    conn.commit()
    conn.close()
# def stored_hash_path(filename):
#     return os.path.join(HASH_FILE, filename + ".sha256")

# def read_stored_hash(filename):
#     path = stored_hash_path(filename)
#     if not os.path.exists(path):
#         return None
#     with open(path, "r") as f:
#         return f.read().strip()

# def write_stored_hash(filename, digest):
#     with open(stored_hash_path(filename), "w") as f:
#         f.write(digest)

def check_for_changes(hashes, tampered_at, last_seen):
    for filename in txt_files():
        new_digest = sha256_of_file(os.path.join(TESTS_DIR, filename))


        if filename not in hashes:
            print("new file", filename, "has appeared")
            hashes[filename] = new_digest
            last_seen[filename] = new_digest

        elif new_digest !=  hashes[filename]:
            print("!!!TAMPERED!!!", filename)
            print("Expected: ", hashes[filename])
            print("Actual: ", new_digest)
            if new_digest != last_seen.get(filename):
                tampered_at[filename] = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            last_seen[filename] = new_digest
            # hashes[filename] = new_digest
            
def check_for_deletions(hashes):
    for filename in list(hashes.keys()):
        if not os.path.exists(os.path.join(TESTS_DIR, filename)):
            print("[!! DELETED !!]", filename, "is missing")
            del hashes[filename]

def baseline():
    hashes = {}
    for filename in txt_files():
        digest = sha256_of_file(os.path.join(TESTS_DIR, filename))
        hashes[filename] = digest
        print("baseline", filename, "->", digest)
    return hashes
if __name__ == "__main__":
    setup_db()
    tampered_at = {}
    hashes = baseline()
    last_seen = dict(hashes)
    try:
        while True:
            time.sleep(INTERVAL)
            check_for_changes(hashes, tampered_at, last_seen)
            check_for_deletions(hashes)
            save_hashes(hashes, tampered_at)
    except KeyboardInterrupt:
        print("\nExiting...")

