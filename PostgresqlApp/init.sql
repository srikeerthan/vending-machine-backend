CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    email VARCHAR(255) NOT NULL,
    full_name VARCHAR(255),
    roles VARCHAR(255) NOT NULL DEFAULT 'buyer',
    hashed_password VARCHAR(255) NOT NULL,
    disabled BOOLEAN DEFAULT FALSE,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE products (
    id BIGSERIAL PRIMARY KEY,
    name VARCHAR(255) UNIQUE NOT NULL,
    price NUMERIC(11, 2) NOT NULL,
    quantity INTEGER NOT NULL,
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    creator_id INTEGER REFERENCES users(id),
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE deposits (
    id SERIAL PRIMARY KEY,
    amount NUMERIC(11, 2) NOT NULL,
    coins VARCHAR NOT NULL,
    user_id INTEGER REFERENCES users(id),
    is_deposit_utilized BOOLEAN DEFAULT FALSE,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE purchases (
    id SERIAL PRIMARY KEY,
    product_id INTEGER REFERENCES products(id),
    deposit_id INTEGER REFERENCES deposits(id),
    quantity INTEGER NOT NULL,
    total_spent NUMERIC(11, 2) NOT NULL,
    created_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
