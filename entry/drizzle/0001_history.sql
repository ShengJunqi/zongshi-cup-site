CREATE TABLE historical_profiles (
  source_key TEXT PRIMARY KEY,
  nickname TEXT NOT NULL,
  nickname_norm TEXT NOT NULL UNIQUE
);
--> statement-breakpoint
CREATE TABLE historical_sources (
  source_key TEXT NOT NULL REFERENCES historical_profiles(source_key),
  source_id TEXT NOT NULL,
  source_cell TEXT NOT NULL,
  PRIMARY KEY (source_key, source_id, source_cell)
);
