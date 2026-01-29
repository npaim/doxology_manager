from src.db.base import engine, Base, SessionLocal
from src.db import models

from src.db.crud import insert_song, get_all_songs

def main():
    Base.metadata.create_all(bind=engine)

    db = SessionLocal()

    try:
        print("Inserting song...")
        insert_song(db, title="SANTO, SANTO, SANTO!", hymn_number=1, misc="HASD")

        print("Querying songs...")
        songs = get_all_songs(db)

        for song in songs:
            print(f"{song.id}: {song.hymn_number} -- {song.title}")

    finally:
        db.close()


if __name__ == "__main__":
    main()