from typing import List, Dict

from database import get_connection
from tmdb.drama_api import fetch_credits
from tmdb.person_api import fetch_person
from ingest import insert_person


def insert_cast(drama_id: str, cast_data: List[Dict]) -> None:
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        for i, member in enumerate(cast_data[:20]):
            person_tmdb_id = member.get("id")
            character = member.get("character")
            order = member.get("order")
            
            if not person_tmdb_id:
                continue
            
            try:
                person = fetch_person(person_tmdb_id)
                person_id = insert_person(person)
            except Exception as e:
                print(f"  Skipping person {person_tmdb_id}: {e}")
                continue
            
            cur.execute("""
                INSERT INTO drama_cast (
                    drama_id, person_id, character_name, 
                    order_index, is_main_cast
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (drama_id, person_id, character_name) DO NOTHING
            """, (
                drama_id,
                person_id,
                character,
                order,
                i < 5
            ))
        
        conn.commit()
        cur.close()
        print(f"inserted cast: {len(cast_data[:20])} members")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"cast insert error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def insert_crew(drama_id: str, crew_data: List[Dict]) -> None:
    key_jobs = {"Director", "Writer", "Screenplay", "Producer"}
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        for member in crew_data:
            job = member.get("job")
            if job not in key_jobs:
                continue
            
            person_tmdb_id = member.get("id")
            if not person_tmdb_id:
                continue
            
            try:
                person = fetch_person(person_tmdb_id)
                person_id = insert_person(person)
            except Exception as e:
                print(f"skipping crew {person_tmdb_id}: {e}")
                continue
            
            cur.execute("""
                INSERT INTO drama_crew (
                    drama_id, person_id, job, department, is_key_creator
                ) VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (drama_id, person_id, job) DO NOTHING
            """, (
                drama_id,
                person_id,
                job,
                member.get("department"),
                job in {"Director", "Writer"}
            ))
        
        conn.commit()
        cur.close()
        print(f"inserted crew: key jobs")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"crew insert error: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    from ingest import insert_drama
    from tmdb.drama_api import fetch_drama
    
    # The Veil as example yet again
    drama = fetch_drama(127358)
    drama_id = insert_drama(drama)
    
    print(f"\nfetching credits for drama {drama_id}...")
    credits = fetch_credits(127358)
    
    insert_cast(drama_id, credits.get("cast", []))
    insert_crew(drama_id, credits.get("crew", []))
    
    print("\ndone")