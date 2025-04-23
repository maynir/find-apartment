import folium
from io import BytesIO
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderUnavailable

def get_coordinates(address, city):
    """Get coordinates for an address using Nominatim geocoder"""
    if not address and not city:
        return None

    # Prepare the search query
    search_query = f"{address}, {city}, ישראל" if address else f"{city}, ישראל"

    try:
        geolocator = Nominatim(user_agent="find-apartment-bot")
        location = geolocator.geocode(search_query)
        if location:
            return (location.latitude, location.longitude)
    except (GeocoderTimedOut, GeocoderUnavailable) as e:
        print(f"⚠️ Error getting coordinates: {e}")
    return None

def generate_map_image(address, city):
    """Generate a map image for the given address and city"""
    coordinates = get_coordinates(address, city)
    if not coordinates:
        return None

    m = folium.Map(location=coordinates, zoom_start=15)

    # Add a marker for the location
    folium.Marker(
        coordinates, popup=address, icon=folium.Icon(color="red", icon="info-sign")
    ).add_to(m)

    # Save map to BytesIO
    img_data = m._to_png()
    img_io = BytesIO(img_data)

    return img_io
