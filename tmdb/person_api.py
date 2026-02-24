from models import Person
from tmdb.client import make_request

def fetch_person(tmdb_person_id: int) -> Person:
    data = make_request(f"person/{tmdb_person_id}")
    return Person.from_tmdb_response(data)

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