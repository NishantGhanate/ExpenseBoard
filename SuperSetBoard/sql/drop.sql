DO $$
DECLARE
    r RECORD;
BEGIN
    -- Drop constraints first
    FOR r IN
        SELECT nspname, relname, conname
        FROM pg_constraint c
        JOIN pg_class t ON c.conrelid = t.oid
        JOIN pg_namespace n ON t.relnamespace = n.oid
        WHERE conname LIKE 'uq_transaction_%'
    LOOP
        EXECUTE format('ALTER TABLE %I.%I DROP CONSTRAINT %I', r.nspname, r.relname, r.conname);
        RAISE NOTICE 'Dropped constraint: %', r.conname;
    END LOOP;

    -- Drop standalone indexes (not backing constraints)
    FOR r IN
        SELECT schemaname, indexname
        FROM pg_indexes
        WHERE indexname LIKE 'uq_transaction_%'
          AND indexname NOT IN (SELECT conname FROM pg_constraint)
    LOOP
        EXECUTE format('DROP INDEX IF EXISTS %I.%I', r.schemaname, r.indexname);
        RAISE NOTICE 'Dropped index: %', r.indexname;
    END LOOP;
END $$;
