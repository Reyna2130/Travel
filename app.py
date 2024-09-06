from flask import Flask, render_template, request, redirect, url_for, session, send_file
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
import pandas as pd
import re
import json
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key_here'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
db = SQLAlchemy(app)

# Define the User model
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

# Define the SavedPlan model
class SavedPlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    city_name = db.Column(db.String(100), nullable=False)
    city_desc = db.Column(db.Text, nullable=False)
    duration_days = db.Column(db.Integer, nullable=False)
    places = db.Column(db.Text, nullable=False)  # Stores JSON data

    user = db.relationship('User', backref=db.backref('saved_plans', lazy=True))

    def get_places(self):
        return json.loads(self.places)

with app.app_context():
    db.create_all()

# Load the data
places_df = pd.read_csv('dataset/Places_decoded.csv')
cities_df = pd.read_csv('dataset/City.csv')
merged_data = pd.read_csv('dataset/merged_file.csv')

def truncate_description(description, sentence_limit=2):
    """ Truncate description to a given number of sentences and remove leading special characters. """
    description = re.sub(r'^["\[\s]+', '', description)
    sentences = description.split('.')
    truncated_sentences = sentences[:sentence_limit]
    return '. '.join(truncated_sentences).strip() + ('.' if sentences[:sentence_limit] else '')

def recommend_hotels(city_input, min_price, max_price):
    city_input = city_input.lower()
    city_hotels = merged_data[merged_data['City'] == city_input]
    
    if city_hotels.empty:
        return f"No hotels found for city: {city_input.capitalize()}"
    
    price_filtered_hotels = city_hotels[
        (city_hotels['Hotel_Price'] >= min_price) & 
        (city_hotels['Hotel_Price'] <= max_price)
    ]
    
    if price_filtered_hotels.empty:
        return f"No hotels found in {city_input.capitalize()} within the price range: {min_price} - {max_price}"
    
    recommended_hotel_name = price_filtered_hotels.sort_values(by='Hotel_Rating', ascending=False)['Hotel_Name'].iloc[0]
    return recommended_hotel_name

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
        budget = float(request.form['budget'])

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

            # Prepare places for each day
            places = [top_places_df.iloc[day * places_per_day : (day + 1) * places_per_day].to_dict('records') for day in range(duration_days)]

            # Get hotel recommendation
            min_price = budget * 0.8
            max_price = budget * 1.2
            recommended_hotel = recommend_hotels(city_name, min_price, max_price)

            return render_template(
                'results.html',
                city_name=city_name,
                duration_days=duration_days,
                city_desc=city_desc,
                ideal_duration=ideal_duration,
                best_time=best_time,
                places=places,
                recommended_hotel=recommended_hotel  # Pass the hotel recommendation here
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
            return redirect(url_for('home'))
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
    return render_template('register.html')

@app.route('/logout')
def logout():
    session.pop('user_id', None)
    return redirect(url_for('login'))

@app.route('/discover_more')
def discover_more():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('discover_more.html')

@app.route('/profile')
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']
    user = User.query.get(user_id)  # Fetch user from the database
    if not user:
        return redirect(url_for('login'))
    
    saved_plans = SavedPlan.query.filter_by(user_id=user_id).all()

    user_name = user.username
    user_email = user.email

    plans = []
    for plan in saved_plans:
        plans.append({
            'city_name': plan.city_name,
            'city_desc': plan.city_desc,
            'duration_days': plan.duration_days,
            'places': plan.get_places()  # Use the get_places method to decode JSON
        })

    return render_template('profile.html', user_name=user_name, user_email=user_email, saved_plans=plans)

@app.route('/save_plan', methods=['POST'])
def save_plan():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    city_name = request.form['city_name']
    city_desc = request.form['city_desc']
    duration_days = int(request.form['duration_days'])
    places = request.form.getlist('places[]')

    user_id = session['user_id']

    # Create a new saved plan
    new_plan = SavedPlan(
        user_id=user_id,
        city_name=city_name,
        city_desc=city_desc,
        duration_days=duration_days,
        places=json.dumps(places)  # Convert list to JSON string
    )

    db.session.add(new_plan)
    db.session.commit()

    return redirect(url_for('profile'))

if __name__ == '__main__':
    app.run(debug=True)
