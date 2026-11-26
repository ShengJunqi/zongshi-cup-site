CREATE TABLE teams (
  id TEXT PRIMARY KEY,
  name TEXT NOT NULL,
  join_code TEXT NOT NULL UNIQUE,
  captain TEXT NOT NULL UNIQUE,
  windows TEXT NOT NULL DEFAULT '[]',
  roster_categories TEXT NOT NULL DEFAULT '["pending"]',
  extras TEXT NOT NULL DEFAULT '{}',
  members_confirmed INTEGER NOT NULL DEFAULT 0,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
--> statement-breakpoint
CREATE TABLE entrants (
  receipt TEXT PRIMARY KEY,
  id TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  contact TEXT NOT NULL,
  route TEXT NOT NULL,
  team_id TEXT REFERENCES teams(id),
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
--> statement-breakpoint
CREATE INDEX entrants_team ON entrants(team_id);
--> statement-breakpoint
CREATE TABLE surveys (
  receipt TEXT PRIMARY KEY,
  answers TEXT NOT NULL,
  updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
--> statement-breakpoint
CREATE TABLE pools (
  id TEXT PRIMARY KEY,
  rounds TEXT NOT NULL,
  created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);
--> statement-breakpoint
CREATE TABLE pool_teams (
  pool_id TEXT NOT NULL REFERENCES pools(id),
  team_id TEXT NOT NULL UNIQUE REFERENCES teams(id),
  position INTEGER NOT NULL,
  PRIMARY KEY (pool_id,position)
);
--> statement-breakpoint
