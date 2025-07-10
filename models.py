from sqlalchemy import create_engine, Column, Integer, String, Date, ForeignKey, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

DATABASE_URL = "postgresql://movietheater_user:DpqonU3tkphMU0Y160g3VZpXyDZOoyff@d1m7efm3jp1c73edteo0-a.singapore-postgres.render.com:5432/movietheater"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(bind=engine)
Base = declarative_base()


class Movie(Base):
    __tablename__ = "movietheater_movie"
    movie_id = Column(String, primary_key=True)
    movie_name_vn = Column(String)
    director = Column(String)
    content = Column(String)
    actor = Column(String)
    duration = Column(Integer)
    from_date = Column(Date)
    to_date = Column(Date)
    trailer_id = Column(String)
    rating = Column(Integer)

    schedules = relationship("MovieSchedule", back_populates="movie")


class ShowDate(Base):
    __tablename__ = "movietheater_show_dates"
    show_date_id = Column(Integer, primary_key=True)
    show_date = Column(Date)
    date_name = Column(String)


class Schedule(Base):
    __tablename__ = "movietheater_schedule"
    schedule_id = Column(Integer, primary_key=True)
    schedule_time = Column(String)


class MovieSchedule(Base):
    __tablename__ = "movietheater_movie_schedule"
    id = Column(Integer, primary_key=True, autoincrement=True)
    movie_id = Column(String, ForeignKey("movietheater_movie.movie_id"))
    show_date_id = Column(Integer, ForeignKey("movietheater_show_dates.show_date_id"))
    schedule_id = Column(Integer, ForeignKey("movietheater_schedule.schedule_id"))
    cinema_room_id = Column(Integer)

    movie = relationship("Movie", back_populates="schedules")
    show_date = relationship("ShowDate")
    schedule = relationship("Schedule")
