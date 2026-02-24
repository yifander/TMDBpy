import os
import sys
from typing import Dict, Any, Optional

import requests
from dotenv import load_dotenv

load_dotenv()

class TMDBError(Exception):
    pass

def get_api_key() -> str:
    key = os.getenv("TMDB_API_KEY")
    if not key:
        raise TMDBError("api key is not correct")
    return key


def make_request(endpoint: str, params: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    base_url = "https://api.themoviedb.org/3"
    url = f"{base_url}/{endpoint}"
    
    request_params = params.copy() if params else {}
    request_params["api_key"] = get_api_key()
    
    try:
        response = requests.get(
            url,
            params=request_params,
            timeout=10
        )
        
        if response.status_code == 401:
            raise TMDBError("invalid api key")
        elif response.status_code == 404:
            raise TMDBError(f"not found: {endpoint}")
        elif response.status_code != 200:
            raise TMDBError(f"HTTP {response.status_code}: {response.text[:200]}")
        
        return response.json()
        
    except requests.exceptions.Timeout:
        raise TMDBError("request timed out")
    except requests.exceptions.RequestException as e:
        raise TMDBError(f"request failed: {e}")


if __name__ == "__main__":
    try:
        result = make_request("configuration")
        base_url = result.get("images", {}).get("secure_base_url")
        print(f"tmdb api ok")
        print(f"images base url: {base_url}")
    except TMDBError as e:
        print(f"failed: {e}")
        sys.exit(1)