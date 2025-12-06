# Progresso 📊

A lightweight weekly habit tracking web application with progress visualization and AI-ready PDF reports.

## Features

- ✅ **Task Management**: Create habits with 5 metric types (Time, Count, Intensity, Progress %, Boolean)
- 📅 **Weekly Table**: Visual grid showing daily completion status
- 📈 **Progress Charts**: Weekly completion and 4-week trend visualization
- 🎨 **Health Indicators**: Color-coded rows based on 14-day performance
- 📄 **PDF Reports**: AI-ready format for personalized guidance
- 🗂️ **Kanban Board**: Organize tasks into TODO, In Progress, and Done columns
- ⏱️ **Focus Timer**: Pomodoro-style focus sessions with Rock Lee motivation!

## Tech Stack

- **Backend**: Flask (Python)
- **Database**: Supabase (PostgreSQL)
- **Frontend**: HTML, CSS, Vanilla JavaScript
- **Charts**: Chart.js
- **PDF**: ReportLab
- **Hosting**: Vercel

## Quick Start

```bash
# Navigate to project directory
cd progresso

# Create virtual environment
python -m venv venv

# Activate virtual environment
source venv/bin/activate  # Linux/Mac
# or
venv\Scripts\activate     # Windows

# Copy environment template and add your Supabase credentials
cp .env.example .env

# Install dependencies
pip install -r requirements.txt

# Run the application
python app.py
```

Open http://localhost:5500 in your browser.

## Supabase Setup

See [SUPABASE_SETUP.md](./SUPABASE_SETUP.md) for detailed instructions on:

1. Creating a Supabase project
2. Setting up the database schema
3. Configuring environment variables
4. Deploying to Vercel

## Project Structure

```
progresso/
├── app.py                    # Flask application
├── config.py                 # Configuration
├── requirements.txt          # Dependencies
├── vercel.json               # Vercel deployment config
├── api/
│   └── index.py              # Vercel serverless entry point
├── database/                 # Database module
│   ├── supabase_db.py        # Supabase connection
│   └── supabase_schema.sql   # PostgreSQL schema
├── routes/                   # API endpoints
│   ├── tasks.py              # Task CRUD
│   ├── progress.py           # Progress logging
│   ├── kanban.py             # Kanban board
│   ├── focus.py              # Focus timer
│   └── reports.py            # PDF generation
├── services/                 # Business logic
│   ├── task_service.py       # Task operations
│   ├── progress_service.py   # Stats & health scores
│   ├── kanban_service.py     # Kanban operations
│   ├── focus_service.py      # Focus session tracking
│   └── pdf_service.py        # PDF generation
├── static/                   # Frontend assets
│   ├── css/
│   ├── js/
│   ├── icons/
│   └── sounds/
├── templates/                # HTML templates
│   └── index.html
└── .env.example              # Environment template
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
| GET    | `/api/kanban`        | Get kanban items    |
| POST   | `/api/kanban`        | Create kanban item  |
| GET    | `/api/focus/stats`   | Get focus stats     |
| POST   | `/api/focus/start`   | Start focus session |
| GET    | `/api/reports/pdf`   | Download PDF report |

## License

MIT
