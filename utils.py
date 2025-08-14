import re
from datetime import datetime
from difflib import get_close_matches
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from unidecode import unidecode


def clean_text(s: str) -> str:
    if not s:
        return ""
    s = unidecode(s)
    s = s.lower()
    return re.sub(r"[^a-z0-9\s]", " ", s).strip()

def parse_date(date_str):
    if isinstance(date_str, datetime):
        return date_str
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except:
        return None

def extract_movie_name(user_input: str) -> str:
    text = clean_text(user_input)
    keywords = [
        "trailer", "phim", "xem", "co", "noi dung", "tom tat", "keo dai", "do dai", "thoi luong",
        "dao dien", "dien vien", "lich chieu", "cua", "của", "muon xem", "toi muon xem",
        "toi muon xem phim", "toi muon", "phim cua", "phim co", "phim nao cua", "phim nao co",
        "xem phim cua", "xem phim co", "phim nao", "phim gi", "phim gi hom nay"
    ]
    for kw in keywords:
        text = text.replace(kw, "")
    return text.strip()

def detect_intent(user_input: str):
    user_clean = clean_text(user_input)
    corpus = []
    intent_keywords = {
        "trailer": ["trailer", "teaser", "clip", "gioi thieu", "trailer phim", "xem trailer"],
        "content": ["noi dung", "tom tat", "phim noi ve", "nội dung phim", "kể sơ", "giới thiệu phim"],
        "duration": ["keo dai", "bao lau", "thoi luong", "bao nhieu phut", "do dai"],
        "director": [
            "dao dien", "phim cua ai", "ai dao dien", "phim nao cua",
            "toi muon xem phim cua dao dien", "phim cua dao dien", "xem phim cua"
        ],
        "actor": [
    "dien vien", "ai dong", "ai tham gia",
    "phim co", "phim nao co", "phim cua dien vien",
    "xem phim cua", "xem phim co", "toi muon xem phim co",
    "co phim cua", "phim nao cua", "phim cua"
],
"director": [
    "dao dien", "ai dao dien", "phim cua ai", "phim nao cua dao dien",
    "co phim cua dao dien", "phim nao cua", "phim cua"
],

        "hot_movie": ["phim hot", "phim hay", "phim noi bat"],
        "genre_action": ["hanh dong", "danh dam", "chien dau"],
        "genre_horror": ["kinh di", "ma", "so hai"],
        "showtime": ["lich chieu", "gio chieu", "suat chieu"],
        "today_movies": [
            "phim gi hom nay", "phim dang chieu", "phim hom nay",
            "dang chieu hom nay", "hom nay co phim gi", "hom nay co gi chieu", "hom nay chieu gi"
        ],
        "nearest_showtime_multiple": [
            "phim sap chieu", "phim nao sap chieu", "suat chieu gan nhat",
            "xem phim som nhat", "lich chieu sap nhat", "phim nao chieu som nhat",
            "suat sap chieu", "phim nao sap chieu nhat", "phim nao chieu gan nhat hom nay",
            "5 phim sap chieu", "lich chieu gan nhat", "suat chieu som nhat",
            "phim sap chieu hom nay", "phim chieu som", "phim nao chieu truoc"
        ],
        "nearest_showtime_for_movie": [
            "gio chieu phim", "phim abc chieu luc nao", "phim .* luc nao",
            "phim .* gio chieu", "luc nao chieu phim", "phim .* sap chieu",
            "xem phim .* luc nao", "phim .* gan nhat", "phim .* suat chieu"
        ],
        "genre_query": [
            "phim hanh dong", "co phim hanh dong khong",
            "phim phieu luu", "phim hai", "phim kinh di", "phim tam ly", "phim tam li",
            "phim tinh cam", "phim khoa hoc vien tuong", "phim hoat hinh", "phim chien tranh",
            "phim hinh su", "phim vien tay", "phim am nhac", "phim the thao", "phim tai lieu",
            "phim gia dinh", "phim lich su", "phim gia tuong", "phim sieu anh hung", "phim anime",
            "phim phim ngan", "phim ngan"
        ]


    }

    intent_labels = []
    for label, keys in intent_keywords.items():
        for k in keys:
            corpus.append(clean_text(k))
            intent_labels.append(label)

        # ✅ Ưu tiên kiểm tra chứa từ khóa thể loại
    if any(g in user_clean for g in intent_keywords.get("genre_query", [])):
        return "genre_query"

    for phrase in corpus:
        if get_close_matches(user_clean, [phrase], n=1, cutoff=0.8):
            matched_index = corpus.index(phrase)
            return intent_labels[matched_index]

    vectorizer = TfidfVectorizer()
    all_texts = corpus + [user_clean]
    X = vectorizer.fit_transform(all_texts)
    scores = cosine_similarity(X[-1], X[:-1])[0]
    best_idx = scores.argmax()
    return intent_labels[best_idx] if scores[best_idx] >= 0.3 else None

from difflib import get_close_matches
from unidecode import unidecode

def fuzzy_find_movie_name(name: str, movie_list: list) -> dict:
    name_clean = unidecode(name).lower().strip()

    if not name_clean:
        return None

    # So khớp tuyệt đối với tên gốc (không clean)
    for m in movie_list:
        if name.strip().lower() == m["movie_name_vn"].strip().lower():
            return m

    # So khớp tuyệt đối với vn_clean
    for m in movie_list:
        if name_clean == m["vn_clean"]:
            return m

    # So khớp chứa trong tên
    for m in movie_list:
        if name_clean in m["vn_clean"]:
            return m

    # So khớp fuzzy gần đúng
    title_map = {m["vn_clean"]: m for m in movie_list}
    matches = get_close_matches(name_clean, title_map.keys(), n=1, cutoff=0.6)
    if matches:
        return title_map[matches[0]]

    return None

