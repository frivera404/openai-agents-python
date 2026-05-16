-- Migration: BusinessShield AI scan requests table
-- Run: wrangler d1 execute bristoltalks-shield --remote --file=migrations/0003_shield.sql --config wrangler-shield.toml

CREATE TABLE IF NOT EXISTS shield_scans (
  id            INTEGER PRIMARY KEY AUTOINCREMENT,
  business_name TEXT NOT NULL,
  email         TEXT NOT NULL,
  scanned_at    TEXT NOT NULL
);
