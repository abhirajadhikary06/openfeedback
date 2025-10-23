from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import requests
import os
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

app = Flask(__name__)
app.config['SECRET_KEY'] = 'openfeed-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openfeed.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Logo.dev token from environment
LOGO_DEV_TOKEN = os.getenv('LOGO_DEV_TOKEN')

# Companies list
COMPANIES = [
    {"name": "Google", "domain": "google.com"},
    {"name": "Apple", "domain": "apple.com"},
    {"name": "Microsoft", "domain": "microsoft.com"},
    {"name": "Amazon", "domain": "amazon.com"},
    {"name": "Netflix", "domain": "netflix.com"},
    {"name": "Tesla", "domain": "tesla.com"},
    {"name": "Facebook", "domain": "facebook.com"},
    {"name": "Twitter", "domain": "twitter.com"},
    {"name": "Spotify", "domain": "spotify.com"},
    {"name": "Uber", "domain": "uber.com"}
]


class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_logo = db.Column(db.String(500))
    comment = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)


def get_company_logo(domain):
    """Get company logo using Logo.dev API"""
    if not LOGO_DEV_TOKEN:
        return (
            f"https://via.placeholder.com/50x50/4285f4/ffffff?"
            f"text={domain[0].upper()}"
        )

    try:
        logo_url = f"https://img.logo.dev/{domain}?token={LOGO_DEV_TOKEN}"
        response = requests.head(logo_url, timeout=5)
        if response.status_code == 200:
            return logo_url
    except Exception:
        pass
    return (
        f"https://via.placeholder.com/50x50/4285f4/ffffff?"
        f"text={domain[0].upper()}"
    )


def analyze_sentiment(text):
    """Simple sentiment analysis"""
    positive_words = [
        'great', 'excellent', 'amazing', 'love', 'perfect', 'awesome',
        'good', 'fantastic'
    ]
    negative_words = [
        'bad', 'terrible', 'awful', 'hate', 'worst', 'poor',
        'disappointing'
    ]

    text_lower = text.lower()
    pos_score = sum(1 for word in positive_words if word in text_lower)
    neg_score = sum(1 for word in negative_words if word in text_lower)

    if pos_score > neg_score:
        return "positive"
    elif neg_score > pos_score:
        return "negative"
    else:
        return "neutral"


@app.route('/')
def index():
    feedbacks = Feedback.query.order_by(Feedback.date_created.desc()).all()
    return render_template('index.html', feedbacks=feedbacks,
                          companies=COMPANIES)


@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    company_name = data['company']
    comment = data['comment']

    # Get company logo
    company = next((c for c in COMPANIES if c['name'] == company_name), None)
    logo = get_company_logo(company['domain']) if company else ""

    # Analyze sentiment
    sentiment = analyze_sentiment(comment)

    # Save feedback
    feedback = Feedback(
        company_name=company_name,
        company_logo=logo,
        comment=comment,
        sentiment=sentiment
    )
    db.session.add(feedback)
    db.session.commit()

    return jsonify({
        'success': True,
        'feedback': {
            'id': feedback.id,
            'company_name': company_name,
            'company_logo': logo,
            'comment': comment,
            'sentiment': sentiment
        }
    })


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
