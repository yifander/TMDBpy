import sys
from typing import Optional

from database import get_connection
from models import Person
from tmdb.person_api import fetch_person

def insert_person(person: Person) -> Optional[str]:
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO people (
                tmdb_id, gender, birth_date, death_date,
                biography, place_of_birth, tmdb_popularity
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tmdb_id) DO UPDATE SET
                gender = EXCLUDED.gender,
                birth_date = EXCLUDED.birth_date,
                death_date = EXCLUDED.death_date,
                biography = EXCLUDED.biography,
                place_of_birth = EXCLUDED.place_of_birth,
                tmdb_popularity = EXCLUDED.tmdb_popularity,
                updated_at = NOW()
            RETURNING person_id
        """, (
            person.tmdb_id,
            person.gender,
            person.birth_date,
            person.death_date,
            person.biography,
            person.place_of_birth,
            person.tmdb_popularity
        ))
        
        result = cur.fetchone()
        if not result:
            raise Exception("failed to insert person")
        
        person_id = result[0]
        
        cur.execute(
            "DELETE FROM person_names WHERE person_id = %s",
            (person_id,)
        )
        
        for name in person.names:
            cur.execute("""
                INSERT INTO person_names (
                    person_id, name_type, language_code,
                    name, is_primary
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                person_id,
                name.name_type,
                name.language_code,
                name.name,
                name.is_primary
            ))
        
        conn.commit()
        cur.close()
        
        print(f"inserted/updated: {person.names[0].name if person.names else 'Unknown'} (ID: {person_id})")
        return str(person_id)
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"db error: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    try:
        person = fetch_person(1239247)  # Namkoong Min (남궁민)
        person_id = insert_person(person)
        print(f"success: person_id = {person_id}")
    except Exception as e:
        print(f"failed: {e}")
        sys.exit(1)