"""Add column apt_num to address table

Revision ID: 32950c3828a7
Revises: a16795eaf6da
Create Date: 2022-11-24 17:58:54.158120

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '32950c3828a7'
down_revision = 'a16795eaf6da'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("address", sa.Column("apt_num", sa.String(), nullable=True))


def downgrade() -> None:
    op.drop_column("address", "apt_num")
