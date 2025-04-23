import re

single_apartment_words = [
    "יחיד",
    "יחידה",
    "רווק",
    "רווקה",
    "ליחיד",
    "ליחידה",
    "ליחידים",
    "לרווק",
    "לרווקה",
    "סטודיו",
    "דירת יחיד",
    "דירה ללא שותפים",
    "1.5 חדרים",
    "1.5 חד",
    "1.5 חד'",
    "אחד וחצי חדרים",
    "2 חדרים",
    "2 חד",
    "2 חד,",
    "חדר שינה וסלון",
    "חדר שינה + חדר עבודה",
    "שני חדרים",
    "2 חדרים",
    "חדר וחצי",
    # "דירת חדר",
    "אחד וחצי",
    "שני חדרים",
    "שניי חדרים",
    "שני חדריי",
    "2.5 חדרים",
    "שתיים וחצי חדרים",
    "שניים וחצי חדרים",
    "פרטר",
    "שלושה חדרים",
    "3 חדרים",
]
sharable_apartment_words = [
    "השותף",
    "השותפה",
    "שותף",
    "שותפה",
    "מתפנה חדר",
    "מפנה חדר",
    "מחליפה",
    "מחליף",
    "מחליפ/ה",
    "שותפ/ה",
    "מחפשת שותפה",
    "מחפש שותפה",
    "מחפש שותף",
    "מחפשת שותפה",
    "מפנה את החדר שלי",
    "חדר להשכרה",
    "דירת שותפים",
    "בדירת שותפים",
    "מפנה את חדרי",
    "שותף/ה",
    "עוזב את החדר שלי",
    "עוזבת את החדר שלי",
    "חדר בדירת",
    "שותפים",
    "שותפות",
    "מפנה את החדר",
    "שלושה חדרים",
    "3 חדרים",
]
sublet_words = [
    "סאבלט",
    "סבלט",
    "מסבלטת",
    "מסבלט",
    "מסבלטים",
]
words = single_apartment_words
good_words_regex = re.compile(r"\b(" + "|".join(re.escape(x) for x in words) + r")\b")

single_apartment_bad_words = [
    "מחפשת דירה",
    "מחפשת דירת",
    "מחפש דירה",
    "מחפש דירת",
    "מתפנה חדר",
    "מפנה חדר",
    "מפנה את החדר",
    "מחפשות שותפה",
    "מחפשות שותף",
    "מחפשים שותפה",
    "מחפשים שותף",
    "מחפשת שותפה",
    "מחפש שותפה",
    "מחפש שותף",
    "מחפשת שותפה",
    "מפנה את החדר שלי",
    "חדר להשכרה",
    "דירת שותפים",
    "בדירת שותפים",
    "מפנה את חדרי",
    "חדר בדירת",
    # "פלורנטין",
    "יד אליהו",
    "רמת גן",
    "נווה אליעזר",
    "בת ים",
    "השותפים",
    "בשכונת התקווה",
    "שכונת התקווה",
    "נווה שאנן",
    "הרצליה",
    "בהרצליה",
    "שפירא",
    "בשפירא",
    "הדר יוסף",
    "בהדר יוסף",
    "יצחק שדה",
    "ביצחק שדה",
    "דירת יוקרה",
    "כיכר המדינה",
    "לה גוארדיה",
    # "לבונטין",
    # "סטודיו",
    "למכירה",
    "נשאר שותף",
    "נשארת שותפה",
    "שכונת לבנה",
    "בשכונת לבנה",
]
sharable_apartment_bad_words = [
    "סורי בנות",
    "סליחה בנות",
    "ביפו",
    "פלורנטין",
    "יד אליהו",
    "רמת גן",
    "נווה אליעזר",
    "בת ים",
    "לא לשותפים",
    "לא מתאימה לשותפים",
    "רמת אביב",
]
no_living_room_word = ["בלי סלון", "אין סלון", "ללא סלון"]
bad_words = single_apartment_bad_words
bad_words_regex = re.compile("|".join(re.escape(x) for x in bad_words))


def validate_match(text, price=None, city=None, rooms=None):
    """
    Validates if an apartment posting is a good match based on both regex and OpenAI extracted data.
    Returns a tuple of (is_good_match, is_bad_match, good_match_word, bad_match_word)
    """
    good_match_word = good_words_regex.search(text)
    bad_match_word = bad_words_regex.search(text)

    # Initial check based on regex
    is_good_match_word = bool(good_match_word)
    is_bad_match_word = bool(bad_match_word)

    # # If we have OpenAI data, use it to validate further
    # if any(x is not None for x in [price, city, rooms]):
    # Bad match conditions based on OpenAI data
    if city and not re.search(r"תל אביב", city.strip()):
        is_bad_match_word = True

    # Good match conditions based on OpenAI data
    if rooms is not None:
        if 1 <= rooms <= 3:  # Consider studios and up to 2.5 rooms as good matches
            is_good_match_word = True
        else:  # 3 or more rooms usually indicates shared apartments
            is_bad_match_word = True

    return is_good_match_word, is_bad_match_word, good_match_word, bad_match_word


def match_info(bad_match_word, good_match_word):
    return f"bad_match_word:{bad_match_word.group() if bad_match_word else 'None'}, good_match_word:{good_match_word.group() if good_match_word else 'None'}"
