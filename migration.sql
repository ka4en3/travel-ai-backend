BEGIN;

CREATE TABLE alembic_version (
    version_num VARCHAR(32) NOT NULL, 
    CONSTRAINT alembic_version_pkc PRIMARY KEY (version_num)
);

-- Running upgrade  -> 7f34871708a8

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

CREATE TABLE aicaches (
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
    CONSTRAINT pk_aicaches PRIMARY KEY (id), 
    CONSTRAINT fk_aicaches_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL
);

CREATE UNIQUE INDEX ix_aicaches_cache_key ON aicaches (cache_key);

CREATE INDEX ix_aicaches_destination ON aicaches (destination);

CREATE INDEX ix_aicaches_id ON aicaches (id);

CREATE INDEX ix_aicaches_origin ON aicaches (origin);

CREATE INDEX ix_cache_from_to_days_budget ON aicaches (origin, destination, duration_days, budget);

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
    CONSTRAINT fk_routes_ai_cache_id_aicaches FOREIGN KEY(ai_cache_id) REFERENCES aicaches (id) ON DELETE SET NULL, 
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

CREATE TABLE routeaccesss (
    user_id INTEGER NOT NULL, 
    route_id INTEGER NOT NULL, 
    role routerole NOT NULL, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_routeaccesss PRIMARY KEY (id), 
    CONSTRAINT fk_routeaccesss_route_id_routes FOREIGN KEY(route_id) REFERENCES routes (id) ON DELETE CASCADE, 
    CONSTRAINT fk_routeaccesss_user_id_users FOREIGN KEY(user_id) REFERENCES users (id) ON DELETE SET NULL, 
    CONSTRAINT uq_user_route UNIQUE (user_id, route_id)
);

CREATE INDEX ix_routeaccesss_id ON routeaccesss (id);

CREATE TABLE routedays (
    route_id INTEGER NOT NULL, 
    day_number INTEGER NOT NULL, 
    description VARCHAR, 
    date TIMESTAMP WITHOUT TIME ZONE, 
    id SERIAL NOT NULL, 
    CONSTRAINT pk_routedays PRIMARY KEY (id), 
    CONSTRAINT fk_routedays_route_id_routes FOREIGN KEY(route_id) REFERENCES routes (id) ON DELETE CASCADE
);

CREATE INDEX ix_routedays_id ON routedays (id);

CREATE TABLE activitys (
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
    CONSTRAINT pk_activitys PRIMARY KEY (id), 
    CONSTRAINT fk_activitys_day_id_routedays FOREIGN KEY(day_id) REFERENCES routedays (id) ON DELETE CASCADE
);

CREATE INDEX ix_activitys_id ON activitys (id);

INSERT INTO alembic_version (version_num) VALUES ('7f34871708a8') RETURNING alembic_version.version_num;

COMMIT;

