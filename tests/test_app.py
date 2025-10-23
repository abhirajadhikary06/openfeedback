import pytest
from app import app, db, Feedback
from app import analyze_sentiment, get_company_logo, COMPANIES

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

def test_analyze_sentiment_positive(client):
    result = analyze_sentiment("This is great and awesome!")
    assert result == "positive"

def test_analyze_sentiment_negative(client):
    result = analyze_sentiment("This is terrible and awful!")
    assert result == "negative"

def test_analyze_sentiment_neutral(client):
    result = analyze_sentiment("This is okay.")
    assert result == "neutral"

def test_companies_list(client):
    assert len(COMPANIES) == 10
    assert COMPANIES[0]["name"] == "Google"

def test_index_page(client):
    response = client.get('/')
    assert response.status_code == 200

def test_submit_feedback(client):
    data = {
        'company': 'Google',
        'comment': 'Great product!'
    }
    
    response = client.post('/submit_feedback', json=data)
    assert response.status_code == 200
    
    json_data = response.get_json()
    assert json_data['success'] is True