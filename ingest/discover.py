import argparse
from datetime import datetime, timedelta
from typing import Dict, List

from tmdb.client import make_request

# discover tool returns a list of new drama tmdb IDs in the discovery_output.txt file
# syntax for using is python -m ingest.discover
# or specify by region code
# python -m ingest.discover --region CN 

def discover_upcoming(region: str, page: int) -> List[Dict]:
    today = datetime.now().strftime("%Y-%m-%d")
    future = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
    
    results = make_request("discover/tv", params={
        "with_origin_country": region,
        "first_air_date.gte": today,
        "first_air_date.lte": future,
        "sort_by": "popularity.desc",
        "page": page
    })

    return results.get("results", [])

def display_dramas(dramas: List[Dict]) -> None:
    if not dramas:
        print("no upcoming dramas found")
        return
    
    print(f"\nfound {len(dramas)} upcoming drama(s):\n")

    for i, drama in enumerate(dramas, 1):
        name = drama.get("name", "Unknown")
        original = drama.get("original_name", "")
        date = drama.get("first_air_date", "TBA")

        display = f"{name}"
        if original and original != name:
            display += f" ({original})"
        
        print(f"{i}. {display}")
        print(f"Air date: {date}")
        print(f"TMDB ID: {drama.get('id')}")
        print()

def save_ids(dramas: List[Dict], filepath: str) -> None:
    ids = [str(d["id"]) for d in dramas]

    with open(filepath, "w") as f:
        f.write("\n".join(ids))

    print(f"wrote {len(ids)} IDs to {filepath}")

def main():
    parser = argparse.ArgumentParser(description="discover upcoming dramas")
    parser.add_argument("--region", default="KR", help="country code (KR, CN, JP, etc.)")
    parser.add_argument("--pages", type=int, default=1, help="pages to fetch")

    args = parser.parse_args()

    print(f"discovering {args.region} dramas in next 30 days...")

    all_dramas = []
    for page in range(1, args.pages + 1):
        print(f"fetching page {page}...")
        dramas = discover_upcoming(args.region, page)
        all_dramas.extend(dramas)
    
    print(f"\ntotal found: {len(all_dramas)} drama(s)")

    display_dramas(all_dramas)
    save_ids(all_dramas, "discovery_output.txt")

if __name__ == "__main__":
    main()