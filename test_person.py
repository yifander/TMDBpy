import os
import sys

import requests
from dotenv import load_dotenv

from models.person_model import Person

load_dotenv()

def get_api_key() -> str:
    key = os.getenv("TMDB_API_KEY")
    if not key:
        print("error: api key not valid or missing")
        sys.exit(1)
    return key

def fetch_person(tmdb_person_id: int) -> Person:
    key = get_api_key()
    url = f"https://api.themoviedb.org/3/person/{tmdb_person_id}"

    response = requests.get(
        url,
        params={"api_key": key, "language": "en-US"},
        timeout=10
    )

    if response.status_code != 200:
        print(f"fail: {response.text}")
        sys.exit(1)
    
    person = Person.from_tmdb_response(response.json())
    return person

if __name__ == "__main__":
    # Namkoong Min (남궁민)
    TEST_PERSON_ID = 1239247
    
    person = fetch_person(TEST_PERSON_ID)
    
    print("--person model--")
    print(f"tmdb_id: {person.tmdb_id}")
    print(f"gender: {person.gender}")
    print(f"birth_date: {person.birth_date}")
    print(f"place_of_birth: {person.place_of_birth}")
    
    print(f"\n-- names ({len(person.names)}) --")
    for n in person.names:
        print(f"  [{n.name_type}] {n.name} ({n.language_code})")