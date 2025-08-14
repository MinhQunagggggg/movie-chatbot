from datetime import datetime
from utils import clean_text, detect_intent, extract_movie_name, fuzzy_find_movie_name
from db_queries import (
    load_movies_data, get_movies_showing_today, get_multiple_nearest_showtimes,
    get_nearest_showtime_for, get_showtime_today_for, get_movies_by_genre_today
)

_movies_cache = None  # Bộ nhớ đệm cục bộ

def get_movies():
    global _movies_cache
    if _movies_cache is None:
        try:
            _movies_cache = load_movies_data()
        except Exception as e:
            print(f"⚠️ Không thể load dữ liệu phim: {e}")
            _movies_cache = []
    return _movies_cache


def generate_answer(user_input: str):
    movies = get_movies()
    user_clean = clean_text(user_input)
    intent = detect_intent(user_input)
    movie_candidate = extract_movie_name(user_input)
    phim = fuzzy_find_movie_name(movie_candidate, movies) if movie_candidate else None
    raw_name = movie_candidate.strip()

    if intent == "genre_query":
        genres = [
            "hành động", "phiêu lưu", "hài", "kinh dị", "tâm lý", "tình cảm",
            "khoa học viễn tưởng", "hoạt hình", "chiến tranh", "hình sự", "viễn tây",
            "âm nhạc", "thể thao", "tài liệu", "gia đình", "lịch sử", "giả tưởng",
            "siêu anh hùng", "anime", "phim ngắn"
        ]
        genre_matched = next((g for g in genres if g in user_input.lower()), None)
        if genre_matched:
            genre_movies = get_movies_by_genre_today(genre_matched)
            if genre_movies:
                return f"Các phim thể loại phim {genre_matched.title()} hôm nay:\n" + "\n".join(
                    f"🎬 {m}" for m in genre_movies)
            else:
                return f"❌ Không có phim thể loại {genre_matched.title()} đang chiếu hôm nay."

    if intent == "actor" and not phim:
        act_matches = [m for m in movies if any(raw_name in actor for actor in m["actors_clean"])]
        if act_matches:
            phim_names = ", ".join(sorted(set(m["movie_name_vn"] for m in act_matches)))
            return f"Diễn viên {raw_name.title()} có trong các phim: {phim_names}"
        else:
            return f"Tôi không tìm thấy phim nào có diễn viên {raw_name.title()}."

    if intent == "director" and not phim:
        dir_matches = [m for m in movies if raw_name in m["dir_clean"]]
        if dir_matches:
            phim_names = ", ".join(sorted(set(m["movie_name_vn"] for m in dir_matches)))
            return f"{dir_matches[0]['director']} Đạo diễn phim: {phim_names}"
        else:
            return f"Tôi không tìm thấy đạo diễn nào tên {raw_name.title()}."

    if intent is None and phim:
        return f"Bạn đang hỏi về phim {phim['movie_name_vn']}. Vui lòng nói rõ bạn muốn biết gì: nội dung, trailer, diễn viên...?"

    if intent == "today_movies":
        movies_today = get_movies_showing_today()
        return "Hôm nay đang chiếu các phim:\n" + "\n".join(f"🎞️ {m}" for m in movies_today) if movies_today else "Không có phim nào đang chiếu hôm nay."

    # ✳️ BỔ SUNG xử lý khi có từ 'suất chiếu' nhưng không xác định được intent
    if not intent and phim and "suat chieu" in user_clean:
        return get_showtime_today_for(phim["movie_name_vn"])

    if intent == "showtime" and phim:
        return get_showtime_today_for(phim["movie_name_vn"])

    if intent == "nearest_showtime_multiple":
        return "\n".join(get_nearest_showtime_for(phim["movie_name_vn"])) if phim else get_multiple_nearest_showtimes()

    if intent == "nearest_showtime_for_movie":
        return get_nearest_showtime_for(phim["movie_name_vn"]) if phim else "Bạn muốn xem suất chiếu gần nhất của phim nào?"

    if phim:
        if intent == "trailer":
            return f"https://youtu.be/{phim['trailer_id']}" if phim.get("trailer_id") else f"Phim {phim['movie_name_vn']} chưa có trailer."
        elif intent == "content":
            return f"Nội dung phim {phim['movie_name_vn']}: {phim['content']}"
        elif intent == "duration":
            return f"Phim {phim['movie_name_vn']} có thời lượng {phim['duration']} phút."
        elif intent == "director":
            return f"Phim {phim['movie_name_vn']} do {phim['director']} đạo diễn."
        elif intent == "actor":
            return f"Diễn viên trong phim {phim['movie_name_vn']} gồm: {phim['actor']}"
        elif intent == "rating":
            return f"Phim {phim['movie_name_vn']} được đánh giá {phim.get('rating', 'chưa có')} điểm."

    return "Tôi chưa có dữ liệu phù hợp để trả lời."



def main():
    print("🎬 Xin chào! Tôi có thể giúp gì về phim hôm nay? (Gõ 'exit' để thoát)\n")
    while True:
        try:
            user_input = input("👤 Bạn: ").strip()
            if user_input.lower() in ["exit", "quit", "thoat"]:
                print("👋 Tạm biệt!")
                break
            response = generate_answer(user_input)
            print(f"🤖 Bot: {response}\n")
        except KeyboardInterrupt:
            print("\n👋 Tạm biệt!")
            break
        except Exception as e:
            print(f"⚠️ Lỗi xảy ra: {str(e)}\n")


if __name__ == "__main__":
    main()
