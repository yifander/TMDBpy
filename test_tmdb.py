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

def test_tmdb_connection() -> None:
    key = get_api_key()
    url = "https://api.themoviedb.org/3/configuration"

    response = requests.get(
        url,
        params={"api_key": key},
        timeout=10
    )

    # successful connection would be status 200 
    # and content length of ~1000 bytes
    print(f"Status: {response.status_code}")
    print(f"Content length: {len(response.text)} bytes")

if __name__ == "__main__":
    test_tmdb_connection()