"""alter todos-column-user_id

Revision ID: gf37ad66a2a6
Revises: g50951ef0588b
Create Date: 2025-11-07 00:34:27.048803

"""
from typing import Sequence

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision: str = 'gf37ad66a2a6'
down_revision: str | Sequence[str] | None = 'g50951ef0588b'
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Upgrade schema."""
    # 先刪除外鍵
    op.drop_constraint('todos_fk_1', 'todos', type_='foreignkey')

    # 修改欄位
    op.alter_column('todos', 'user_id',
               existing_type=sa.Integer(),
               nullable=False)
    
    # 重新建立外鍵
    op.create_foreign_key(
        'todos_fk_1',
        'todos','users',
        ['user_id'], ['id'],
        onupdate="CASCADE",
        ondelete="CASCADE"
    )


def downgrade() -> None:
    """Downgrade schema."""
    # 先刪除外鍵
    op.drop_constraint('todos_fk_1', 'todos', type_='foreignkey')

    # 修改欄位
    op.alter_column('todos', 'user_id',
               existing_type=sa.Integer(),
               nullable=True)
    
    # 重新建立外鍵
    op.create_foreign_key(
        'todos_fk_1',
        'todos','users',
        ['user_id'], ['id'],
        onupdate="CASCADE",
        ondelete="CASCADE"
    )
