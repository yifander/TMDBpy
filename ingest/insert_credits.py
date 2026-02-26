from database import get_connection
from tmdb.person_api import fetch_person


def insert_person_and_get_id(person_tmdb_id: int) -> str:
    person = fetch_person(person_tmdb_id)
    
    conn = get_connection()
    cur = conn.cursor()
    
    try:
        cur.execute("""
            INSERT INTO people (
                tmdb_id, gender, birth_date, death_date,
                biography, place_of_birth, tmdb_popularity
            ) VALUES (%s, %s, %s, %s, %s, %s, %s)
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
            person.tmdb_id, person.gender, person.birth_date,
            person.death_date, person.biography,
            person.place_of_birth, person.tmdb_popularity
        ))
        
        person_id = cur.fetchone()[0]
        
        cur.execute("DELETE FROM person_names WHERE person_id = %s", (person_id,))
        for name in person.names:
            cur.execute("""
                INSERT INTO person_names (person_id, name_type, language_code, name, is_primary)
                VALUES (%s, %s, %s, %s, %s)
            """, (person_id, name.name_type, name.language_code, name.name, name.is_primary))
        
        conn.commit()
        return str(person_id)
        
    finally:
        cur.close()
        conn.close()


def insert_cast(drama_id: str, cast_data: list) -> None:
    print("inserting cast...")
    
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    
    try:
        for i, member in enumerate(cast_data[:15]):
            person_tmdb_id = member.get("id")
            if not person_tmdb_id:
                continue
            
            try:
                person_id = insert_person_and_get_id(person_tmdb_id)
            except Exception as e:
                print(f"warning: failed person {person_tmdb_id}: {e}")
                continue
            
            cur.execute("""
                INSERT INTO drama_cast (
                    drama_id, person_id, character_name, order_index, is_main_cast
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (drama_id, person_id, character_name) DO NOTHING
            """, (
                drama_id, person_id,
                member.get("character"),
                member.get("order"),
                i < 5
            ))
            inserted += 1
        
        conn.commit()
        print(f"{inserted} cast members")
        
    finally:
        cur.close()
        conn.close()


def insert_crew(drama_id: str, crew_data: list) -> None:
    print("inserting crew...")
    
    key_jobs = {"Director", "Writer", "Screenplay", "Producer", "Executive Producer"}
    
    conn = get_connection()
    cur = conn.cursor()
    inserted = 0
    
    try:
        for member in crew_data:
            job = member.get("job")
            if job not in key_jobs:
                continue
            
            person_tmdb_id = member.get("id")
            if not person_tmdb_id:
                continue
            
            try:
                person_id = insert_person_and_get_id(person_tmdb_id)
            except Exception as e:
                print(f"warning: failed person {person_tmdb_id}: {e}")
                continue
            
            cur.execute("""
                INSERT INTO drama_crew (
                    drama_id, person_id, job, department, is_key_creator
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (drama_id, person_id, job) DO NOTHING
            """, (
                drama_id, person_id, job,
                member.get("department"),
                job in {"Director", "Writer"}
            ))
            inserted += 1
        
        conn.commit()
        print(f"  {inserted} crew members")
        
    finally:
        cur.close()
        conn.close()