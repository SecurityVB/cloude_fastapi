"""Move file usage accounting into the application."""
from alembic import op

revision = "a29f3cc940ed"
down_revision = "c2e6d88db172"
branch_labels = None
depends_on = None


def upgrade():
    op.execute("DROP TRIGGER files_update_storage_usage ON files")
    op.execute("DROP FUNCTION update_user_storage_usage()")


def downgrade():
    op.execute("""
        CREATE FUNCTION update_user_storage_usage() RETURNS trigger LANGUAGE plpgsql AS $$
        BEGIN
            IF TG_OP IN ('DELETE', 'UPDATE') THEN
                UPDATE users SET used_bytes = used_bytes - OLD.size_bytes WHERE id = OLD.owner;
            END IF;
            IF TG_OP IN ('INSERT', 'UPDATE') THEN
                UPDATE users SET used_bytes = used_bytes + NEW.size_bytes WHERE id = NEW.owner;
            END IF;
            RETURN NULL;
        END;
        $$
    """)
    op.execute("""
        CREATE TRIGGER files_update_storage_usage
        AFTER INSERT OR DELETE OR UPDATE OF owner, size_bytes ON files
        FOR EACH ROW EXECUTE FUNCTION update_user_storage_usage()
    """)
