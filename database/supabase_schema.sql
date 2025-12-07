-- Progresso PostgreSQL Schema for Supabase (with user isolation)
-- Run this in the Supabase SQL Editor to create your tables

-- Tasks table: Stores habit/task definitions
CREATE TABLE IF NOT EXISTS tasks (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    name VARCHAR(100) NOT NULL,
    description VARCHAR(500),
    metric_type VARCHAR(20) NOT NULL CHECK (metric_type IN ('TIME', 'INTENSITY', 'PROGRESS', 'COUNT', 'BOOLEAN')),
    metric_unit VARCHAR(50),
    target_value REAL,
    frequency VARCHAR(20) NOT NULL CHECK (frequency IN ('DAILY', 'WEEKDAYS', 'WEEKENDS', 'CUSTOM')),
    custom_days VARCHAR(20),
    is_archived BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Progress logs table: Stores daily completion records
CREATE TABLE IF NOT EXISTS progress_logs (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    log_date DATE NOT NULL,
    week_start_date DATE NOT NULL,
    metric_value REAL,
    is_completed BOOLEAN DEFAULT TRUE,
    notes VARCHAR(200),
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW(),
    UNIQUE(task_id, log_date)
);

-- Kanban items table: Stores to-do items for Kanban board
CREATE TABLE IF NOT EXISTS kanban_items (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    title VARCHAR(200) NOT NULL,
    description TEXT,
    due_date DATE NOT NULL,
    status VARCHAR(20) DEFAULT 'TODO' CHECK (status IN ('TODO', 'IN_PROGRESS', 'DONE')),
    position INTEGER DEFAULT 0,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Focus sessions table: Stores Pomodoro timer sessions
CREATE TABLE IF NOT EXISTS focus_sessions (
    id SERIAL PRIMARY KEY,
    user_id UUID NOT NULL,
    kanban_item_id INTEGER REFERENCES kanban_items(id) ON DELETE SET NULL,
    duration_minutes INTEGER NOT NULL,
    started_at TIMESTAMPTZ NOT NULL,
    ended_at TIMESTAMPTZ,
    is_completed BOOLEAN DEFAULT FALSE,
    notes TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Indexes for performance
CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_progress_logs_task_id ON progress_logs(task_id);
CREATE INDEX IF NOT EXISTS idx_progress_logs_log_date ON progress_logs(log_date);
CREATE INDEX IF NOT EXISTS idx_progress_logs_week_start ON progress_logs(week_start_date);
CREATE INDEX IF NOT EXISTS idx_tasks_archived ON tasks(is_archived);
CREATE INDEX IF NOT EXISTS idx_kanban_user ON kanban_items(user_id);
CREATE INDEX IF NOT EXISTS idx_kanban_status ON kanban_items(status);
CREATE INDEX IF NOT EXISTS idx_kanban_due_date ON kanban_items(due_date);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_user ON focus_sessions(user_id);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_date ON focus_sessions(started_at);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_task ON focus_sessions(kanban_item_id);

-- Enable Row Level Security (RLS) for user data isolation
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE kanban_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE focus_sessions ENABLE ROW LEVEL SECURITY;

-- RLS Policies: Users can only access their own data
CREATE POLICY "Users can view own tasks" ON tasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tasks" ON tasks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tasks" ON tasks FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own tasks" ON tasks FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own kanban" ON kanban_items FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own kanban" ON kanban_items FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own kanban" ON kanban_items FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own kanban" ON kanban_items FOR DELETE USING (auth.uid() = user_id);

CREATE POLICY "Users can view own focus" ON focus_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own focus" ON focus_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own focus" ON focus_sessions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own focus" ON focus_sessions FOR DELETE USING (auth.uid() = user_id);

-- Progress logs inherit access from their parent task
CREATE POLICY "Users can access own progress" ON progress_logs FOR ALL 
USING (EXISTS (SELECT 1 FROM tasks WHERE tasks.id = progress_logs.task_id AND tasks.user_id = auth.uid()));
