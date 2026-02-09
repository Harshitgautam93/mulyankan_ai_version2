# Supabase Setup for Session Persistence

## Create the `sessions` Table

To persist login information, you need to create a `sessions` table in Supabase. Follow these steps:

### 1. Go to Supabase Dashboard
- Open [supabase.com](https://supabase.com) and log in
- Select your project

### 2. Create the `sessions` Table
- Click **SQL Editor** in the left sidebar
- Click **New Query**
- Paste this SQL:

```sql
CREATE TABLE sessions (
  id BIGSERIAL PRIMARY KEY,
  username TEXT NOT NULL,
  user_id TEXT NOT NULL UNIQUE,
  created_at TIMESTAMP DEFAULT now(),
  updated_at TIMESTAMP DEFAULT now()
);

-- Create an index on user_id for faster lookups
CREATE INDEX idx_sessions_user_id ON sessions(user_id);

-- Enable Row Level Security (optional but recommended)
ALTER TABLE sessions ENABLE ROW LEVEL SECURITY;
```

- Click **Run**

### 3. (Optional) Set Row Level Security Policies

If you want to restrict users from seeing other users' sessions:

```sql
-- Allow users to read only their own session
CREATE POLICY "Users can view their own session"
ON sessions FOR SELECT
USING (auth.uid()::text = user_id);

-- Allow users to delete only their own session
CREATE POLICY "Users can delete their own session"
ON sessions FOR DELETE
USING (auth.uid()::text = user_id);

-- Allow inserting their own session
CREATE POLICY "Users can insert their own session"
ON sessions FOR INSERT
WITH CHECK (auth.uid()::text = user_id);
```

## How It Works

1. **Login**: When a user logs in via `st_login_form()`, their session is saved to the `sessions` table
2. **Persistence**: The session info (username, user_id) is stored in Supabase
3. **Logout**: When they click "Logout", their session is deleted from the database
4. **Next Time**: When they return and log in again, a new session record is created

## Database Functions in Your Code

The following functions in `backend/database.py` handle session management:

- `save_session(username, user_id)` - Saves a session after login
- `get_session(user_id)` - Retrieves an existing session
- `delete_session(user_id)` - Deletes session on logout

These are automatically called in `backend/main.py` when users authenticate.

## Troubleshooting

- **"sessions" table doesn't exist**: Run the SQL setup above in Supabase
- **RLS Errors**: Make sure your service role key is used (check `SUPABASE_KEY` in `.env`)
- **Sessions not saving**: Check Supabase logs for database errors
