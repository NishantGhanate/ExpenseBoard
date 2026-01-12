CREATE TABLE ss_statement_pdfs (
    id BIGSERIAL PRIMARY KEY,

    user_id BIGINT NOT NULL
        REFERENCES ss_users(id)
        ON DELETE CASCADE,

    bank_account_id INTEGER
        REFERENCES ss_bank_accounts(id)
        ON DELETE SET NULL,

    -- Categorization Metadata
    sender_email VARCHAR(255) NOT NULL, -- e.g., 'alerts@hdfcbank.net'
    filename VARCHAR(255) NOT NULL, -- e.g., 'Statement_.*\.pdf' (Regex)

    -- Security
    -- Renamed to 'encrypted_password' because you cannot 'verify' a hash to open a PDF;
    -- you must be able to decrypt it to provide the secret to the PDF parser.
    encrypted_password TEXT NOT NULL,
    key_id VARCHAR(50), -- Reference to which KMS/Vault key was used to encrypt

    -- Status & Audit
    is_active BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

    -- Constraints
    CONSTRAINT uq_bank_pdfs_rule UNIQUE (user_id, sender_email, filename)
);

-- Index for the background worker to find matching rules quickly
CREATE INDEX idx_statement_pdfs_lookup
ON ss_statement_pdfs (sender_email)
WHERE is_active = TRUE;

CREATE INDEX idx_filename_regex ON ss_statement_pdfs (filename text_pattern_ops);
