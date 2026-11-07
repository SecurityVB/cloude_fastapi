"""Store file sizes, user usage and role quotas in bytes."""
from pathlib import Path

import sqlalchemy as sa
from alembic import op

from src.catalogs.config import UCATALOGS_DIR

revision = "c2e6d88db172"
down_revision = "91fe0d06425b"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column("roles", "limit", new_column_name="limit_bytes",
                    type_=sa.BigInteger(), postgresql_using='pg_size_bytes("limit")')
    op.add_column("users", sa.Column("used_bytes", sa.BigInteger(), nullable=False,
                                     server_default="0"))
    op.add_column("files", sa.Column("size_bytes", sa.BigInteger()))
    conn = op.get_bind()
    rows = conn.execute(sa.text("SELECT id, path, server_filename FROM files")).all()
    for file_id, folder, name in rows:
        location = UCATALOGS_DIR / Path(folder) / name
        size = location.stat().st_size
        conn.execute(sa.text("UPDATE files SET size_bytes = :size WHERE id = :id"),
                     {"size": size, "id": file_id})
    op.alter_column("files", "size_bytes", nullable=False)
    op.execute("""
        UPDATE users SET used_bytes = totals.bytes
        FROM (SELECT owner, SUM(size_bytes) AS bytes FROM files GROUP BY owner) totals
        WHERE users.id = totals.owner
    """)
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


def downgrade():
    op.execute("DROP TRIGGER files_update_storage_usage ON files")
    op.execute("DROP FUNCTION update_user_storage_usage()")
    op.drop_column("files", "size_bytes")
    op.drop_column("users", "used_bytes")
    # Use the largest exact unit so existing quotas fit the original VARCHAR(7).
    op.alter_column("roles", "limit_bytes", new_column_name="limit", type_=sa.String(7),
                    postgresql_using="""
                        CASE
                            WHEN limit_bytes % 1099511627776 = 0 THEN (limit_bytes / 1099511627776)::text || 'TB'
                            WHEN limit_bytes % 1073741824 = 0 THEN (limit_bytes / 1073741824)::text || 'GB'
                            WHEN limit_bytes % 1048576 = 0 THEN (limit_bytes / 1048576)::text || 'MB'
                            WHEN limit_bytes % 1024 = 0 THEN (limit_bytes / 1024)::text || 'KB'
                            ELSE limit_bytes::text
                        END
                    """)
