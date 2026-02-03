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

# Test COMPANIES data to be removed in future refactor
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


def test_filter_feedback_api(client):
    # Create test feedback data
    from app import Feedback, User
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
        
        # Create test feedback
        feedback1 = Feedback(
            user_id=test_user.id,
            company_name='Google',
            company_logo='/static/logos/google.png',
            comment='Great service!',
            sentiment='positive',
            status='approved'
        )
        feedback2 = Feedback(
            user_id=test_user.id,
            company_name='Apple',
            company_logo='/static/logos/apple.png',
            comment='Poor experience',
            sentiment='negative',
            status='approved'
        )
        db.session.add(feedback1)
        db.session.add(feedback2)
        db.session.commit()
    
    # Test filter by sentiment
    response = client.get('/api/feedback/filter?sentiment=positive')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']
    assert len(json_data['feedbacks']) == 1
    assert json_data['feedbacks'][0]['sentiment'] == 'positive'
    
    # Test filter by company
    response = client.get('/api/feedback/filter?company=Apple')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']
    assert len(json_data['feedbacks']) == 1
    assert json_data['feedbacks'][0]['company_name'] == 'Apple'
    
    # Test search
    response = client.get('/api/feedback/filter?search=great')
    assert response.status_code == 200
    json_data = response.get_json()
    assert json_data['success']
    assert len(json_data['feedbacks']) == 1
    assert 'Great' in json_data['feedbacks'][0]['comment']