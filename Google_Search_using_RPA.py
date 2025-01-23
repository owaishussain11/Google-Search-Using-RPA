import http.client
import json
import pandas as pd
import urllib.parse

# Step 1: Fetch dest_id based on the user input location


def fetch_dest_id(location):
    conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "f8bdab4d1cmshfb039d59a479c88p1d22c8jsnfcf40c7e381d",
        'x-rapidapi-host': "booking-com15.p.rapidapi.com"
    }

    # Search for the destination ID
    destination_url = f"/api/v1/hotels/searchDestination?query={urllib.parse.quote(location)}&locale=en-us"

    print('dest_url', destination_url)

    conn.request("GET", destination_url, headers=headers)
    res = conn.getresponse()
    data = res.read()

    print('res', res, data)

    if res.status == 200:
        response_data = json.loads(data.decode("utf-8"))
        if response_data.get("data"):
            dest_id = response_data["data"][0].get("dest_id", None)
            print(f"Destination ID for {location}: {dest_id}")
            return dest_id
        else:
            print(f"No destination ID found for {location}.")
            return None
    else:
        print(f"Failed to fetch destination ID: {res.status} - {res.reason}")
        return None

# Step 2: Use dest_id to fetch hotel data (No check-in/checkout dates)


def fetch_hotel_data(location):
    dest_id = fetch_dest_id(location)
    if not dest_id:
        return []

    conn = http.client.HTTPSConnection("booking-com15.p.rapidapi.com")

    headers = {
        'x-rapidapi-key': "f8bdab4d1cmshfb039d59a479c88p1d22c8jsnfcf40c7e381d",
        'x-rapidapi-host': "booking-com15.p.rapidapi.com"
    }

    # Simplified query without check-in and checkout dates
    querystring = {
        "dest_id": dest_id,
        "search_type": "CITY",
        "arrival_date": "2025-02-01",
        "departure_date": "2025-02-10",
        "locale": "en-us",
        "page": "1"
    }
    # Encode the query parameters for the hotel search
    hotel_search_url = f"/api/v1/hotels/searchHotels?{urllib.parse.urlencode(querystring)}"

    print('hotel_search_url', hotel_search_url)

    conn.request("GET", hotel_search_url, headers=headers)
    res = conn.getresponse()
    data = res.read()

    # Debug: Print response to verify data
    print("Hotel Search Response:", data.decode("utf-8"))

    if res.status == 200:
        response_data = json.loads(data.decode("utf-8"))
        hotels = []

        # Check if data exists
        if response_data.get("data"):
            # data.hotel
            for result in response_data.get("data").get("hotels", []):
                hotels.append({
                    "Hotel ID": result.get("hotel_id", 'No ID available'),
                    "Name": result.get("property").get("name", 'No name available'),
                    "Description": result.get("accessibilityLabel", 'No description available'),
                    "Ranking Position": result.get("property").get("rankingPosition", 'No ranking available'),
                    "Rating": result.get("property").get("reviewScore", 'No rating available'),
                })
        else:
            print("No hotel data found for this location.")

        return hotels
    else:
        print(f"Failed to fetch hotel data: {res.status} - {res.reason}")
        return []

# Step 3: Save hotel data to Excel


def save_to_excel(hotel_list, location):
    df = pd.DataFrame(hotel_list)
    filename = f"hotels_in_{location.replace(' ', '_')}.xlsx"
    df.to_excel(filename, index=False)
    print(f"Hotel data saved to {filename}")

# Step 4: Main function to handle the search


def main():
    location = input("Enter the location for hotel search: ").strip()
    hotels = fetch_hotel_data(location)

    if hotels:
        save_to_excel(hotels, location)
    else:
        print("No hotel data found or an error occurred.")


if __name__ == "__main__":
    main()
