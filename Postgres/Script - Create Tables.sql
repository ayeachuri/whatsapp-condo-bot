-- Units and Users
CREATE TABLE condo_bot_schema.units (
    id SERIAL PRIMARY KEY,
    unit_number VARCHAR(20) UNIQUE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    phone_number VARCHAR(20) UNIQUE NOT NULL,
    unit_id INTEGER REFERENCES units(id),
    user_type VARCHAR(20) NOT NULL, -- admin, manager, resident, staff
    staff_role VARCHAR(50), -- for facility workers: security, cleaner, etc.
    is_active BOOLEAN DEFAULT TRUE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Facilities and Bookings
CREATE TABLE facilities (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    max_concurrent_bookings INTEGER DEFAULT 1,
    booking_limit_type VARCHAR(20), -- daily, weekly, monthly
    booking_limit_count INTEGER,
    unit_booking_limit INTEGER, -- limit per unit
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE bookings (
    id SERIAL PRIMARY KEY,
    facility_id INTEGER REFERENCES facilities(id) NOT NULL,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    unit_id INTEGER REFERENCES units(id) NOT NULL,
    start_time TIMESTAMP NOT NULL,
    end_time TIMESTAMP NOT NULL,
    status VARCHAR(20) DEFAULT 'confirmed', -- confirmed, cancelled, completed
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Issues and Maintenance
CREATE TABLE issue_categories (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    requires_worker_type VARCHAR(50) -- electrician, plumber, etc.
);

CREATE TABLE issues (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id) NOT NULL,
    unit_id INTEGER REFERENCES units(id) NOT NULL,
    category_id INTEGER REFERENCES issue_categories(id),
    description TEXT NOT NULL,
    status VARCHAR(20) DEFAULT 'open', -- open, assigned, resolved, closed
    assigned_to INTEGER REFERENCES users(id),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    resolved_at TIMESTAMP
);

-- Announcements
CREATE TABLE announcements (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    sender_id INTEGER REFERENCES users(id) NOT NULL,
    priority VARCHAR(20) DEFAULT 'normal', -- normal, urgent, emergency
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Chat Logs
CREATE TABLE chat_logs (
    id SERIAL PRIMARY KEY,
    user_id INTEGER REFERENCES users(id),
    message_type VARCHAR(20) NOT NULL, -- incoming, outgoing
    content TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- AI Instructions Repository
CREATE TABLE instructions (
    id SERIAL PRIMARY KEY,
    title VARCHAR(200) NOT NULL,
    content TEXT NOT NULL,
    category VARCHAR(50), -- SOP, incident_report, daily_task
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);