"""create phone number for user column

Revision ID: addb53730a6d
Revises: 
Create Date: 2022-11-22 17:50:11.386013

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'addb53730a6d'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        table_name="users", 
        column=sa.Column("phone_number", sa.String(), nullable=True)
    )


def downgrade() -> None:
    pass
