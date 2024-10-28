"""empty message

Revision ID: 9eeb11f04482
Revises: e92481579942
Create Date: 2024-09-08 23:28:52.337535

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '9eeb11f04482'
down_revision = 'e92481579942'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('interaction_call_recording',
    sa.Column('id', sa.Integer(), nullable=False),
    sa.Column('interaction_id', sa.Integer(), nullable=False),
    sa.Column('s3_location', sa.String(), nullable=False),
    sa.Column('file_format', postgresql.ENUM('mp3', 'wav', 'transcription', name='file_format'), nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['interaction_id'], ['interaction.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('interaction_call_recording')
    # ### end Alembic commands ###
