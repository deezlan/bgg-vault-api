import csv
import sys
from app.database import SessionLocal, engine, Base
from app.models import Game

def clean_float(value: str) -> float | None:
    """Convert European decimal format (comma) to float."""
    if not value or value.strip() == "":
        return None
    try:
        return float(value.strip().replace(",", "."))
    except ValueError:
        return None

def clean_int(value: str) -> int | None:
    """Convert string to int, return None if invalid."""
    if not value or value.strip() == "":
        return None
    try:
        val = int(float(value.strip().replace(",", ".")))
        return val
    except ValueError:
        return None

def seed():
    # Create tables if they don't exist
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        # Check if already seeded
        existing = db.query(Game).count()
        if existing > 0:
            print(f"Database already contains {existing} games. Skipping seed.")
            return

        print("Seeding database from CSV...")

        inserted = 0
        skipped = 0

        with open("data/bgg_dataset.csv", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter=";")

            for row in reader:
                # Skip games with no name or clearly bad year data
                if not row.get("Name", "").strip():
                    skipped += 1
                    continue

                year = clean_int(row.get("Year Published", ""))
                if year is not None and (year < 1900 or year > 2025):
                    skipped += 1
                    continue

                game = Game(
                    bgg_id=clean_int(row.get("ID", "")),
                    title=row.get("Name", "").strip(),
                    year_published=year,
                    min_players=clean_int(row.get("Min Players", "")),
                    max_players=clean_int(row.get("Max Players", "")),
                    play_time=clean_int(row.get("Play Time", "")),
                    complexity=clean_float(row.get("Complexity Average", "")),
                    avg_rating=clean_float(row.get("Rating Average", "")),
                    mechanics=row.get("Mechanics", "").strip() or None,
                    categories=row.get("Domains", "").strip() or None,
                )

                db.add(game)
                inserted += 1

                # Commit in batches of 500 for performance
                if inserted % 500 == 0:
                    db.commit()
                    print(f"  {inserted} games inserted...")

        db.commit()
        print(f"\nDone! Inserted {inserted} games, skipped {skipped} rows.")

    except FileNotFoundError:
        print("ERROR: data/bgg_dataset.csv not found.")
        print("Download it from https://www.kaggle.com/datasets/andrewmvd/board-games")
        sys.exit(1)
    except Exception as e:
        db.rollback()
        print(f"ERROR: {e}")
        raise
    finally:
        db.close()

if __name__ == "__main__":
    seed()