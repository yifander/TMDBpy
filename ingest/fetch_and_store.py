
import sys

from tmdb.drama_api import fetch_drama, fetch_credits, get_season_count
from ingest.insert_drama import insert_drama
from ingest.insert_credits import insert_cast, insert_crew
from ingest.insert_episodes import insert_all_episodes
from ingest.insert_providers import insert_providers

# acts as the single script pipeline for data ingestion
# python -m ingest.fetch_and_store <tmdb_id>
# todo support for person

def run(tmdb_id: int):
    print(f"fetching and storing drama {tmdb_id}...")
    
    drama = fetch_drama(tmdb_id)
    drama_id = insert_drama(drama)
    print(f"drama: {drama.titles[0].title}")
    
    credits = fetch_credits(tmdb_id)
    insert_cast(drama_id, credits["cast"])
    insert_crew(drama_id, credits["crew"])
    
    seasons = get_season_count(tmdb_id)
    insert_all_episodes(drama_id, tmdb_id, seasons)
    
    insert_providers(drama_id, tmdb_id)
    
    print("finished")


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python -m ingest.fetch_and_store <tmdb_id>")
        sys.exit(1)
    
    run(int(sys.argv[1]))