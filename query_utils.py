from models import SessionLocal, Movie, MovieSchedule, ShowDate
from datetime import date

def get_movies_showing_today():
    db = SessionLocal()
    today = date.today()
    results = (
        db.query(Movie)
        .join(MovieSchedule)
        .join(ShowDate)
        .filter(ShowDate.show_date == today)
        .distinct()
        .all()
    )
    db.close()
    return results
