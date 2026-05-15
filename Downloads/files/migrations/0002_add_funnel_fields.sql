-- Migration: add funnel tracking fields to leads table
-- Run: wrangler d1 execute bristoltalks-db --file=migrations/0002_add_funnel_fields.sql

ALTER TABLE leads ADD COLUMN source TEXT;
ALTER TABLE leads ADD COLUMN utm_source TEXT;
ALTER TABLE leads ADD COLUMN utm_campaign TEXT;
ALTER TABLE leads ADD COLUMN utm_medium TEXT;
ALTER TABLE leads ADD COLUMN product TEXT;
