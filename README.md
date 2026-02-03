# Openfeed

Openfeed is an open feedback platform where users can submit and view company feedback in real-time. Features include sentiment analysis, company logos, and a responsive card-based interface.

## Features

- Submit feedback for 30+ major companies

- Automatic sentiment analysis (positive/neutral/negative)

- Real-time feedback cards with hover animations

- Responsive design for mobile and desktop

- Local logo storage for instant loading

- SQLite database for persistence

## Quick Start

```bash

pip install -r requirements.txt

python app.py

```

Visit `http://localhost:5000`

## Tech Stack

- Flask (Python web framework)

- Flask-SQLAlchemy (database ORM)

- SQLite (lightweight database)

- HTML/CSS/JavaScript (frontend)

- Docker (containerization)

## Architecture Diagram

```mermaid
flowchart TD
    A[User/Visitor] -->|Browse| B[Frontend - HTML/CSS/JS]
    A -->|Register/Login| C[Auth Module]
    
    C -->|Authenticate| D[Session Management]
    D -->|Valid Session| E[User Dashboard]
    
    E -->|Submit Feedback| F[Flask Backend]
    B -->|View Public Feedback| F
    
    F -->|Analyze Text| G[Sentiment Analysis Engine]
    G -->|positive/negative/neutral| F
    
    F -->|Save| H[(SQLite Database)]
    F -->|Retrieve| H
    
    H -->|Store| I[User Data]
    H -->|Store| J[Feedback Data]
    
    K[Admin User] -->|Access| L[Admin Dashboard]
    L -->|Moderate| M[Pending Feedback Queue]
    M -->|Approve/Reject| H
    
    F -->|Filter & Search| N[API Endpoints]
    N -->|Return JSON| B
    
    F -->|Company Logos| O[Static Assets]
    O -->|Serve Images| B
    
    style A fill:#4A90E2,stroke:#2E5C8A,stroke-width:2px,color:#fff
    style K fill:#E24A4A,stroke:#8A2E2E,stroke-width:2px,color:#fff
    style B fill:#9B59B6,stroke:#6C3483,stroke-width:2px,color:#fff
    style C fill:#E67E22,stroke:#A04000,stroke-width:2px,color:#fff
    style D fill:#1ABC9C,stroke:#117A65,stroke-width:2px,color:#fff
    style E fill:#3498DB,stroke:#21618C,stroke-width:2px,color:#fff
    style F fill:#E74C3C,stroke:#943126,stroke-width:2px,color:#fff
    style G fill:#2ECC71,stroke:#1E8449,stroke-width:2px,color:#fff
    style H fill:#F39C12,stroke:#B9770E,stroke-width:2px,color:#fff
    style I fill:#16A085,stroke:#0E6655,stroke-width:2px,color:#fff
    style J fill:#8E44AD,stroke:#5B2C6F,stroke-width:2px,color:#fff
    style L fill:#C0392B,stroke:#78281F,stroke-width:2px,color:#fff
    style M fill:#D35400,stroke:#873600,stroke-width:2px,color:#fff
    style N fill:#27AE60,stroke:#186A3B,stroke-width:2px,color:#fff
    style O fill:#2980B9,stroke:#1B4F72,stroke-width:2px,color:#fff
```

**Flow Description:**
1. **User Registration/Login**: Users authenticate via the auth module with session management
2. **Feedback Submission**: Logged-in users submit feedback for companies
3. **Sentiment Analysis**: Text is automatically analyzed for positive/negative/neutral sentiment
4. **Database Storage**: All data persists in SQLite database
5. **Admin Moderation**: Admins review and approve/reject pending feedback
6. **Public Display**: Approved feedback is displayed to all visitors with filtering and search capabilities

## Project Structure

```

openfeed/

├── app.py              # Main Flask application

├── requirements.txt    # Python dependencies

├── Dockerfile          # Docker configuration

├── static/             # CSS, JS, logos

├── templates/          # HTML templates

├── tests/              # Unit tests

├── .github/workflows/  # GitHub Actions CI/CD

└── .gitlab-ci.yml      # GitLab CI/CD

```

## Working on a Branch (GitHub)

1. Fetch latest: `git fetch origin`
2. Update main then branch: `git checkout main && git pull origin main && git checkout -b feature/your-branch` (or if already on an updated main: `git checkout -b feature/your-branch`)
3. Commit locally: `git add .` then `git commit -m "feat: describe change"`
4. Push branch: `git push -u origin feature/your-branch`
5. Open a pull request on GitHub targeting `main`.

## CI/CD Pipelines

- Automated testing with pytest

- Docker image builds

- GitHub Actions + GitLab CI/CD support

## Companies Supported

Google, Apple, Microsoft, Amazon, Netflix, Tesla, Facebook, Twitter, Spotify, and 22 more.

## Contributors

Thanks to all the amazing contributors who have helped make this project better! 🎉

<a href="https://github.com/rudrabhowmick/openfeedback/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=rudrabhowmick/openfeedback" />
</a>

Made with [contrib.rocks](https://contrib.rocks).

## License
MIT License