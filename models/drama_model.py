from datetime import date
from typing import List, Optional

from pydantic import BaseModel, field_validator

class DramaTitle(BaseModel):
    title_type: str
    language_code: str
    title: str
    is_primary: bool = False

class Genre(BaseModel):
    id: int
    name: str

class Drama(BaseModel):
    tmdb_id: int
    content_type: str = "series"
    original_country: str
    original_language: str
    first_air_date: Optional[date] = None
    air_status: str = "unknown"
    total_episodes: Optional[int] = None
    total_seasons: Optional[int] = None
    synopsis: Optional[str] = None
    titles: List[DramaTitle] = []
    genres: List[Genre] = []
    poster_path: Optional[str] = None
    backdrop_path: Optional[str] = None
    tmdb_popularity: Optional[float] = None
    tmdb_vote_average: Optional[float] = None
    tmdb_vote_count: Optional[int] = None

    @field_validator("content_type")
    @classmethod
    def validate_drama_type(cls, v: str) -> str:
        valid_type = {"series", "special", "movie"}
        if v not in valid_type:
            raise ValueError(f"drama type is invalid")
        return v

    @field_validator("air_status")
    @classmethod
    def validate_air_status(cls, v: str) -> str:
        valid_status = {"unknown", "upcoming", "ongoing", "hiatus", "ended"}
        if v not in valid_status:
            raise ValueError(f"air status is not valid")
        return v

    @classmethod
    def from_tmdb_response(cls, data: dict) -> "Drama":
        titles = []

        if data.get("original_name"):
            titles.append(DramaTitle(
                title_type="original",
                language_code=data.get("original_language", "unknown"),
                title=data["original_name"],
                is_primary=True
            ))

        if data.get("name"):
            titles.append(DramaTitle(
                title_type="english",
                language_code="en",
                title=data["name"],
                is_primary=False
            ))
    
        countries = data.get("origin_country", [])
        country = countries[0] if countries else "unknown"

        status_map = {
            "Returning Series": "ongoing",
            "Planned": "upcoming",
            "In Production": "upcoming",
            "Ended": "ended",
            "Canceled": "ended",
            "Pilot": "unknown"
        }
        air_status = status_map.get(data.get("status"), "unknown")

        genres = [Genre(id=g["id"], name=g["name"]) for g in data.get("genres", [])]

        return cls(
            tmdb_id=data["id"],
            content_type="series",
            original_country=country,
            original_language=data.get("original_language", "unknown"),
            first_air_date=data.get("first_air_date"),
            air_status=air_status,
            total_episodes=data.get("number_of_episodes"),
            total_seasons=data.get("number_of_seasons"),
            synopsis=data.get("overview"),
            titles=titles,
            genres=genres,
            poster_path=data.get("poster_path"),
            backdrop_path=data.get("backdrop_path"),
            tmdb_popularity=data.get("popularity"),
            tmdb_vote_average=data.get("vote_average"),
            tmdb_vote_count=data.get("vote_count")
        )

    def to_db_dict(self) -> dict:
        return {
            "tmdb_id": self.tmdb_id,
            "content_type": self.content_type,
            "original_country": self.original_country,
            "original_language": self.original_language,
            "first_air_date": self.first_air_date,
            "air_status": self.air_status,
            "total_episodes": self.total_episodes,
            "number_of_seasons": self.total_seasons,
            "synopsis": self.synopsis,
            "tmdb_popularity_score": self.tmdb_popularity,
            "tmdb_vote_average": self.tmdb_vote_average,
            "tmdb_vote_count": self.tmdb_vote_count
        }