"""Description of the change1

Revision ID: 1451b71664c0
Revises: 
Create Date: 2025-01-13 07:55:42.118129

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.types import Text
from sqlalchemy.dialects import postgresql

from backend.db import JSONEncodedList

# revision identifiers, used by Alembic.
revision: str = '1451b71664c0'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('email', sa.String(), nullable=True),
    sa.Column('password', sa.String(), nullable=True),
    sa.Column('role', sa.String(), nullable=True),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_table('farmer_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('land_handling_capacity', sa.Integer(), nullable=True),
    sa.Column('preferred_locations', JSONEncodedList(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_farmer_details_id'), 'farmer_details', ['id'], unique=False)
    op.create_table('landlord_details',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=True),
    sa.Column('phone_number', sa.String(), nullable=True),
    sa.Column('soil_type', sa.String(), nullable=True),
    sa.Column('acres', sa.Integer(), nullable=True),
    sa.Column('location', sa.String(), nullable=True),
    sa.Column('images_list', JSONEncodedList(), nullable=True),
    sa.ForeignKeyConstraint(['user_id'], ['users.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_landlord_details_id'), 'landlord_details', ['id'], unique=False)
    op.create_table('spaces',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('farmer_id', sa.Integer(), nullable=False),
    sa.Column('landlord_id', sa.Integer(), nullable=False),
    sa.Column('admin_id', sa.Integer(), nullable=False),
    sa.Column('description', sa.Text(), nullable=True),
    sa.Column('progress', postgresql.JSON(astext_type=Text()), nullable=True),
    sa.ForeignKeyConstraint(['admin_id'], ['users.id'], ),
    sa.ForeignKeyConstraint(['farmer_id'], ['farmer_details.id'], ),
    sa.ForeignKeyConstraint(['landlord_id'], ['landlord_details.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_spaces_id'), 'spaces', ['id'], unique=False)
    op.create_table('crops',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('crop_name', sa.String(), nullable=False),
    sa.Column('duration', sa.String(), nullable=False),
    sa.Column('steps', postgresql.JSON(astext_type=Text()), nullable=True),
    sa.Column('space_id', sa.Integer(), nullable=True),
    sa.ForeignKeyConstraint(['space_id'], ['spaces.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_crops_id'), 'crops', ['id'], unique=False)
    op.create_table('proofs',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('file_url', sa.String(), nullable=False),
    sa.Column('crop_id', sa.Integer(), nullable=False),
    sa.Column('step_index', sa.Integer(), nullable=False),
    sa.ForeignKeyConstraint(['crop_id'], ['crops.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_proofs_id'), 'proofs', ['id'], unique=False)
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(op.f('ix_proofs_id'), table_name='proofs')
    op.drop_table('proofs')
    op.drop_index(op.f('ix_crops_id'), table_name='crops')
    op.drop_table('crops')
    op.drop_index(op.f('ix_spaces_id'), table_name='spaces')
    op.drop_table('spaces')
    op.drop_index(op.f('ix_landlord_details_id'), table_name='landlord_details')
    op.drop_table('landlord_details')
    op.drop_index(op.f('ix_farmer_details_id'), table_name='farmer_details')
    op.drop_table('farmer_details')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_table('users')
    # ### end Alembic commands ###