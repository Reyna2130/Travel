from flask import Flask, render_template, request, send_file
import pandas as pd
import re
from io import BytesIO
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak

app = Flask(__name__)

# Load the data
places_df = pd.read_csv('dataset/Places_decoded.csv')
cities_df = pd.read_csv('dataset/City.csv')

def truncate_description(description, sentence_limit=2):
    """ Truncate description to a given number of sentences and remove leading special characters. """
    description = re.sub(r'^["\[\s]+', '', description)
    sentences = description.split('.')
    truncated_sentences = sentences[:sentence_limit]
    return '. '.join(truncated_sentences).strip() + ('.' if sentences[:sentence_limit] else '')

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/chatbot')
def chatbot():
    return render_template('indexchatbot.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    if request.method == 'POST':
        city_name = request.form['city_name']
        duration_days = int(request.form['duration_days'])

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

            return render_template(
                'results.html',
                city_name=city_name,
                duration_days=duration_days,
                city_desc=city_desc,
                ideal_duration=ideal_duration,
                best_time=best_time,
                places=places
            )
        else:
            return render_template('index.html', error="City not found")

    return render_template('index.html')

@app.route('/download_pdf', methods=['POST'])
def download_pdf():
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

if __name__ == '__main__':
    app.run(debug=True)
