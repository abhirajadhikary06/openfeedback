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

# Vote model for feedback voting system
class Vote(db.Model):
    """Represents a user's vote on a feedback item"""
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id', ondelete='CASCADE'), nullable=False)
    feedback_id = db.Column(db.Integer, db.ForeignKey('feedback.id', ondelete='CASCADE'), nullable=False)
    vote_type = db.Column(db.String(10), nullable=False)  # 'upvote' or 'downvote'
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    user = db.relationship('User', backref='votes')
    feedback = db.relationship('Feedback', backref='votes')
    
    # Constraints
    __table_args__ = (
        db.UniqueConstraint('user_id', 'feedback_id', name='unique_user_feedback_vote'),
    )

def get_vote_score(feedback_id):
    """Calculate vote score for a feedback item (upvotes - downvotes)"""
    upvotes = db.session.query(Vote).filter_by(
        feedback_id=feedback_id,
        vote_type='upvote'
    ).count()
    
    downvotes = db.session.query(Vote).filter_by(
        feedback_id=feedback_id,
        vote_type='downvote'
    ).count()
    
    return upvotes - downvotes

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
        # Sort by vote score (upvotes - downvotes) in descending order
        # Use a subquery to calculate vote scores
        from sqlalchemy import func, case
        
        vote_score_subquery = db.session.query(
            Vote.feedback_id,
            func.sum(
                case(
                    (Vote.vote_type == 'upvote', 1),
                    (Vote.vote_type == 'downvote', -1),
                    else_=0
                )
            ).label('vote_score')
        ).group_by(Vote.feedback_id).subquery()
        
        # Join with vote scores and order by score (descending), then by date (descending) for ties
        query = query.outerjoin(
            vote_score_subquery,
            Feedback.id == vote_score_subquery.c.feedback_id
        ).order_by(
            vote_score_subquery.c.vote_score.desc().nullslast(),
            Feedback.date_created.desc()
        )
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

# Vote submission endpoint
@app.route('/api/vote', methods=['POST'])
@login_required
def submit_vote():
    """Submit or update a vote on feedback"""
    try:
        data = request.json
        feedback_id = data.get('feedback_id')
        vote_type = data.get('vote_type')
        
        # Validate request body
        if not feedback_id or not vote_type:
            return jsonify({
                'success': False,
                'error': 'Missing required fields: feedback_id and vote_type'
            }), 400
        
        if vote_type not in ['upvote', 'downvote']:
            return jsonify({
                'success': False,
                'error': 'Invalid vote_type. Must be "upvote" or "downvote"'
            }), 400
        
        # Check if feedback exists
        feedback = Feedback.query.get(feedback_id)
        if not feedback:
            return jsonify({
                'success': False,
                'error': 'Feedback not found'
            }), 404
        
        # Check if user owns the feedback
        if feedback.user_id == session.get('user_id'):
            return jsonify({
                'success': False,
                'error': 'Cannot vote on your own feedback'
            }), 403
        
        # Check for existing vote
        existing_vote = db.session.query(Vote).filter_by(
            user_id=session.get('user_id'),
            feedback_id=feedback_id
        ).first()
        
        if existing_vote:
            # Update existing vote
            existing_vote.vote_type = vote_type
            existing_vote.updated_at = datetime.utcnow()
        else:
            # Create new vote
            new_vote = Vote(
                user_id=session.get('user_id'),
                feedback_id=feedback_id,
                vote_type=vote_type
            )
            db.session.add(new_vote)
        
        db.session.commit()
        
        # Calculate updated vote score
        vote_score = get_vote_score(feedback_id)
        
        return jsonify({
            'success': True,
            'vote': {
                'feedback_id': feedback_id,
                'vote_type': vote_type,
                'vote_score': vote_score
            }
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'An error occurred while processing your vote'
        }), 500

# Vote removal endpoint
@app.route('/api/vote/<int:feedback_id>', methods=['DELETE'])
@login_required
def remove_vote(feedback_id):
    """Remove a vote from feedback"""
    try:
        # Find user's vote for this feedback
        vote = db.session.query(Vote).filter_by(
            user_id=session.get('user_id'),
            feedback_id=feedback_id
        ).first()
        
        if not vote:
            return jsonify({
                'success': False,
                'error': 'Vote not found'
            }), 404
        
        # Delete the vote
        db.session.delete(vote)
        db.session.commit()
        
        # Calculate updated vote score
        vote_score = get_vote_score(feedback_id)
        
        return jsonify({
            'success': True,
            'vote_score': vote_score
        })
        
    except Exception as e:
        db.session.rollback()
        return jsonify({
            'success': False,
            'error': 'An error occurred while removing your vote'
        }), 500

# Get vote data for a specific feedback item
@app.route('/api/feedback/<int:feedback_id>/votes', methods=['GET'])
def get_feedback_votes(feedback_id):
    """Get vote information for a specific feedback item"""
    try:
        # Check if feedback exists
        feedback = db.session.get(Feedback, feedback_id)
        if not feedback:
            return jsonify({
                'success': False,
                'error': 'Feedback not found'
            }), 404
        
        # Calculate vote counts
        upvotes = db.session.query(Vote).filter_by(
            feedback_id=feedback_id,
            vote_type='upvote'
        ).count()
        
        downvotes = db.session.query(Vote).filter_by(
            feedback_id=feedback_id,
            vote_type='downvote'
        ).count()
        
        vote_score = upvotes - downvotes
        
        # Get user's vote if authenticated
        user_vote = None
        if 'user_id' in session:
            user_vote_record = db.session.query(Vote).filter_by(
                user_id=session.get('user_id'),
                feedback_id=feedback_id
            ).first()
            if user_vote_record:
                user_vote = user_vote_record.vote_type
        
        return jsonify({
            'success': True,
            'vote_score': vote_score,
            'upvotes': upvotes,
            'downvotes': downvotes,
            'user_vote': user_vote
        })
        
    except Exception as e:
        print(f"Error in get_feedback_votes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching vote data'
        }), 500

# Get vote data for all feedback items
@app.route('/api/feedback/votes', methods=['GET'])
def get_all_feedback_votes():
    """Get vote information for all feedback items"""
    try:
        # Get all feedback IDs from the current page
        # In a real implementation, you might want to filter by status or other criteria
        if session.get('is_admin'):
            feedbacks = Feedback.query.all()
        else:
            feedbacks = Feedback.query.filter_by(status='approved').all()
        
        votes_data = {}
        user_id = session.get('user_id')
        
        for feedback in feedbacks:
            try:
                # Calculate vote counts
                upvotes = db.session.query(Vote).filter_by(
                    feedback_id=feedback.id,
                    vote_type='upvote'
                ).count()
                
                downvotes = db.session.query(Vote).filter_by(
                    feedback_id=feedback.id,
                    vote_type='downvote'
                ).count()
                
                vote_score = upvotes - downvotes
                
                # Get user's vote if authenticated
                user_vote = None
                if user_id:
                    user_vote_record = db.session.query(Vote).filter_by(
                        user_id=user_id,
                        feedback_id=feedback.id
                    ).first()
                    if user_vote_record:
                        user_vote = user_vote_record.vote_type
                
                votes_data[str(feedback.id)] = {
                    'vote_score': vote_score,
                    'upvotes': upvotes,
                    'downvotes': downvotes,
                    'user_vote': user_vote
                }
            except Exception as feedback_error:
                # Log error but continue with other feedback
                print(f"Error processing feedback {feedback.id}: {feedback_error}")
                continue
        
        return jsonify({
            'success': True,
            'votes': votes_data
        })
        
    except Exception as e:
        print(f"Error in get_all_feedback_votes: {e}")
        import traceback
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': 'An error occurred while fetching vote data'
        }), 500

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