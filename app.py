from flask import Flask, render_template, request, jsonify
from flask_sqlalchemy import SQLAlchemy
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'openfeed-secret'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openfeed.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Companies list with local logo paths
COMPANIES = [
    {"name": "Google", "domain": "google.com", "logo": "static/logos/google.png"},
    {"name": "Apple", "domain": "apple.com", "logo": "static/logos/apple.png"},
    {"name": "Microsoft", "domain": "microsoft.com", "logo": "static/logos/microsoft.png"},
    {"name": "Amazon", "domain": "amazon.com", "logo": "static/logos/amazon.png"},
    {"name": "Netflix", "domain": "netflix.com", "logo": "static/logos/netflix.png"},
    {"name": "Tesla", "domain": "tesla.com", "logo": "static/logos/tesla.png"},
    {"name": "Meta", "domain": "meta.com", "logo": "static/logos/meta.png"},
    {"name": "Twitter", "domain": "twitter.com", "logo": "static/logos/twitter.png"},
    {"name": "Uber", "domain": "uber.com", "logo": "static/logos/uber.png"},
    {"name": "Adobe", "domain": "adobe.com", "logo": "static/logos/adobe.png"}
]

class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    company_name = db.Column(db.String(100), nullable=False)
    company_logo = db.Column(db.String(500))
    comment = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

def get_company_logo(company_name):
    """Get company logo from static folder"""
    company = next((c for c in COMPANIES if c['name'] == company_name), None)
    if company and os.path.exists(company['logo']):
        return f"/{company['logo']}"
    return "/static/logos/placeholder.png"

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
    return render_template('index.html', feedbacks=feedbacks, companies=COMPANIES)

@app.route('/submit_feedback', methods=['POST'])
def submit_feedback():
    data = request.json
    company_name = data['company']
    comment = data['comment']

    # Get company logo from static folder
    logo = get_company_logo(company_name)

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
    app.run(host='0.0.0.0', port=5000, debug=True)
