from typing import Dict, List
from models import Drama
from tmdb.client import make_request

def fetch_drama(tmdb_id: int) -> Drama:
    data = make_request(f"tv/{tmdb_id}", params={"language": "en-US"})
    return Drama.from_tmdb_response(data)
    
def fetch_credits(tmdb_id: int) -> dict:
    return make_request(f"tv/{tmdb_id}/credits")

def fetch_episodes(tmdb_id: int, season_number: int = 1) -> List[Dict]:
    data = make_request(f"tv/{tmdb_id}/season/{season_number}")
    return data.get("episodes", [])

def fetch_providers(tmdb_id: int) -> Dict[str, List[Dict]]:
    data = make_request(f"tv/{tmdb_id}/watch/providers")
    return data.get("results", {})

def get_season_count(tmdb_id: int) -> int:
    data = make_request(f"tv/{tmdb_id}")
    seasons = data.get("seasons", [])
    
    valid_seasons = [
        s for s in seasons 
        if s.get("season_number", 0) > 0 
        and "special" not in s.get("name", "").lower()
    ]
    
    return len(valid_seasons)

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