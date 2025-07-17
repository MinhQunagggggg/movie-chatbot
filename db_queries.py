import psycopg2
import re
from datetime import datetime
import pytz
from utils import clean_text, parse_date

def connect_db():
    return psycopg2.connect(
        host="d1m7efm3jp1c73edteo0-a.singapore-postgres.render.com",
        port="5432",
        dbname="movietheater",
        user="movietheater_user",
        password="DpqonU3tkphMU0Y160g3VZpXyDZOoyff"
    )

def load_movies_data():
    conn = connect_db()
    cur = conn.cursor()
    cur.execute("""
        SELECT movie_id, movie_name_vn, director, content, actor, duration, from_date, to_date, trailer_id, rating
        FROM movietheater_movie
    """)
    rows = cur.fetchall()
    columns = [desc[0] for desc in cur.description]
    data = [dict(zip(columns, row)) for row in rows]

    for m in data:
        m["vn_clean"] = clean_text(m.get("movie_name_vn", ""))
        m["dir_clean"] = clean_text(m.get("director", ""))
        m["content_clean"] = clean_text(m.get("content", ""))
        raw_actors = re.split(r"[;,]", m.get("actor", "") or "")
        m["actors_clean"] = [clean_text(actor) for actor in raw_actors if clean_text(actor)]
        m["from_date_dt"] = parse_date(m.get("from_date"))
        m["to_date_dt"] = parse_date(m.get("to_date"))

    cur.close()
    conn.close()
    return data

def get_movies_showing_today():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT DISTINCT m.movie_name_vn
            FROM movietheater_movie m
            JOIN movietheater_movie_schedule ms ON m.movie_id = ms.movie_id
            JOIN movietheater_show_dates sd ON ms.show_date_id = sd.show_date_id
            WHERE sd.show_date = CURRENT_DATE
        """)
        movies = [row[0] for row in cur.fetchall()]
        return movies if movies else []
    except:
        return []
    finally:
        cur.close()
        conn.close()

def get_multiple_nearest_showtimes():
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT 
                m.movie_name_vn, sd.show_date, s.schedule_time, ms.cinema_room_id
            FROM 
                movietheater_movie m
            JOIN 
                movietheater_movie_schedule ms ON m.movie_id = ms.movie_id
            JOIN 
                movietheater_show_dates sd ON ms.show_date_id = sd.show_date_id
            JOIN 
                movietheater_schedule s ON ms.schedule_id = s.schedule_id
            WHERE 
                sd.show_date = CURRENT_DATE
            ORDER BY 
                m.movie_name_vn, TO_TIMESTAMP(TRIM(s.schedule_time), 'HH24:MI')::time ASC
        """)
        rows = cur.fetchall()
        result = []
        now = datetime.now(pytz.timezone("Asia/Ho_Chi_Minh")).time()
        seen_movies = set()

        for movie_name, show_date, show_time_str, room in rows:
            if movie_name in seen_movies:
                continue
            try:
                show_time = datetime.strptime(show_time_str.strip(), "%H:%M").time()
                if show_time <= now:
                    continue
                show_date = datetime.strptime(str(show_date), "%Y-%m-%d").date()
                formatted = f"🎬 {movie_name} - 🕒 {show_time.strftime('%H:%M')} 📅 {show_date.strftime('%d/%m/%Y')}"
                result.append(formatted)
                seen_movies.add(movie_name)
                if len(result) >= 5:
                    break
            except:
                continue

        return "Các suất chiếu sắp tới hôm nay:\n" + "\n".join(result) if result else "❌ Không có suất chiếu sắp tới hôm nay."
    except Exception as e:
        return f"⚠️ Lỗi: {str(e)}"
    finally:
        cur.close()
        conn.close()

def get_nearest_showtime_for(movie_name: str):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.movie_name_vn, sd.show_date, s.schedule_time, ms.cinema_room_id
            FROM movietheater_movie m
            JOIN movietheater_movie_schedule ms ON m.movie_id = ms.movie_id
            JOIN movietheater_show_dates sd ON ms.show_date_id = sd.show_date_id
            JOIN movietheater_schedule s ON ms.schedule_id = s.schedule_id
            WHERE unaccent(lower(m.movie_name_vn)) ILIKE unaccent(%s)
              AND sd.show_date = CURRENT_DATE
            ORDER BY TO_TIMESTAMP(TRIM(s.schedule_time), 'HH24:MI')::time ASC
        """, (f"%{movie_name.lower()}%",))
        rows = cur.fetchall()
        now = datetime.now().time()
        result = []

        for row in rows:
            name, date_obj, time_str, room = row
            time_obj = datetime.strptime(time_str.strip(), "%H:%M").time()
            if time_obj <= now:
                continue
            date_obj = datetime.strptime(str(date_obj), "%Y-%m-%d").date()
            formatted = f"🎬 {name} - 🕒 {time_obj.strftime('%H:%M')} 📅 {date_obj.strftime('%d/%m/%Y')}"
            result.append(formatted)
            if len(result) >= 2:
                break

        return result if result else [f"❌ Không có suất chiếu gần nhất hôm nay cho phim '{movie_name}'."]
    except Exception as e:
        return [f"⚠️ Lỗi: {str(e)}"]
    finally:
        cur.close()
        conn.close()

def get_showtime_today_for(movie_name: str):
    try:
        conn = connect_db()
        cur = conn.cursor()
        cur.execute("""
            SELECT m.movie_name_vn, sd.show_date, s.schedule_time, ms.cinema_room_id
            FROM movietheater_movie m
            JOIN movietheater_movie_schedule ms ON m.movie_id = ms.movie_id
            JOIN movietheater_show_dates sd ON ms.show_date_id = sd.show_date_id
            JOIN movietheater_schedule s ON ms.schedule_id = s.schedule_id
            WHERE unaccent(lower(m.movie_name_vn)) ILIKE unaccent(%s)
              AND sd.show_date = CURRENT_DATE
            ORDER BY TO_TIMESTAMP(s.schedule_time, 'HH24:MI')::time ASC
        """, (f"%{movie_name.lower()}%",))
        rows = cur.fetchall()
        if not rows:
            return f"Không có lịch chiếu hôm nay cho phim {movie_name}."
        showtimes = [f"{r[2]} (Phòng {r[3]})" for r in rows]
        return f"Lịch chiếu hôm nay cho **{rows[0][0]}**:\n" + "\n".join(f"🕒 {t}" for t in showtimes)
    except Exception as e:
        return f"⚠️ Có lỗi xảy ra khi truy vấn lịch chiếu: {str(e)}"
    finally:
        cur.close()
        conn.close()
def get_movies_by_genre_today(genre_keyword: str):
    try:
        conn = connect_db()
        cur = conn.cursor()
        query = """
            SELECT DISTINCT m.movie_name_vn
            FROM movietheater_movie m
            JOIN movietheater_movie_schedule ms ON m.movie_id = ms.movie_id
            JOIN movietheater_show_dates sd ON ms.show_date_id = sd.show_date_id
            JOIN movietheater_movie_type mt ON m.movie_id = mt.movie_id
            JOIN movietheater_type t ON mt.type_id = t.type_id
            WHERE sd.show_date = CURRENT_DATE
              AND unaccent(lower(t.type_name)) ILIKE unaccent(%s)
        """
        cur.execute(query, (f"%{genre_keyword.lower()}%",))
        results = cur.fetchall()
        return [r[0] for r in results]
    except Exception as e:
        return [f"⚠️ Lỗi khi truy vấn thể loại: {str(e)}"]
    finally:
        cur.close()
        conn.close()
