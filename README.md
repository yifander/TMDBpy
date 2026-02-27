# TMDBpy

ETL pipeline for asian drama data: from TMDB to PostgreSQL

## Setup
```bash
python3 -m venv .venv
source .venv/bin/activate

pip install -r requirements.txt

psql -d tmdb_py -f database/schema.sql
```

## Usage
```bash
# for discovering upcoming dramas within the last 30 days
# use a region arg based on which dramas you want
# using no args will default to KR
# returns list of tmdb IDs in discovery_output.txt
python -m ingest.cli.discover --region CN

# for a single drama usage
# fetches and stores drama data, cast, crew, episodes, providers into postgres db
python -m ingest.cli.fetch_drama <tmdb_id>

# for batch insert usage
# takes the list of tmdb IDs from discovery_output.txt and fetches/stores all data in postgres db
# Processes each ID, skips if already in database
python -m ingest.cli.fetch_batch discovery_output.txt
```

## Database Schema

| Table             | Purpose                                       |
| ----------------- | --------------------------------------------- |
| `dramas`          | Core drama metadata                           |
| `drama_titles`    | Title variants (original, English, romanized) |
| `people`          | Cast and crew                                 |
| `person_names`    | Name variants                                 |
| `drama_cast`      | Actor-role relationships                      |
| `drama_crew`      | Director/writer credits                       |
| `episodes`        | Episode list with air dates                   |
| `watch_providers` | Streaming availability by country             |
