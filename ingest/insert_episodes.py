from database import get_connection
from tmdb.drama_api import fetch_episodes


def insert_episodes(drama_id: str, tmdb_id: int, season_number: int = 1) -> None:
    episodes = fetch_episodes(tmdb_id, season_number)
    
    if not episodes:
        print(f"no episodes found for season {season_number}")
        return
    
    conn = None
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        for ep in episodes:
            cur.execute("""
                INSERT INTO episodes (
                    drama_id, season_number, episode_number,
                    title, synopsis, air_date, runtime,
                    tmdb_rating, tmdb_vote_count, still_image_path
                ) VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                ON CONFLICT (drama_id, season_number, episode_number) DO UPDATE SET
                    title = EXCLUDED.title,
                    synopsis = EXCLUDED.synopsis,
                    air_date = EXCLUDED.air_date,
                    runtime = EXCLUDED.runtime,
                    tmdb_rating = EXCLUDED.tmdb_rating,
                    tmdb_vote_count = EXCLUDED.tmdb_vote_count,
                    still_image_path = EXCLUDED.still_image_path
            """, (
                drama_id,
                season_number,
                ep.get("episode_number"),
                ep.get("name"),
                ep.get("overview"),
                ep.get("air_date"),
                ep.get("runtime"),
                ep.get("vote_average"),
                ep.get("vote_count"),
                ep.get("still_path")
            ))
        
        conn.commit()
        cur.close()
        print(f"inserted {len(episodes)} episodes for season {season_number}")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"episode insert error: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    from ingest import insert_drama
    from tmdb.drama_api import fetch_drama
    
    # The Veil
    drama = fetch_drama(127358)
    drama_id = insert_drama(drama)
    
    print(f"\ninserting episodes for drama {drama_id}...")
    insert_episodes(drama_id, 127358, season_number=1)
    
    print("\nfinished")