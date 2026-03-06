import sys
import argparse

from database import get_connection
from ingest.cli.fetch_drama import run as fetch_and_store


def drama_exists(tmdb_id: str) -> bool:
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("SELECT 1 FROM dramas WHERE tmdb_id = %s LIMIT 1", (tmdb_id,))
        return cur.fetchone() is not None
    finally:
        cur.close()
        conn.close()


def batch_process(filepath: str) -> None:
    try:
        with open(filepath) as f:
            ids = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"file not found: {filepath}")
        sys.exit(1)
    
    print(f"processing {len(ids)} drama(s) from {filepath}")
    print("skip existing: enabled\n")
    
    success = 0
    failed = 0
    skipped = 0
    
    for i, tmdb_id in enumerate(ids, 1):
        if drama_exists(tmdb_id):
            print(f"[{i}/{len(ids)}] {tmdb_id}: skipped (exists)")
            skipped += 1
            continue
        
        print(f"[{i}/{len(ids)}] processing {tmdb_id}...")
        
        try:
            fetch_and_store(int(tmdb_id))
            success += 1
            print(f"success\n")
        except Exception as e:
            failed += 1
            print(f"failed: {e}\n")
            continue
    
    print(f"{'='*40}")
    print(f"complete: {success} success, {skipped} skipped, {failed} failed")
    print(f"{'='*40}")


def main():
    parser = argparse.ArgumentParser(description="batch ingest dramas from file")
    parser.add_argument("file", help="file containing TMDB IDs (one per line)")
    
    args = parser.parse_args()
    
    batch_process(args.file)


if __name__ == "__main__":
    main()