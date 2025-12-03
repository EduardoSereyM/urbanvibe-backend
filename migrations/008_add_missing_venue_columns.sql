ALTER TABLE venues
ADD COLUMN opening_hours JSONB DEFAULT '{}'::jsonb,
ADD COLUMN payment_methods JSONB DEFAULT '{}'::jsonb,
ADD COLUMN price_tier SMALLINT DEFAULT 1,
ADD COLUMN avg_price_min FLOAT DEFAULT 0.0,
ADD COLUMN avg_price_max FLOAT DEFAULT 0.0,
ADD COLUMN currency_code VARCHAR(3) DEFAULT 'CLP';
