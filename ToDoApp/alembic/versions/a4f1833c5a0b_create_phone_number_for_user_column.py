"""create phone number for user column

Revision ID: a4f1833c5a0b
Revises: addb53730a6d
Create Date: 2022-11-22 17:59:06.387335

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'a4f1833c5a0b'
down_revision = 'addb53730a6d'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("users", sa.Column("phone_number", sa.String(), nullable=True))

def downgrade() -> None:
    op.drop_column("users", "phone_number")
