import pytest

from src.utils.openai_helper import (
    analyze_budget_with_openai,
    analyze_apartment_details_with_openai,
)


# Test cases for apartment details analysis
APARTMENT_TEST_CASES = [
    pytest.param(
        "דירת 3 חדרים להשכרה ברחוב דיזנגוף 99, תל אביב, מחיר: 4500 שח לחודש",
        {"price": 4500, "city": "תל אביב", "address": "דיזנגוף 99", "rooms": 3, "is_in_kerem_hateimanim": False},
        id="full_apartment_details_tel_aviv",
    ),
    pytest.param(
        "דירת 2.5 חדרים להשכרה בפלורנטין, תל אביב, 5000 שקל",
        {"price": 5000, "city": "תל אביב", "address": "פלורנטין", "rooms": 2.5, "is_in_kerem_hateimanim": False},
        id="florentin_neighborhood_only",
    ),
    pytest.param(
        "דירה 4 חדרים בשכונת רמת אביב ג, צפון תל אביב, 8000 שקל",
        {"price": 8000, "city": "תל אביב", "address": "רמת אביב ג", "rooms": 4, "is_in_kerem_hateimanim": False},
        id="partial_address_ramat_aviv",
    ),
    pytest.param(
        "רחוב אייר",
        {"price": None, "city": None, "address": "אייר", "rooms": None, "is_in_kerem_hateimanim": False},
        id="street_only",
    ),
    pytest.param(
        "להשכרה-ללא תיווך!\n"
        "דירה עורפית מקסימה, מרוהטת קומפלט.\n"
        "מתאימה ליחיד-סטודנט/עובד.\n"
        "בבניין ורחוב שקטים במיוחד.\n"
        "קומה ראשונה- קומה+1.\n"
        "חניה בשפע.\n"
        "שכירות-2,650₪\n"
        "כולל ארנונה ומים.\n"
        "כניסה ב1.5\n"
        "לפרטים-\n"
        "רועי 0523401525\n"
        "מרינה 0546699249\n"
        "מרחק של 5 דק הליכה משוק התקווה ומרכבת ההגנה.\n"
        "באזור ישנם מספר פארקים,מרכז קהילתי.\n"
        "איזור נגיש ונוח מאוד.",
        {"price": 2650, "city": "תל אביב", "address": "התקווה", "rooms": 1, "is_in_kerem_hateimanim": False},
        id="complex_listing_shuk_hatikva",
    ),
    pytest.param(
        "דירת סטודיו מושלמת, ברח' חבקוק 7 100 מטר מחוף מציצים, שכ\"ד 6.350 ₪ (לא כולל חשבונות)",
        {"price": 6350, "city": "תל אביב", "address": "חבקוק 7", "rooms": 1, "is_in_kerem_hateimanim": False},
        id="price_with_dot",
    ),
    pytest.param(
        "חדר שינה וסלון",
        {"price": None, "city": None, "address": None, "rooms": 2, "is_in_kerem_hateimanim": False},
        id="bedroom_and_living_room",
    ),
    pytest.param(
        "דירת 2 חדרים להשכרה ברחוב בוגרשוב 50, תל אביב, 5500 שקל",
        {"price": 5500, "city": "תל אביב", "address": "בוגרשוב 50", "rooms": 2, "is_in_kerem_hateimanim": False},
        id="bograshov_NOT_in_kerem_hateimanim",
    ),
    pytest.param(
        "דירת 3 חדרים להשכרה ברחוב גאולה 15, כרם התימנים, תל אביב, 6000 שקל",
        {"price": 6000, "city": "תל אביב", "address": "גאולה 15", "rooms": 3, "is_in_kerem_hateimanim": True},
        id="geula_IS_in_kerem_hateimanim",
    ),
    pytest.param(
        "דירת 3 חדרים להשכרה ברחוב הרב קוק 15, תל אביב, 6000 שקל",
        {"price": 6000, "city": "תל אביב", "address": "הרב קוק 15", "rooms": 3, "is_in_kerem_hateimanim": True},
        id="harav_kook_IS_in_kerem_hateimanim",
    ),
]


@pytest.mark.parametrize("text,expected", APARTMENT_TEST_CASES)
def test_analyze_apartment_details(text, expected):
    """Test the OpenAI-based apartment details analysis function"""
    price, city, address, rooms, location_details, close_to_sea, is_in_kerem_hateimanim = (
        analyze_apartment_details_with_openai(text)
    )

    assert price == expected["price"]
    assert city == expected["city"]
    assert address == expected["address"]
    assert rooms == expected["rooms"]
    assert is_in_kerem_hateimanim == expected["is_in_kerem_hateimanim"]


def test_analyze_budget():
    """Test the OpenAI-based budget analysis function"""
    apartment_text = "דירה להשכרה במרכז תל אביב, מחיר: 6500 שח לחודש"

    is_within_budget, price, explanation = analyze_budget_with_openai(apartment_text)

    assert price == 6500
    assert is_within_budget == True
