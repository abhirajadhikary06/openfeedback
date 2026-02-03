from flask import Flask, render_template, request, jsonify, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy
from auth import auth_bp, login_required, admin_required
from werkzeug.security import generate_password_hash, check_password_hash
import os
from datetime import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'openfeed-secret'  # Keep your existing secret key
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///openfeed.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# Register the authentication blueprint
app.register_blueprint(auth_bp, url_prefix='/auth')

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

# User model for authentication
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(200), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    is_admin = db.Column(db.Boolean, default=False)
    
    # Relationship with feedback
    feedbacks = db.relationship('Feedback', backref='user', lazy=True)

# Updated Feedback model with user relationship
class Feedback(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=True)  # nullable for existing data
    company_name = db.Column(db.String(100), nullable=False)
    company_logo = db.Column(db.String(500))
    comment = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20), nullable=False)
    status = db.Column(db.String(20), default='pending')  # pending, approved, rejected
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
    # Only show approved feedback or all feedback if user is admin
    if session.get('is_admin'):
        feedbacks = Feedback.query.order_by(Feedback.date_created.desc()).all()
    else:
        feedbacks = Feedback.query.filter_by(status='approved').order_by(Feedback.date_created.desc()).all()
    
    return render_template('index.html', feedbacks=feedbacks, companies=COMPANIES)

@app.route('/api/feedback/filter', methods=['GET'])
def filter_feedback():
    """API endpoint to get filtered feedback"""
    # Get query parameters
    search = request.args.get('search', '').lower()
    sentiment = request.args.get('sentiment', '')
    company = request.args.get('company', '')
    sort_by = request.args.get('sort', 'recent')
    
    # Base query - only show approved feedback unless admin
    if session.get('is_admin'):
        query = Feedback.query
    else:
        query = Feedback.query.filter_by(status='approved')
    
    # Apply filters
    if search:
        query = query.filter(
            db.or_(
                Feedback.company_name.ilike(f'%{search}%'),
                Feedback.comment.ilike(f'%{search}%')
            )
        )
    
    if sentiment:
        query = query.filter_by(sentiment=sentiment)
    
    if company:
        query = query.filter_by(company_name=company)
    
    # Apply sorting
    if sort_by == 'oldest':
        query = query.order_by(Feedback.date_created.asc())
    elif sort_by == 'helpful':
        # For now, sort by ID as a proxy for helpful (could be extended with actual helpful votes)
        query = query.order_by(Feedback.id.desc())
    else:  # recent (default)
        query = query.order_by(Feedback.date_created.desc())
    
    feedbacks = query.all()
    
    # Convert to JSON
    feedback_list = []
    for feedback in feedbacks:
        feedback_list.append({
            'id': feedback.id,
            'company_name': feedback.company_name,
            'company_logo': feedback.company_logo,
            'comment': feedback.comment,
            'sentiment': feedback.sentiment,
            'date_created': feedback.date_created.isoformat() if feedback.date_created else None
        })
    
    return jsonify({
        'success': True,
        'feedbacks': feedback_list,
        'total': len(feedback_list)
    })

@app.route('/submit_feedback', methods=['POST'])
@login_required  # Now requires login to submit feedback
def submit_feedback():
    data = request.json
    company_name = data['company']
    comment = data['comment']

    # Get company logo from static folder
    logo = get_company_logo(company_name)

    # Analyze sentiment
    sentiment = analyze_sentiment(comment)

    # Save feedback with user_id
    feedback = Feedback(
        user_id=session.get('user_id'),  # Link feedback to logged-in user
        company_name=company_name,
        company_logo=logo,
        comment=comment,
        sentiment=sentiment,
        status='pending'  # Set to pending for moderation
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
            'sentiment': sentiment,
            'status': feedback.status
        }
    })

# New routes for user features
@app.route('/my-feedback')
@login_required
def my_feedback():
    """View logged-in user's feedback submissions"""
    user_feedbacks = Feedback.query.filter_by(user_id=session.get('user_id')).order_by(Feedback.date_created.desc()).all()
    return render_template('my_feedback.html', feedbacks=user_feedbacks, companies=COMPANIES)

@app.route('/admin/moderate')
@admin_required
def moderate_feedback():
    """Admin page to moderate pending feedback"""
    pending_feedbacks = Feedback.query.filter_by(status='pending').order_by(Feedback.date_created.desc()).all()
    return render_template('moderate.html', feedbacks=pending_feedbacks)

@app.route('/admin/moderate/<int:feedback_id>/<action>', methods=['POST'])
@admin_required
def moderate_action(feedback_id, action):
    """Approve or reject feedback"""
    if action not in ['approve', 'reject']:
        return jsonify({'success': False, 'message': 'Invalid action'}), 400
    
    feedback = Feedback.query.get_or_404(feedback_id)
    feedback.status = 'approved' if action == 'approve' else 'rejected'
    db.session.commit()
    
    return jsonify({
        'success': True,
        'message': f'Feedback {feedback.status} successfully!',
        'status': feedback.status
    })

# Template context processor to make user info available in all templates
@app.context_processor
def inject_user():
    """Make user info available in all templates"""
    if 'user_id' in session:
        user = User.query.get(session['user_id'])
        return {
            'logged_in': True,
            'current_user': session.get('username'),
            'is_admin': session.get('is_admin', False),
            'user': user
        }
    return {'logged_in': False, 'user': None}

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
        
        # Create default admin user if not exists
        admin = User.query.filter_by(username='admin').first()
        if not admin:
            admin = User(
                username='admin',
                email='admin@openfeed.com',
                password_hash=generate_password_hash('admin123'),
                is_admin=True
            )
            db.session.add(admin)
            db.session.commit()
            print(" Default admin user created (username: admin, password: admin123)")
            print("  IMPORTANT: Change this password after first login!")
    
    app.run(host='0.0.0.0', port=5000, debug=True)