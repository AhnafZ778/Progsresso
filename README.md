# HabitPulse 📊

A lightweight weekly habit tracking web application with progress visualization and AI-ready PDF reports.

## Features

- ✅ **Task Management**: Create habits with 5 metric types (Time, Count, Intensity, Progress %, Boolean)
- 📅 **Weekly Table**: Visual grid showing daily completion status
- 📈 **Progress Charts**: Weekly completion and 4-week trend visualization
- 🎨 **Health Indicators**: Color-coded rows based on 14-day performance
- 📄 **PDF Reports**: AI-ready format for personalized guidance

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: SQLite
- **Frontend**: HTML, TailwindCSS (CDN), Vanilla JavaScript
- **Charts**: Chart.js
- **PDF**: ReportLab

## Quick Start

```bash
# Navigate to project directory
cd habitpulse

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open http://localhost:5000 in your browser.

## Project Structure

```
habitpulse/
├── app.py                    # Flask application
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── database/                 # Database module
│   ├── db.py                 # Connection handling
│   └── schema.sql            # SQLite schema
├── routes/                   # API endpoints
│   ├── tasks.py              # Task CRUD
│   ├── progress.py           # Progress logging
│   └── reports.py            # PDF generation
├── services/                 # Business logic
│   ├── task_service.py       # Task operations
│   ├── progress_service.py   # Stats & health scores
│   └── pdf_service.py        # PDF generation
├── static/                   # Frontend assets
│   ├── css/styles.css
│   └── js/
├── templates/                # HTML templates
│   └── index.html
└── data/                     # Database file (auto-created)
```

## API Endpoints

| Method | Endpoint             | Description         |
| ------ | -------------------- | ------------------- |
| GET    | `/api/tasks`         | List all tasks      |
| POST   | `/api/tasks`         | Create task         |
| PUT    | `/api/tasks/<id>`    | Update task         |
| DELETE | `/api/tasks/<id>`    | Delete/archive task |
| GET    | `/api/progress/week` | Get week's progress |
| POST   | `/api/progress`      | Log progress        |
| GET    | `/api/reports/pdf`   | Download PDF report |

## License

MIT
