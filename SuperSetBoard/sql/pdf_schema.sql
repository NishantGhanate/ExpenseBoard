CREATE TABLE statement_pdfs (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES ss_users(id)
        ON DELETE CASCADE,

    sender_email VARCHAR(255) NOT NULL,

    -- Original PDF filename pattern or exact name
    filename VARCHAR(255) NOT NULL,

    -- Store encrypted / hashed PDF password only
    password_hash TEXT NOT NULL,

    is_active BOOLEAN NOT NULL DEFAULT TRUE,

    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Prevent duplicate rules per user
    CONSTRAINT uq_bank_pdfs_rule UNIQUE (user_id, sender_email, filename)
);
