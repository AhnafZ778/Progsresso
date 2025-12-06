-- HabitPulse Database Schema
-- Enable foreign keys
PRAGMA foreign_keys = ON;

-- Tasks table: Stores habit/task definitions
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    metric_type VARCHAR(20) NOT NULL CHECK (metric_type IN ('TIME', 'INTENSITY', 'PROGRESS', 'COUNT', 'BOOLEAN')),
    metric_unit VARCHAR(50),
    target_value REAL,
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('DAILY', 'WEEKDAYS', 'WEEKENDS', 'CUSTOM')),
    custom_days VARCHAR(20),
    is_archived BOOLEAN DEFAULT FALSE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

-- Progress logs table: Stores daily completion records
CREATE TABLE IF NOT EXISTS progress_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    task_id INTEGER NOT NULL,
    log_date DATE NOT NULL,
    week_start_date DATE NOT NULL,
    metric_value REAL,
    is_completed BOOLEAN DEFAULT TRUE,
    notes VARCHAR(200),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (task_id) REFERENCES tasks(id) ON DELETE CASCADE,
    UNIQUE(task_id, log_date)
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_progress_logs_task_id ON progress_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_progress_logs_log_date ON progress_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_progress_logs_week_start ON progress_logs(week_start_date);
CREATE INDEX IF NOT EXISTS idx_tasks_archived ON tasks(is_archived);

-- Kanban items table: Stores to-do items for Kanban board
CREATE TABLE IF NOT EXISTS kanban_items (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'TODO' CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE')),
    position INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_kanban_status ON kanban_items(status);
CREATE INDEX IF NOT EXISTS idx_kanban_due_date ON kanban_items(due_date);

-- Focus sessions table: Stores Pomodoro timer sessions
CREATE TABLE IF NOT EXISTS focus_sessions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    kanban_item_id INTEGER,
    duration_minutes INTEGER NOT NULL,
    started_at DATETIME NOT NULL,
    ended_at DATETIME,
    is_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (kanban_item_id) REFERENCES kanban_items(id) ON DELETE SET NULL
);

CREATE INDEX IF NOT EXISTS idx_focus_sessions_date ON focus_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_task ON focus_sessions(kanban_item_id);
