import sys
from typing import Optional

from database import get_connection
from models import Drama
from tmdb.drama_api import fetch_drama


def insert_drama(drama: Drama) -> Optional[str]:
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        cur.execute("""
            INSERT INTO dramas (
                tmdb_id, content_type, original_country,
                original_language, first_air_date, air_status,
                total_episodes, synopsis, tmdb_popularity_score,
                tmdb_vote_average, tmdb_vote_count
            ) VALUES (
                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s
            )
            ON CONFLICT (tmdb_id) DO UPDATE SET
                content_type = EXCLUDED.content_type,
                original_country = EXCLUDED.original_country,
                original_language = EXCLUDED.original_language,
                first_air_date = EXCLUDED.first_air_date,
                air_status = EXCLUDED.air_status,
                total_episodes = EXCLUDED.total_episodes,
                synopsis = EXCLUDED.synopsis,
                tmdb_popularity_score = EXCLUDED.tmdb_popularity_score,
                tmdb_vote_average = EXCLUDED.tmdb_vote_average,
                tmdb_vote_count = EXCLUDED.tmdb_vote_count,
                updated_at = NOW()
            RETURNING drama_id
        """, (
            drama.tmdb_id,
            drama.content_type,
            drama.original_country,
            drama.original_language,
            drama.first_air_date,
            drama.air_status,
            drama.total_episodes,
            drama.synopsis,
            drama.tmdb_popularity,
            drama.tmdb_vote_average,
            drama.tmdb_vote_count
        ))
        
        result = cur.fetchone()
        if not result:
            raise Exception("Failed to insert drama")
        
        drama_id = result[0]
        
        cur.execute(
            "DELETE FROM drama_titles WHERE drama_id = %s",
            (drama_id,)
        )
        
        for title in drama.titles:
            cur.execute("""
                INSERT INTO drama_titles (
                    drama_id, title_type, language_code,
                    title, is_primary
                ) VALUES (%s, %s, %s, %s, %s)
            """, (
                drama_id,
                title.title_type,
                title.language_code,
                title.title,
                title.is_primary
            ))
        
        conn.commit()
        cur.close()
        
        print(f"inserted/updated: {drama.titles[0].title if drama.titles else 'Unknown'} (ID: {drama_id})")
        return str(drama_id)
        
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
        drama = fetch_drama(127358)
        drama_id = insert_drama(drama)
        print(f"success: drama_id = {drama_id}")
    except Exception as e:
        print(f"failed: {e}")
        sys.exit(1)