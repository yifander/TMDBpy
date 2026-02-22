import os
import sys
from dotenv import load_dotenv
import requests

from models.drama_model import Drama

load_dotenv()

def get_api_key() -> str:
    key = os.getenv("TMDB_API_KEY")
    if not key:
        print("Error: api key not included in env")
        sys.exit(1)
    return key

def fetch_drama(tmdb_id: int) -> Drama:
    key = get_api_key()
    url = f"https://api.themoviedb.org/3/tv/{tmdb_id}"

    response = requests.get(
        url,
        params={
            "api_key": key,
            "language": 'en-US'
        },
        timeout=10
    )

    # successful connection would be status 200 
    if response.status_code != 200:
        print(f"failed response: {response.text}")
        return
    
    drama = Drama.from_tmdb_response(response.json())
    return drama
    

if __name__ == "__main__":
    # 127358 is ID for The Veil (검은 태양)
    drama = fetch_drama(127358)

    print("-- Drama Model --")
    print(f"tmdb_id: {drama.tmdb_id}")
    print(f"country: {drama.original_country}")
    print(f"language: {drama.original_language}")
    print(f"episodes: {drama.total_episodes}")
    print(f"air_status: {drama.air_status}")
    
    print(f"\n-- Titles ({len(drama.titles)}) --")
    for t in drama.titles:
        print(f"  [{t.title_type}] {t.title} ({t.language_code})")