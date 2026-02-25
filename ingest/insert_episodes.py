from database import get_connection
from tmdb.drama_api import fetch_episodes, get_season_count


def insert_episodes_for_season(
    drama_id: str, 
    tmdb_id: int, 
    season_number: int
) -> int:
    episodes = fetch_episodes(tmdb_id, season_number)
    
    if not episodes:
        print(f"  Season {season_number}: no episodes found")
        return 0
    
    conn = None
    inserted = 0
    
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
            inserted += 1
        
        conn.commit()
        cur.close()
        print(f"season {season_number}: {inserted} episodes")
        return inserted
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"season {season_number} error: {e}")
        raise
    finally:
        if conn:
            conn.close()


def insert_all_episodes(drama_id: str, tmdb_id: int, total_seasons: int) -> int:
    print(f"\ninserting episodes for {total_seasons} season(s)...")
    
    total = 0
    for season in range(1, total_seasons + 1):
        count = insert_episodes_for_season(drama_id, tmdb_id, season)
        total += count
    
    print(f"total: {total} episodes across {total_seasons} season(s)")
    return total


if __name__ == "__main__":
    from ingest import insert_drama
    from tmdb.drama_api import fetch_drama
    
    # Hospital Playlist (슬기로운 의사생활)
    # using this as an example since it has two seasons
    TEST_DRAMA_ID = 96102

    drama = fetch_drama(TEST_DRAMA_ID)
    drama_id = insert_drama(drama)

    total_seasons = get_season_count(TEST_DRAMA_ID)
    print(f"Seasons detected: {total_seasons}")

    insert_all_episodes(drama_id, TEST_DRAMA_ID, total_seasons)
    
    print("\nfinished")