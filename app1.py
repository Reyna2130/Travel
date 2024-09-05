from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

# Machine Learning Libraries
import numpy as np
from sklearn.preprocessing import LabelEncoder, StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split

app = Flask(__name__)
app.config['SECRET_KEY'] = '770b0b8509abe280460e773fb9e4cb36c6f8d3271dcfdae3'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

with app.app_context():
    db.create_all()

# Load the data
places_df = pd.read_csv('dataset/Places_decoded.csv')
cities_df = pd.read_csv('dataset/City.csv')
hotel_df = pd.read_csv('dataset/google_hotel_data_clean_v2.csv')  

# Train the machine learning model
label_encoder = LabelEncoder()
hotel_df['City_Encoded'] = label_encoder.fit_transform(hotel_df['City'])

# Prepare features and target variable
X = hotel_df[['City_Encoded', 'Hotel_Price']]
y = hotel_df['Hotel_Name']

# Split the data into training and testing sets (for demonstration purposes)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Standardize the features
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Train the RandomForest model
rf_model = RandomForestClassifier()
rf_model.fit(X_train, y_train)

def truncate_description(description, sentence_limit=2):
    """ Truncate description to a given number of sentences and remove leading special characters. """
    description = re.sub(r'^["\[\s]+', '', description)
    sentences = description.split('.')
    truncated_sentences = sentences[:sentence_limit]
    return '. '.join(truncated_sentences).strip() + ('.' if sentences[:sentence_limit] else '')

def predict_hotel(city, price):
    """ Predict hotel based on city and price using the trained model """
    city_encoded = label_encoder.transform([city])[0]  # Encode city
    input_features = pd.DataFrame([[city_encoded, price]], columns=['City_Encoded', 'Hotel_Price'])
    input_features = scaler.transform(input_features)  # Standardize input
    predicted_hotel = rf_model.predict(input_features)
    return predicted_hotel[0]

@app.route('/')
def home():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('indexchatbot.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    if request.method == 'POST':
        city_name = request.form['city_name']
        duration_days = int(request.form['duration_days'])
        hotel_price = float(request.form['hotel_price'])  # Get hotel price from user input

        # Get city information
        city_info = cities_df[cities_df['City'].str.lower() == city_name.lower()]

        if not city_info.empty:
            city_info = city_info.iloc[0]
            city_desc = truncate_description(city_info['City_desc'])
            ideal_duration = city_info['Ideal_duration']
            best_time = city_info['Best_time_to_visit']

            # Filter places for the selected city
            city_places_df = places_df[places_df['City'].str.lower() == city_name.lower()]
            sorted_city_places_df = city_places_df.sort_values(by='Ratings', ascending=False)
            places_per_day = 3
            total_places_needed = duration_days * places_per_day
            top_places_df = sorted_city_places_df.head(total_places_needed)

            # Predict hotel based on city and price
            recommended_hotel = predict_hotel(city_name, hotel_price)

            # Prepare places for each day
            places = [top_places_df.iloc[day * places_per_day : (day + 1) * places_per_day].to_dict('records') for day in range(duration_days)]

            return render_template(
                'results.html',
                city_name=city_name,
                duration_days=duration_days,
                city_desc=city_desc,
                ideal_duration=ideal_duration,
                best_time=best_time,
                places=places,
                recommended_hotel=recommended_hotel  # Pass the recommended hotel to the template
            )
        else:
            return render_template('index.html', error="City not found")

    return render_template('index.html')

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    city_name = request.form['city_name']
    city_desc = request.form['city_desc']
    duration_days = int(request.form['duration_days'])
    places = request.form.getlist('places[]')

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []

    # Define styles
    styles = getSampleStyleSheet()
    title_style = styles['Title']
    normal_style = styles['Normal']
    
    # Add content
    elements.append(Paragraph(f"Places to Visit in {city_name}", title_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Description: {city_desc}", normal_style))
    elements.append(Spacer(1, 12))
    elements.append(Paragraph(f"Ideal Duration: {duration_days} days", normal_style))
    elements.append(Spacer(1, 24))

    for i, place in enumerate(places, 1):
        elements.append(Paragraph(f"{i}. {place}", normal_style))
        elements.append(Spacer(1, 12))
        if len(elements) > 30:  # Start a new page if there's no space
            elements.append(PageBreak())

    doc.build(elements)

    buffer.seek(0)
    return send_file(buffer, as_attachment=True, download_name=f"{city_name}_places.pdf", mimetype='application/pdf')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id
            return redirect(url_for('home'))  # Redirect to the 'home' route after successful login
        else:
            return render_template('login.html', error='Invalid email or password')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = generate_password_hash(request.form['password'])
        user = User(username=username, email=email, password=password)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('login'))
    return render_template('register.html')  # Adjust this to render a registration page, if you have one

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
