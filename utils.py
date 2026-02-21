import re


def remove_tashkeel(text):
    tashkeel_pattern = re.compile(
        r'[\u0617-\u061A\u064B-\u0652]'
    )
    return re.sub(tashkeel_pattern, '', text)


def normalize_arabic(text):
    text = re.sub("[إأآا]", "ا", text)
    text = re.sub("ى", "ي", text)
    text = re.sub("ؤ", "و", text)
    text = re.sub("ئ", "ي", text)
    text = re.sub("ة", "ه", text)
    return text


def preprocess_arabic(text):
    text = remove_tashkeel(text)
    text = normalize_arabic(text)
    return text


def remove_tafsir_stopwords(query):
    # Strip trailing punctuation first
    cleaned = re.sub(r'[\?؟\.،]+$', '', query).strip()
    
    # 1. Strip trailing author names (e.g. "عند الطبري")
    author_pattern = r'\s+(?:عند|حسب|تفسير)\s+(?:الطبري|ابن\s*كثير|القرطبي|السعدي|البغوي|الجلالين|الميسر)$'
    cleaned = re.sub(author_pattern, '', cleaned).strip()

    # 2. Main Prefix Stripper
    prefix_pattern = r'^(?:(?:ما\s+)?(?:تفسير|معنى|معني|شرح|مقصود|المقصود|المراد)\s+(?:بـ|في\s+)?(?:قوله\s+تعالى|قوله\s+تعالي|قوله\s+عز\s*وجل|آية|اية|سورة)?\s*)' \
                     r'|^(?:ماذا\s+قال\s+المفسرون\s+في\s+قوله\s+تعالى\s*)' \
                     r'|^(?:كيف\s+فسر\s+.*?\s+آية\s+)' \
                     r'|^(?:أقوال\s+العلماء\s+في\s+تفسير\s*)' \
                     r'|^(?:تفسير\s+(?:آية|اية|سورة)\s*)' \
                     r'|^(?:تفسير\s+)' \
                     r'|^(?:شرح\s+(?:آية|اية)\s*)'
    
    # Needs to be stripped repeatedly to peel layers like "تفسير آية"
    old = ""
    while old != cleaned:
        old = cleaned
        cleaned = re.sub(prefix_pattern, '', cleaned, flags=re.IGNORECASE).strip()
        
    return cleaned


def bm25_tokenize(text):
    return preprocess_arabic(text).split()


def preprocess_query(query):
    query = preprocess_arabic(query)
    return bm25_tokenize(query)
