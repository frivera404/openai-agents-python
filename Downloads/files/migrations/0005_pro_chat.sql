-- Migration: BristolBot Pro chat history table
-- Run: wrangler d1 execute bristoltalks-pro-chat --remote --file=migrations/0005_pro_chat.sql --config wrangler-bristolbot-pro.toml

CREATE TABLE IF NOT EXISTS pro_chat_history (
  id         INTEGER PRIMARY KEY AUTOINCREMENT,
  session_id TEXT NOT NULL,
  role       TEXT NOT NULL,
  content    TEXT NOT NULL,
  model      TEXT,
  created_at TEXT NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_session ON pro_chat_history (session_id, created_at);
