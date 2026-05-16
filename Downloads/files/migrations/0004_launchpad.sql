-- Migration: Bristol LaunchPad listings table
-- Run: wrangler d1 execute bristoltalks-launchpad --remote --file=migrations/0004_launchpad.sql --config wrangler-launchpad.toml

CREATE TABLE IF NOT EXISTS launchpad_listings (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  business_name TEXT NOT NULL,
  owner_name    TEXT,
  email         TEXT NOT NULL,
  phone         TEXT,
  category      TEXT,
  description   TEXT,
  submitted_at  TEXT NOT NULL
);
