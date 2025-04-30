import json

from openai import OpenAI

from etc import config

client = OpenAI(api_key=config.OPENAI_API_KEY)


def analyze_budget_with_openai(text):
    """
    Use OpenAI to analyze if the post is within budget.
    Returns a tuple of (is_within_budget, price, explanation)
    """
    try:
        # First try to extract price using regex for efficiency
        # price = extract_price_from_text(text)
        # if price is not None:
        #     is_within_budget = price <= config.BUDGET_THRESHOLD
        #     return (is_within_budget, price, f"Price extracted: {price} ILS")

        # If regex fails, use OpenAI
        prompt = f"""
        Analyze the following apartment post text and determine:
        1. Is there a price mentioned? If yes, what is the price in ILS (Israeli Shekels)?
        2. Is the price less than or equal to {config.BUDGET_THRESHOLD} ILS?

        Post text:
        {text}

        Respond in the following JSON format:
        {{
            "price_mentioned": true/false,
            "price": number or null,
            "is_within_budget": true/false,
            "explanation": "brief explanation"
        }}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant that analyzes apartment posts in Hebrew to extract price information.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        # Parse the response
        result = response.choices[0].message.content

        parsed_result = json.loads(result)

        price = parsed_result.get("price")
        is_within_budget = parsed_result.get("is_within_budget", False)
        explanation = parsed_result.get("explanation", "No explanation provided")

        return (is_within_budget, price, explanation)

    except Exception as e:
        print(f"⚠️ Error analyzing budget with OpenAI: {e}")
        return (False, None, f"Failed to analyze budget: {str(e)}")


def analyze_apartment_details_with_openai(text):
    """
    Use OpenAI to analyze apartment post details.
    Returns a tuple of (price, city, address, rooms, location_details, close_to_sea)
    """
    try:
        prompt = f"""
        Analyze the following apartment post text and determine:
        1. What is the price in ILS (Israeli Shekels)?
        2. What is the city name?
        3. What is the location? Return ONLY the street name and number WITHOUT the word 'רחוב', or if not available, return the neighborhood name.
        4. What is the EXACT number of rooms?
        5. Give a brief, one-line summary of key location details (nearby landmarks, transportation, or features).
        6. Is the location close to the beach?

        Post text:
        {text}

        Respond in the following JSON format:
        {{
            "price": number or null,
            "city": string or null,
            "address": string or null,
            "rooms": number or null,
            "location_details": string or null,
            "close_to_sea": boolean or null
        }}
        """

        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {
                    "role": "system",
                    "content": "You are a helpful assistant answering in hebrew that analyzes apartment posts in Hebrew to extract key information. You have deep knowledge of Israeli cities and landmarks. Provide brief, concise summaries and be accurate.",
                },
                {"role": "user", "content": prompt},
            ],
            temperature=0,
            response_format={"type": "json_object"},
        )

        # Parse the response
        result = response.choices[0].message.content
        parsed_result = json.loads(result)

        price = parsed_result.get("price")
        city = parsed_result.get("city")
        address = parsed_result.get("address")
        rooms = parsed_result.get("rooms")
        location_details = parsed_result.get("location_details")
        close_to_sea = parsed_result.get("close_to_sea")

        return (price, city, address, rooms, location_details, close_to_sea)

    except Exception as e:
        print(f"⚠️ Error analyzing apartment details with OpenAI: {e}")
        return (None, None, None, None, None, None)
