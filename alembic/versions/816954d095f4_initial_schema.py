"""initial schema

Revision ID: 816954d095f4
Revises: 
Create Date: 2026-04-24 15:35:43.139269

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '816954d095f4'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('telegram_user_id', sa.Text(), primary_key=True),
        sa.Column('username', sa.Text()),
        sa.Column('first_joined', sa.TIMESTAMP(), server_default=sa.text('NOW()'))
    )
    
    op.create_table(
        'alerts',
        sa.Column('alert_id', sa.UUID(), primary_key=True),
        sa.Column('user_id', sa.Text(), sa.ForeignKey('users.telegram_user_id', ondelete='CASCADE')),
        sa.Column('type', sa.Text(), nullable=False),
        sa.Column('active', sa.Boolean(), server_default=sa.text('TRUE')),
        sa.Column('zone_percent', sa.Float()),
        sa.Column('created_at', sa.TIMESTAMP(), server_default=sa.text('NOW()')),
        sa.Column('last_triggered_price', sa.Float()),
        sa.Column('last_triggered_at', sa.TIMESTAMP()),
        sa.Column('data', sa.JSON())
    )


def downgrade() -> None:
    op.drop_table('alerts')
    op.drop_table('users')

