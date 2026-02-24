-- create database tmdb_py;

create EXTENSION if not exists "uuid-ossp";

create table if not exists dramas (
    drama_id UUID primary key default uuid_generate_v4(),
    tmdb_id integer unique,
    content_type varchar(20) not null default 'series',
    original_country varchar(2) not null,
    original_language varchar(5) not null,
    first_air_date date,
    air_status varchar(20) not null default 'unknown',
    total_episodes smallint,
    synopsis text,
    tmdb_popularity_score decimal(10,3),
    tmdb_vote_average decimal(3,1),
    tmdb_vote_count integer,
    created_at timestamptz default now(),
    updated_at timestamptz default now(),

    constraint chk_content_type check (content_type in ('series', 'special', 'movie')),
    constraint chk_air_status check (air_status in ('unknown', 'upcoming', 'ongoing', 'hiatus', 'ended'))
);

create table if not exists drama_titles (
    title_id UUID primary key default uuid_generate_v4(),
    drama_id UUID not null references dramas(drama_id) on delete cascade,
    title_type varchar(20) not null,
    language_code varchar(10) not null,
    title text not null,
    is_primary boolean default FALSE,
    created_at timestamptz default now(),
    
    constraint chk_title_type check (title_type in ('original', 'english', 'romanized', 'aka', 'synonym')),
    unique(drama_id, title_type, language_code, title)
);

create table if not exists people (
    person_id UUID primary key default uuid_generate_v4(),
    tmdb_id integer unique,
    gender integer,
    birth_date date,
    death_date date,
    biography text,
    place_of_birth text,
    tmdb_popularity decimal(10,3),
    created_at timestamptz default now(),
    updated_at timestamptz default now()
);

create table if not exists person_names (
    name_id UUID primary key default uuid_generate_v4(),
    person_id UUID not null references people(person_id) on delete cascade,
    name_type varchar(20) not null,
    language_code varchar(10) not null,
    name text not null,
    is_primary boolean default FALSE,
    created_at timestamptz default now(),

    constraint chk_name_type check (name_type in ('original', 'english', 'romanized', 'aka')),
    UNIQUE(person_id, name_type, language_code, name)
);

create table if not exists drama_cast (
    cast_id UUID primary key default uuid_generate_v4(),
    drama_id UUID not null references dramas(drama_id) on delete cascade,
    person_id UUID not null references people(person_id) on delete cascade,
    character_name text,
    order_index smallint,
    is_main_cast boolean default FALSE,
    created_at timestamptz default now(),
    unique(drama_id, person_id, character_name)
);

create table if not exists drama_crew (
    crew_id UUID primary key default uuid_generate_v4(),
    drama_id UUID not null references dramas(drama_id) on delete cascade,
    person_id UUID not null references people(person_id) on delete cascade,
    job varchar(100) not null,
    department varchar(50),
    is_key_creator boolean default FALSE,
    created_at timestamptz default now(),
    unique(drama_id, person_id, job)
);

create table if not exists episodes (
    episode_id UUID primary key default uuid_generate_v4(),
    drama_id UUID not null references dramas(drama_id) on delete cascade,
    season_number smallint not null default 1,
    episode_number smallint not null,
    title text,
    synopsis text,
    air_date date,
    runtime integer,
    tmdb_rating decimal(3,1),
    tmdb_vote_count integer,
    still_image_path text,
    created_at timestamptz default now(),
    
    unique(drama_id, season_number, episode_number)
);