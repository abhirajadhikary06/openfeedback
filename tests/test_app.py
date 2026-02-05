import os
import sys

# Add the parent directory to sys.path to allow importing app module
parent_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, parent_dir)

import pytest
from unittest.mock import patch, MagicMock
from app import app, db, COMPANIES


@pytest.fixture
def client():
    app.config['TESTING'] = True
    app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
    with app.test_client() as client:
        with app.app_context():
            db.create_all()
        yield client
        with app.app_context():
            db.drop_all()


def test_index_returns_html(client):
    response = client.get('/')
    assert response.status_code == 200
    assert b'<div class="feedback-grid"' in response.data


def test_submit_feedback_valid_data(client):
    # First create a test user and log them in
    from app import User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Create a test user
        test_user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            is_admin=False
        )
        db.session.add(test_user)
        db.session.commit()
        
        # Log in the test user
        with client.session_transaction() as sess:
            sess['user_id'] = test_user.id
            sess['username'] = test_user.username
            sess['is_admin'] = test_user.is_admin
    
    data = {
        'company': 'Google',
        'comment': 'Great product!'
    }
    response = client.post('/submit_feedback',
                           json=data,
                           content_type='application/json')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']


def test_companies_list_not_empty():
    assert len(COMPANIES) > 0
    assert COMPANIES[0]['name'] == 'Google'


def test_analyze_sentiment_positive():
    from app import analyze_sentiment
    result = analyze_sentiment('This is great and awesome!')
    assert result == 'positive'


def test_analyze_sentiment_negative():
    from app import analyze_sentiment
    result = analyze_sentiment('This is terrible and awful!')
    assert result == 'negative'


def test_analyze_sentiment_neutral():
    from app import analyze_sentiment
    result = analyze_sentiment('This is okay.')
    assert result == 'neutral'


def test_vote_feedback(client):
    # Create test users and feedback
    from app import Feedback, User, Vote
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Create test users
        user1 = User(
            username='user1',
            email='user1@example.com',
            password_hash=generate_password_hash('testpass'),
            is_admin=False
        )
        user2 = User(
            username='user2',
            email='user2@example.com',
            password_hash=generate_password_hash('testpass'),
            is_admin=False
        )
        db.session.add(user1)
        db.session.add(user2)
        db.session.commit()
        
        # Create test feedback by user1
        feedback = Feedback(
            user_id=user1.id,
            company_name='Google',
            company_logo='/static/logos/google.png',
            comment='Great service!',
            sentiment='positive',
            status='approved'
        )
        db.session.add(feedback)
        db.session.commit()
        
        feedback_id = feedback.id  # Store the ID
        
        # Log in as user2
        with client.session_transaction() as sess:
            sess['user_id'] = user2.id
            sess['username'] = user2.username
            sess['is_admin'] = user2.is_admin
    
    # Test upvote
    response = client.post('/api/vote', 
                          json={'feedback_id': feedback_id, 'vote_type': 1},
                          content_type='application/json')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']
    assert json_data['action'] == 'added'
    assert json_data['upvote_count'] == 1
    assert json_data['vote_score'] == 1


def test_vote_own_feedback_forbidden(client):
    # Test that users cannot vote on their own feedback
    from app import Feedback, User
    from werkzeug.security import generate_password_hash
    
    with app.app_context():
        # Create test user
        user = User(
            username='testuser',
            email='test@example.com',
            password_hash=generate_password_hash('testpass'),
            is_admin=False
        )
        db.session.add(user)
        db.session.commit()
        
        # Create feedback by the same user
        feedback = Feedback(
            user_id=user.id,
            company_name='Google',
            company_logo='/static/logos/google.png',
            comment='Great service!',
            sentiment='positive',
            status='approved'
        )
        db.session.add(feedback)
        db.session.commit()
        
        feedback_id = feedback.id  # Store the ID
        
        # Log in as the same user
        with client.session_transaction() as sess:
            sess['user_id'] = user.id
            sess['username'] = user.username
            sess['is_admin'] = user.is_admin
    
    # Try to vote on own feedback
    response = client.post('/api/vote',
                          json={'feedback_id': feedback_id, 'vote_type': 1},
                          content_type='application/json')
    assert response.status_code == 403
    json_data = response.get_json()
    assert not json_data['success']
    assert 'Cannot vote on your own feedback' in json_data['message']