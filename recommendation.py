import pandas as pd

def load_data(city_file, hotel_data_file):
    try:
        city_data = pd.read_csv(city_file)
        hotel_data = pd.read_csv(hotel_data_file)
    except FileNotFoundError as e:
        print(f"Error: {e}")
        return None, None
    
    return city_data, hotel_data

def preprocess_data(city_data, hotel_data):
    # Check if required columns are present
    required_hotel_columns = ['City', 'Hotel_Name', 'Hotel_Price', 'Hotel_Rating']
    required_city_columns = ['City', 'Ratings']

    missing_hotel_columns = [col for col in required_hotel_columns if col not in hotel_data.columns]
    missing_city_columns = [col for col in required_city_columns if col not in city_data.columns]

    if missing_hotel_columns:
        print(f"Missing columns in hotel data: {', '.join(missing_hotel_columns)}")
        return None

    if missing_city_columns:
        print(f"Missing columns in city data: {', '.join(missing_city_columns)}")
        return None

    # Drop rows where important columns have missing values in the hotel dataset
    hotel_data_clean = hotel_data.dropna(subset=['City', 'Hotel_Name', 'Hotel_Price'])

    # Convert city names to lowercase for consistent matching
    hotel_data_clean['City'] = hotel_data_clean['City'].str.lower()
    city_data['City'] = city_data['City'].str.lower()

    # Merge the hotel and city datasets based on the city name
    merged_data = pd.merge(hotel_data_clean, city_data[['City', 'Ratings']], on='City', how='left')

    return merged_data

def recommend_hotels(merged_data, city_input, min_price, max_price):
    # Normalize the input city to lowercase
    city_input = city_input.lower()
    
    # Filter hotels in the specified city
    city_hotels = merged_data[merged_data['City'] == city_input]
    
    if city_hotels.empty:
        return f"No hotels found for city: {city_input.capitalize()}"
    
    # Filter hotels within the price range
    price_filtered_hotels = city_hotels[
        (city_hotels['Hotel_Price'] >= min_price) & 
        (city_hotels['Hotel_Price'] <= max_price)
    ]
    
    if price_filtered_hotels.empty:
        return f"No hotels found in {city_input.capitalize()} within the price range: {min_price} - {max_price}"
    
    # Sort by hotel rating and return the name of the top recommendation
    recommended_hotel_name = price_filtered_hotels.sort_values(by='Hotel_Rating', ascending=False)['Hotel_Name'].iloc[0]
    return recommended_hotel_name

def main(city_file, hotel_data_file, city_input, budget):
    city_data, hotel_data = load_data(city_file, hotel_data_file)
    
    if city_data is None or hotel_data is None:
        return
    
    merged_data = preprocess_data(city_data, hotel_data)
    
    if merged_data is None:
        return
    
    try:
        min_price = budget * 0.8
        max_price = budget * 1.2
    except ValueError:
        print("Invalid input for budget. Please enter a numeric value.")
        return

    recommendation = recommend_hotels(merged_data, city_input, min_price, max_price)
    print(recommendation)

# Example usage
if __name__ == "__main__":
    city_file = 'dataset/City.csv'
    hotel_data_file = 'dataset/google_hotel_data_clean_v2.csv'
    
    # Get user input for city and price range
    city_input = input("Enter the city: ")
    try:
        budget = float(input("Enter the budget: "))
    except ValueError:
        print("Invalid input for budget. Please enter a numeric value.")
        exit()

    # Call the main function
    main(city_file, hotel_data_file, city_input, budget)
