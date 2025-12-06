# Supabase Integration Guide

This guide walks you through setting up Supabase for Progresso and deploying to Vercel.

## Step 1: Create a Supabase Project

1. Go to [supabase.com](https://supabase.com) and sign in (or create an account)
2. Click **"New Project"**
3. Choose your organization
4. Enter project details:
   - **Name**: `progresso` (or any name you prefer)
   - **Database Password**: Generate a strong password (save this!)
   - **Region**: Choose the closest to you
5. Click **"Create new project"** and wait for it to initialize (~2 minutes)

## Step 2: Create Database Tables

1. In your Supabase dashboard, go to **SQL Editor** (left sidebar)
2. Click **"New query"**
3. Copy and paste the contents of `database/supabase_schema.sql`
4. Click **"Run"** to create all tables and indexes

## Step 3: Get Your API Credentials

1. Go to **Project Settings** (gear icon in sidebar)
2. Click **"API"** in the left menu
3. Copy these values:
   - **Project URL** → This is your `SUPABASE_URL`
   - **anon public** key → This is your `SUPABASE_KEY`

## Step 4: Set Up Local Development

1. Create a `.env` file in the project root:

   ```bash
   cp .env.example .env
   ```

2. Edit `.env` with your Supabase credentials:

   ```
   SUPABASE_URL=https://your-project-id.supabase.co
   SUPABASE_KEY=your-anon-public-key
   SECRET_KEY=your-random-secret-key
   DEBUG=True
   ```

3. Install dependencies:

   ```bash
   pip install -r requirements.txt
   ```

4. Run locally:

   ```bash
   python app.py
   ```

   Visit `http://localhost:5500`

## Step 5: Deploy to Vercel

### Option A: Deploy via Vercel Dashboard

1. Push your code to GitHub
2. Go to [vercel.com](https://vercel.com) and sign in
3. Click **"Add New"** → **"Project"**
4. Import your GitHub repository
5. Configure environment variables:
   - `SUPABASE_URL` = your Supabase project URL
   - `SUPABASE_KEY` = your Supabase anon key
   - `SECRET_KEY` = a random secret string
6. Click **"Deploy"**

### Option B: Deploy via Vercel CLI

1. Install Vercel CLI:

   ```bash
   npm i -g vercel
   ```

2. Login to Vercel:

   ```bash
   vercel login
   ```

3. Deploy:

   ```bash
   vercel
   ```

4. Set environment variables:

   ```bash
   vercel env add SUPABASE_URL
   vercel env add SUPABASE_KEY
   vercel env add SECRET_KEY
   ```

5. Redeploy with environment variables:
   ```bash
   vercel --prod
   ```

## Troubleshooting

### "SUPABASE_URL and SUPABASE_KEY must be set"

- Make sure your `.env` file exists and has the correct values
- On Vercel, check that environment variables are set in project settings

### Database connection errors

- Verify your Supabase project is active (not paused)
- Check that the API keys are correct (use anon key, not service role)
- Ensure tables were created by running the SQL schema

### 500 errors on Vercel

- Check Vercel function logs: `vercel logs`
- Make sure all dependencies are in `requirements.txt`

## Project Structure

```
progresso/
├── api/
│   └── index.py          # Vercel serverless entry point
├── database/
│   ├── supabase_db.py    # Supabase connection handler
│   └── supabase_schema.sql # PostgreSQL schema
├── routes/               # Flask blueprints
├── services/             # Business logic (Supabase queries)
├── static/               # CSS, JS, icons, sounds
├── templates/            # HTML templates
├── app.py                # Flask application
├── config.py             # Configuration
├── requirements.txt      # Python dependencies
├── vercel.json           # Vercel config
├── .env.example          # Environment template
└── .env                  # Your local credentials (gitignored)
```
