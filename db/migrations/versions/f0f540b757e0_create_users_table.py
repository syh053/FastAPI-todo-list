"""create users table

Revision ID: 975ec80664df
Revises: dc6f5f89e55a
Create Date: 2025-10-26 18:34:41.275200

"""
from typing import Sequence
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '975ec80664df'
down_revision: str | Sequence[str] | None = 'dc6f5f89e55a'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """ 建立 users 資料表 """
    op.create_table("users",
    sa.Column("id", sa.Integer(), nullable=False, primary_key=True),
    sa.Column("email", sa.String(50), nullable=False, unique=True),
    sa.Column("password", sa.String(200), nullable=False, unique=True),
    sa.Column("name", sa.String(100)),
    sa.Column("created_at", sa.DateTime(), nullable=False),
    sa.Column("updated_at", sa.DateTime(), nullable=False)
    )


def downgrade() -> None:
    """ 刪除 users 資料表 """
    op.drop_table("users")
