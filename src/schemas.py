from pydantic import BaseModel


class SongInsert(BaseModel):
    title: str
    hymn_number: int
    misc: str


class SongRead(BaseModel):
    id: int
    title: str
    hymn_number: int
    misc: str

    class Config:
        from_attributes = True