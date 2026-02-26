from typing import Dict, List

from database import get_connection
from tmdb.drama_api import fetch_providers


def insert_providers(drama_id: str, tmdb_id: int) -> None:
    providers_by_country = fetch_providers(tmdb_id)
    
    if not providers_by_country:
        print("no watch providers found")
        return
    
    conn = None
    inserted = 0
    
    try:
        conn = get_connection()
        cur = conn.cursor()
        
        for country_code, country_data in providers_by_country.items():
            flat_providers: List[Dict] = []
            
            for provider_type in ["flatrate", "rent", "buy", "free", "ads"]:
                type_list = country_data.get(provider_type, [])
                for provider in type_list:
                    provider["type"] = {
                        "flatrate": "subscription",
                        "rent": "rent",
                        "buy": "buy",
                        "free": "free",
                        "ads": "ads"
                    }.get(provider_type, "unknown")
                    flat_providers.append(provider)
            
            for provider in flat_providers:
                cur.execute("""
                    INSERT INTO watch_providers (
                        drama_id, country_code, service_name,
                        provider_type, link_url, logo_path, display_priority
                    ) VALUES (%s, %s, %s, %s, %s, %s, %s)
                    ON CONFLICT (drama_id, country_code, service_name, provider_type) DO UPDATE SET
                        link_url = EXCLUDED.link_url,
                        logo_path = EXCLUDED.logo_path,
                        display_priority = EXCLUDED.display_priority,
                        updated_at = NOW()
                """, (
                    drama_id,
                    country_code,
                    provider.get("provider_name"),
                    provider.get("type"),
                    country_data.get("link"),
                    provider.get("logo_path"),
                    provider.get("display_priority")
                ))
                inserted += 1
        
        conn.commit()
        cur.close()
        print(f"inserted {inserted} provider entries across {len(providers_by_country)} countries")
        
    except Exception as e:
        if conn:
            conn.rollback()
        print(f"provider insert error: {e}")
        raise
    finally:
        if conn:
            conn.close()


if __name__ == "__main__":
    from ingest import insert_drama
    from tmdb.drama_api import fetch_drama
    
    # The Veil
    TEST_DRAMA_ID = 127358
    
    drama = fetch_drama(TEST_DRAMA_ID)
    drama_id = insert_drama(drama)
    
    print(f"\nfetching providers for drama {drama_id}...")
    insert_providers(drama_id, TEST_DRAMA_ID)
    
    print("\nfinished")