-- Progresso Database Migration: Add user_id for user isolation
-- Run this in Supabase SQL Editor if you already have tables

-- Step 1: Add user_id columns
ALTER TABLE tasks ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE kanban_items ADD COLUMN IF NOT EXISTS user_id UUID;
ALTER TABLE focus_sessions ADD COLUMN IF NOT EXISTS user_id UUID;

-- Step 2: Add indexes for user_id
CREATE INDEX IF NOT EXISTS idx_tasks_user ON tasks(user_id);
CREATE INDEX IF NOT EXISTS idx_kanban_user ON kanban_items(user_id);
CREATE INDEX IF NOT EXISTS idx_focus_sessions_user ON focus_sessions(user_id);

-- Step 3: Enable Row Level Security
ALTER TABLE tasks ENABLE ROW LEVEL SECURITY;
ALTER TABLE progress_logs ENABLE ROW LEVEL SECURITY;
ALTER TABLE kanban_items ENABLE ROW LEVEL SECURITY;
ALTER TABLE focus_sessions ENABLE ROW LEVEL SECURITY;

-- Step 4: Create RLS Policies (run these one by one if errors occur)
-- Tasks policies
DROP POLICY IF EXISTS "Users can view own tasks" ON tasks;
DROP POLICY IF EXISTS "Users can insert own tasks" ON tasks;
DROP POLICY IF EXISTS "Users can update own tasks" ON tasks;
DROP POLICY IF EXISTS "Users can delete own tasks" ON tasks;

CREATE POLICY "Users can view own tasks" ON tasks FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own tasks" ON tasks FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own tasks" ON tasks FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own tasks" ON tasks FOR DELETE USING (auth.uid() = user_id);

-- Kanban policies
DROP POLICY IF EXISTS "Users can view own kanban" ON kanban_items;
DROP POLICY IF EXISTS "Users can insert own kanban" ON kanban_items;
DROP POLICY IF EXISTS "Users can update own kanban" ON kanban_items;
DROP POLICY IF EXISTS "Users can delete own kanban" ON kanban_items;

CREATE POLICY "Users can view own kanban" ON kanban_items FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own kanban" ON kanban_items FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own kanban" ON kanban_items FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own kanban" ON kanban_items FOR DELETE USING (auth.uid() = user_id);

-- Focus sessions policies
DROP POLICY IF EXISTS "Users can view own focus" ON focus_sessions;
DROP POLICY IF EXISTS "Users can insert own focus" ON focus_sessions;
DROP POLICY IF EXISTS "Users can update own focus" ON focus_sessions;
DROP POLICY IF EXISTS "Users can delete own focus" ON focus_sessions;

CREATE POLICY "Users can view own focus" ON focus_sessions FOR SELECT USING (auth.uid() = user_id);
CREATE POLICY "Users can insert own focus" ON focus_sessions FOR INSERT WITH CHECK (auth.uid() = user_id);
CREATE POLICY "Users can update own focus" ON focus_sessions FOR UPDATE USING (auth.uid() = user_id);
CREATE POLICY "Users can delete own focus" ON focus_sessions FOR DELETE USING (auth.uid() = user_id);

-- Progress logs (inherit from task)
DROP POLICY IF EXISTS "Users can access own progress" ON progress_logs;
CREATE POLICY "Users can access own progress" ON progress_logs FOR ALL 
USING (EXISTS (SELECT 1 FROM tasks WHERE tasks.id = progress_logs.task_id AND tasks.user_id = auth.uid()));
