import os
import sys
from dotenv import load_dotenv
import requests

load_dotenv()

def get_api_key() -> str:
    key = os.getenv("TMDB_API_KEY")
    if not key:
        print("Error: api key not included in env")
        sys.exit(1)
    return key

def fetch_drama(tmdb_id: int) -> None:
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
    
    data = response.json()

    print(f"-- drama details --")
    print(f"tmdb id: {data.get('id')}")
    print(f"name: {data.get('name')}")
    print(f"original name: {data.get('original_name')}")
    print(f"original lang: {data.get('original_language')}")
    print(f"country: {data.get('origin_country')}")
    print(f"episode count: {data.get('number_of_episodes')}")
    print(f"description: {data.get('overview', '')[:200]}...")
    print(f"genres: {[g['name'] for g in data.get('genres', [])]}")
    

if __name__ == "__main__":
    # 127358 is ID for The Veil (검은 태양)
    fetch_drama(127358)