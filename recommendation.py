import pandas as pd

# Load the uploaded CSV files
city_file = 'dataset/City.csv'
hotel_data_file = 'dataset/google_hotel_data_clean_v2.csv'

# Read the files
try:
    city_data = pd.read_csv(city_file)
    hotel_data = pd.read_csv(hotel_data_file)
except FileNotFoundError as e:
    print(f"Error: {e}")
    exit()

# Drop rows where important columns have missing values in the hotel dataset
hotel_data_clean = hotel_data.dropna(subset=['City', 'Hotel_Name', 'Hotel_Price'])

# Convert city names to lowercase for consistent matching
hotel_data_clean['City'] = hotel_data_clean['City'].str.lower()
city_data['City'] = city_data['City'].str.lower()

# Merge the hotel and city datasets based on the city name
merged_data = pd.merge(hotel_data_clean, city_data[['City', 'Ratings']], on='City', how='left')

# Save the merged dataframe to a new CSV file
merged_data.to_csv('dataset/merged_file.csv', index=False)

# Function to recommend hotels based on city and price range
def recommend_hotels(city_input, min_price, max_price):
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

# Get user input for city and price range
city_input = input("Enter the city: ")
try:
    budget = float(input("Enter the budget: "))
except ValueError:
    print("Invalid input for budget. Please enter a numeric value.")
    exit()

min_price = budget * 0.8
max_price = budget * 1.2

# Call the recommendation function with user input
recommendation = recommend_hotels(city_input, min_price, max_price)
print(recommendation)
