"""change command column to string

Revision ID: 1d8bb701dbd7
Revises: 75cd9aa3db4e
Create Date: 2024-09-25 11:02:18.792788

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '1d8bb701dbd7'
down_revision: Union[str, None] = '75cd9aa3db4e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
