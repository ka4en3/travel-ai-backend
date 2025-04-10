DB URL: postgresql+asyncpg://user:password@localhost:5432/travel_ai
Tables in metadata:
 - users
 - routes
 - route_days
 - activities
 - route_access
 - ai_cache
 - exports
BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> c60638198953

CREATE TABLE users (
    telegram_id INTEGER NOT NULL, 
    username VARCHAR, 
    first_name VARCHAR NOT NULL, 
    last_name VARCHAR, 
    language VARCHAR, 
    is_premium BOOLEAN NOT NULL, 
    is_bot BOOLEAN NOT NULL, 
    last_active TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_users PRIMARY KEY (id)
);

CREATE INDEX ix_users_id ON users (id);

CREATE UNIQUE INDEX ix_users_telegram_id ON users (telegram_id);

CREATE INDEX ix_users_username ON users (username);

CREATE TABLE ai_cache (
    cache_key VARCHAR NOT NULL, 
    prompt_hash VARCHAR, 
    original_prompt TEXT, 
    origin VARCHAR, 
    destination VARCHAR, 
    duration_days INTEGER, 
    interests JSON, 
    budget FLOAT, 
    result JSON NOT NULL, 
    hit_count INTEGER NOT NULL, 
    source VARCHAR NOT NULL, 
    expires_at TIMESTAMP WITH TIME ZONE, 
    user_id INTEGER, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_ai_cache PRIMARY KEY (id), 
    CONSTRAINT fk_ai_cache_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX ix_ai_cache_cache_key ON ai_cache (cache_key);

CREATE INDEX ix_ai_cache_destination ON ai_cache (destination);

CREATE INDEX ix_ai_cache_id ON ai_cache (id);

CREATE INDEX ix_ai_cache_origin ON ai_cache (origin);

CREATE INDEX ix_cache_from_to_days_budget ON ai_cache (origin, destination, duration_days, budget);

CREATE TABLE routes (
    name VARCHAR NOT NULL, 
    share_code VARCHAR NOT NULL, 
    is_public BOOLEAN NOT NULL, 
    origin VARCHAR NOT NULL, 
    destination VARCHAR NOT NULL, 
    duration_days INTEGER NOT NULL, 
    interests JSON, 
    budget FLOAT NOT NULL, 
    route_data JSON, 
    owner_id INTEGER NOT NULL, 
    last_edited_by INTEGER, 
    ai_cache_id INTEGER, 
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_routes PRIMARY KEY (id), 
    CONSTRAINT fk_routes_ai_cache_id_ai_cache FOREIGN KEY(ai_cache_id) REFERENCES ai_cache (id) ON DELETE SET NULL, 
    CONSTRAINT fk_routes_last_edited_by_users FOREIGN KEY(last_edited_by) REFERENCES users (id) ON DELETE SET NULL, 
    CONSTRAINT fk_routes_owner_id_users FOREIGN KEY(owner_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_routes_destination ON routes (destination);

CREATE INDEX ix_routes_id ON routes (id);

CREATE INDEX ix_routes_name ON routes (name);

CREATE INDEX ix_routes_origin ON routes (origin);

CREATE UNIQUE INDEX ix_routes_share_code ON routes (share_code);

CREATE TYPE exporttype AS ENUM ('PDF', 'GOOGLE_CALENDAR', 'GOOGLE_DOCS');

CREATE TYPE exportstatus AS ENUM ('QUEUED', 'SUCCESS', 'FAILED');

CREATE TABLE exports (
    route_id INTEGER NOT NULL, 
    user_id INTEGER NOT NULL, 
    export_type exporttype NOT NULL, 
    status exportstatus NOT NULL, 
    file_path VARCHAR, 
    external_id VARCHAR, 
    error_message TEXT, 
    created_at TIMESTAMP WITH TIME ZONE DEFAULT now() NOT NULL, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_exports PRIMARY KEY (id), 
    CONSTRAINT fk_exports_route_id_routes FOREIGN KEY(route_id) REFERENCES routes (id) ON DELETE CASCADE, 
    CONSTRAINT fk_exports_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE CASCADE
);

CREATE INDEX ix_exports_id ON exports (id);

CREATE TYPE routerole AS ENUM ('CREATOR', 'EDITOR', 'VIEWER');

CREATE TABLE route_access (
    user_id INTEGER NOT NULL, 
    route_id INTEGER NOT NULL, 
    role routerole NOT NULL, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_route_access PRIMARY KEY (id), 
    CONSTRAINT fk_route_access_route_id_routes FOREIGN KEY(route_id) REFERENCES routes (id) ON DELETE CASCADE, 
    CONSTRAINT fk_route_access_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL, 
    CONSTRAINT uq_user_route UNIQUE (user_id, route_id)
);

CREATE INDEX ix_route_access_id ON route_access (id);

CREATE TABLE route_days (
    route_id INTEGER NOT NULL, 
    day_number INTEGER NOT NULL, 
    description VARCHAR, 
    date TIMESTAMP WITHOUT TIME ZONE, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_route_days PRIMARY KEY (id), 
    CONSTRAINT fk_route_days_route_id_routes FOREIGN KEY(route_id) REFERENCES routes (id) ON DELETE CASCADE
);

CREATE INDEX ix_route_days_id ON route_days (id);

CREATE TABLE activities (
    day_id INTEGER NOT NULL, 
    name VARCHAR NOT NULL, 
    description VARCHAR, 
    start_time VARCHAR, 
    end_time VARCHAR, 
    location VARCHAR, 
    cost FLOAT, 
    notes VARCHAR, 
    activity_type VARCHAR, 
    external_link VARCHAR, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_activities PRIMARY KEY (id), 
    CONSTRAINT fk_activities_day_id_route_days FOREIGN KEY(day_id) REFERENCES route_days (id) ON DELETE CASCADE
);

CREATE INDEX ix_activities_id ON activities (id);

INSERT INTO alembic_version (version_num) VALUES ('c60638198953') RETURNING alembic_version.version_num;

COMMIT;

