"""create address table

Revision ID: 92343b70dd94
Revises: a4f1833c5a0b
Create Date: 2022-11-22 21:09:10.009437

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '92343b70dd94'
down_revision = 'a4f1833c5a0b'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "address",
        sa.Column("id", sa.Integer(), nullable=True, primary_key=True),
        sa.Column("address1", sa.String(), nullable=False),
        sa.Column("address2", sa.String(), nullable=False),
        sa.Column("city", sa.String(), nullable=False),
        sa.Column("state", sa.String(), nullable=False),
        sa.Column("country", sa.String(), nullable=False),
        sa.Column("postalcode", sa.String(), nullable=False)
    )


def downgrade() -> None:
    op.drop_table("address")
