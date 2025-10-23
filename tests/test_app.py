import pytest
from app import app, db, COMPANIES
from unittest.mock import patch, MagicMock


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
    assert b'<div class="hof-container">' in response.data


def test_submit_feedback_valid_data(client):
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


@patch('app.requests.head')
def test_get_company_logo_success(mock_head, client):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_head.return_value = mock_response
    from app import get_company_logo
    logo = get_company_logo('google.com')
    assert 'img.logo.dev' in logo


@patch('app.requests.head')
def test_get_company_logo_failure(mock_head, client):
    mock_head.side_effect = Exception('Connection error')
    from app import get_company_logo
    logo = get_company_logo('test.com')
    assert 'via.placeholder.com' in logo


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