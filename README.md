
## TripGenie - AI-Powered Travel Planner

Welcome to TripGenie, your AI-powered travel companion! TripGenie simplifies the process of planning the perfect trip, offering personalized itineraries based on your destination, budget, and duration. Whether you're planning a quick weekend getaway or a once-in-a-lifetime adventure, TripGenie helps you craft a seamless and enjoyable experience.


## Features

1. Effortless Trip Itineraries: Generate personalized travel plans, including destination recommendations, activities, and places to visit based on your preferences.
2. Hotel Recommendations: Receive hotel suggestions tailored to your budget and city of choice.
3. Save and Manage Plans: Save your travel itineraries and manage them from your profile. 
4. Delete or modify saved plans as needed.
5. PDF Export: Download your itinerary in PDF format for easy access while traveling.
6. AI Chatbot: Get real-time assistance from our AI-powered chatbot for any travel-related questions or recommendations.


## Future Work
1. Enhanced Recommendations: Integrate more advanced recommendation algorithms or external APIs to offer better travel suggestions and dynamic pricing for hotels and activities.
2. Google Maps Integration: Show locations on the app using the Google Maps API, helping users visualize and group places based on proximity.
3. User Reviews & Ratings: Allow users to leave reviews and ratings for destinations and hotels to improve recommendations.
4. Personalized Notifications: Implement notifications for trip reminders and travel updates.
5. Scalability & Deployment: Deploy the app to a cloud-based platform and explore advanced database solutions as the user base grows.


## Tech Stack

1. Frontend: HTML, CSS, JavaScript (Jinja templating for dynamic content)
2. Backend: Flask (Python)
3. Database: SQLite (local database using SQLAlchemy ORM)


## Libraries & Tools:

1. `pandas`: Data manipulation and analysis

2. `Flask-SQLAlchemy`: Database management

3. `ReportLab`: PDF generation for itinerary downloads

4. `werkzeug.security`: Password hashing for user authentication


## Deployment

Clone this repository:

```bash
  https://github.com/Reyna2130/Travel.git
```

Navigate into the project directory:

```bash
    cd Travel
```

Install the required dependencies:
```bash
    pip install -r requirements.txt
```

Run the recommendation.py once:
```bash
    python recommendation.py
```
    
Run the Flask application:
```bash
    flask run
```


## Usage
1. Register or log in to start using TripGenie.
2. Search for a destination, input your travel duration, and budget to generate a personalized itinerary.
3. Save your itinerary, download it as a PDF, or view and manage your saved plans in your profile.
4. Use the AI chatbot for quick travel assistance or recommendations.


## Dataset

1. City.csv: Contains data on various cities used for destination recommendations.
2. google_hotel_data_clean_v2.csv: Provides information on hotels, including facilities and ratings.
3. merged_file.csv: A merged dataset combining relevant data for recommendations.
4. Places.csv: Includes details on various places of interest.
5. Places_decoded.csv: Contains additional decoded information for places of interest(Use tempCodeRunnerFile.py file on Places.csv to generate this file).
   

## Documentation

Documentation is available here: [Documentaion.pdf](Documentation.pdf)


## Contributing

Contributions are always welcome!

Feel free to fork the repository and create a pull request to contribute to this project. For major changes, please open an issue first to discuss what you would like to change.
