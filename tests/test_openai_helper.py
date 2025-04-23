import unittest

from src.utils.openai_helper import (
    analyze_budget_with_openai,
    analyze_apartment_details_with_openai,
)


class TestOpenAIHelper(unittest.TestCase):
    """Test cases for the OpenAI helper functions"""

    # Test cases for apartment details analysis
    APARTMENT_TEST_CASES = [
        {
            "description": "Full apartment details in Tel Aviv with specific address",
            "text": "דירת 3 חדרים להשכרה ברחוב דיזנגוף 99, תל אביב, מחיר: 4500 שח לחודש",
            "expected": {
                "price": 4500,
                "city": "תל אביב",
                "address": "רחוב דיזנגוף 99",
                "rooms": 3,
                # "location_details": "מרכז תל אביב",
            },
        },
        {
            "description": "Apartment in Florentin with neighborhood only",
            "text": "דירת 2.5 חדרים להשכרה בפלורנטין, תל אביב, 5000 שקל",
            "expected": {
                "price": 5000,
                "city": "תל אביב",
                "address": "פלורנטין",
                "rooms": 2.5,
                # "location_details": "שכונת פלורנטין",
            },
        },
        {
            "description": "Apartment with partial address details",
            "text": "דירה 4 חדרים בשכונת רמת אביב ג, צפון תל אביב, 8000 שקל",
            "expected": {
                "price": 8000,
                "city": "תל אביב",
                "address": "רמת אביב ג",
                "rooms": 4,
                # "location_details": "צפון תל אביב",
            },
        },
        {
            "description": "Complex listing near Shuk HaTikva",
            "text": "להשכרה-ללא תיווך!\n"
            "דירה עורפית מקסימה, מרוהטת קומפלט.\n"
            "מתאימה ליחיד-סטודנט/עובד.\n"
            "בבניין ורחוב שקטים במיוחד.\n"
            "קומה ראשונה- ק+1.\n"
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
            "expected": {
                "price": 2650,
                "city": "תל אביב",
                "address": None,
                "rooms": 1,
                # "location_details":
                #     "5 דק מהשוק והרכבת",
            },
        },
    ]

    def test_analyze_apartment_details_with_openai_real_api(self):
        """Test the OpenAI-based apartment details analysis function with real API calls"""

        for test_case in self.APARTMENT_TEST_CASES:
            with self.subTest(description=test_case["description"]):
                price, city, address, rooms, location_details = (
                    analyze_apartment_details_with_openai(test_case["text"])
                )

                expected = test_case["expected"]
                self.assertEqual(price, expected["price"])
                self.assertEqual(city, expected["city"])
                self.assertEqual(address, expected["address"])
                self.assertEqual(rooms, expected["rooms"])
                # self.assertEqual(location_details, expected["location_details"])

    def test_analyze_budget_with_openai_real_api(self):
        """Test the OpenAI-based budget analysis function with a real API call"""

        apartment_text = "דירה להשכרה במרכז תל אביב, מחיר: 6500 שח לחודש"

        is_within_budget, price, explanation = analyze_budget_with_openai(
            apartment_text
        )

        self.assertEqual(price, 6500)
        self.assertEqual(is_within_budget, True)


if __name__ == "__main__":
    unittest.main()
