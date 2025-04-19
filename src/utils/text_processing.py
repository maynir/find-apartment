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
    "אחד וחצי חדרים",
    "2 חדרים",
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
    "2.5 חדרים" ,
    "שתיים וחצי חדרים",
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
    "מתפנה חדר",
    "מפנה חדר",
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
    # "לבונטין",
    # "סטודיו",
    "למכירה"
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


def match_info(bad_match_word, good_match_word):
    return f"bad_match_word:{bad_match_word.group() if bad_match_word else 'None'}, good_match_word:{good_match_word.group() if good_match_word else 'None'}"
