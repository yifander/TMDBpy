from datetime import date
from typing import List, Optional

from pydantic import BaseModel

class PersonName(BaseModel):
    name_type: str
    language_code: str
    name: str
    is_primary: bool = False

class Person(BaseModel):
    tmdb_id: int
    gender: Optional[int] = None
    birth_date: Optional[date] = None
    death_date: Optional[date] = None
    biography: Optional[str] = None
    place_of_birth: Optional[str] = None
    names: List[PersonName] = []
    profile_path: Optional[str] = None
    tmdb_popularity: Optional[float] = None

    @classmethod
    def from_tmdb_response(cls, data: dict) -> "Person":
        names = []

        if data.get("name"):
            names.append(PersonName(
                name_type="original",
                language_code=data.get("original_language", "unknown"),
                name=data["name"],
                is_primary=True
            ))

        for aka in data.get("also_known_as", []):
            if aka and aka != data.get("name"):
                names.append(PersonName(
                    name_type="aka",
                    language_code="unknown",
                    name=aka,
                    is_primary=False
                ))
    
        return cls(
            tmdb_id=data["id"],
            gender=data.get("gender"),
            birth_date=data.get("birthday"),
            death_date=data.get("deathday"),
            biography=data.get("biography"),
            place_of_birth=data.get("place_of_birth"),
            names=names,
            profile_path=data.get("profile_path"),
            tmdb_popularity=data.get("popularity")
        )

    def to_db_dict(self) -> dict:
        return {
            "tmdb_id": self.tmdb_id,
            "gender": self.gender,
            "birth_date": self.birth_date,
            "death_date": self.death_date,
            "biography": self.biography,
            "place_of_birth": self.place_of_birth,
            "tmdb_popularity": self.tmdb_popularity
        }