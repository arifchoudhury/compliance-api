"""empty message

Revision ID: e92481579942
Revises: 
Create Date: 2024-08-27 21:34:14.718851

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'e92481579942'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('channel',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('policy',
    sa.Column('service', sa.String(length=128), nullable=False),
    sa.Column('action', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('service', 'action', name='_service_action_uc')
    )
    op.create_table('recorded_contact',
    sa.Column('fullname', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fullname')
    )
    op.create_table('recorded_contact_attribute',
    sa.Column('name', sa.String(length=20), nullable=False),
    sa.Column('regex', sa.String(length=100), nullable=True),
    sa.Column('required', sa.Boolean(), nullable=True),
    sa.Column('unique', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('retention_policy',
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('call_retention_days', sa.Integer(), nullable=True),
    sa.Column('sms_retention_days', sa.Integer(), nullable=True),
    sa.Column('retain_metadata', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('role',
    sa.Column('name', sa.String(length=128), nullable=False),
    sa.Column('description', sa.String(length=128), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('third_party_contact',
    sa.Column('fullname', sa.String(length=128), nullable=True),
    sa.Column('email', sa.String(length=128), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fullname')
    )
    op.create_table('token_block_list',
    sa.Column('jti', sa.String(length=36), nullable=False),
    sa.Column('created_at', sa.DateTime(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_token_block_list_jti'), 'token_block_list', ['jti'], unique=True)
    op.create_table('identifier',
    sa.Column('identifier', sa.String(length=100), nullable=False),
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('date_associated', sa.DateTime(), nullable=True),
    sa.Column('date_disassociated', sa.DateTime(), nullable=True),
    sa.Column('associated', sa.Boolean(), nullable=True),
    sa.Column('recorded_contact_id', sa.Integer(), nullable=True),
    sa.Column('third_party_contact_id', sa.Integer(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.CheckConstraint('(recorded_contact_id IS NOT NULL AND third_party_contact_id IS NULL) OR (third_party_contact_id IS NOT NULL AND recorded_contact_id IS NULL)', name='check_contact_type_id'),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], ),
    sa.ForeignKeyConstraint(['recorded_contact_id'], ['recorded_contact.id'], ),
    sa.ForeignKeyConstraint(['third_party_contact_id'], ['third_party_contact.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recorded_contact_attribute_association',
    sa.Column('recorded_contact_id', sa.Integer(), nullable=True),
    sa.Column('recorded_contact_attribute_id', sa.Integer(), nullable=True),
    sa.Column('associated_value', sa.String(length=20), nullable=False),
    sa.Column('date_associated', sa.DateTime(), nullable=True),
    sa.Column('date_disassociated', sa.DateTime(), nullable=True),
    sa.Column('associated', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['recorded_contact_attribute_id'], ['recorded_contact_attribute.id'], ),
    sa.ForeignKeyConstraint(['recorded_contact_id'], ['recorded_contact.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('recorded_contact_retention_policy',
    sa.Column('retention_policy_id', sa.Integer(), nullable=False),
    sa.Column('recorded_contact_id', sa.Integer(), nullable=False),
    sa.Column('date_associated', sa.DateTime(), nullable=True),
    sa.Column('date_disassociated', sa.DateTime(), nullable=True),
    sa.Column('associated', sa.Boolean(), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['recorded_contact_id'], ['recorded_contact.id'], ),
    sa.ForeignKeyConstraint(['retention_policy_id'], ['retention_policy.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('role_policies',
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('policy_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['policy_id'], ['policy.id'], ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('role_id', 'policy_id', 'id')
    )
    op.create_table('user',
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('fullname', sa.String(length=128), nullable=False),
    sa.Column('email', sa.String(length=128), nullable=False),
    sa.Column('password', sa.String(length=100), nullable=True),
    sa.Column('role_id', sa.Integer(), nullable=False),
    sa.Column('active', sa.Boolean(), nullable=True),
    sa.Column('reset_token', sa.String(length=64), nullable=True),
    sa.Column('reset_token_expiration', sa.DateTime(), nullable=True),
    sa.Column('failed_login_attempts', sa.Integer(), nullable=True),
    sa.Column('lockout_until', sa.DateTime(), nullable=True),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['role_id'], ['role.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('email'),
    sa.UniqueConstraint('fullname'),
    sa.UniqueConstraint('reset_token')
    )
    op.create_table('interaction',
    sa.Column('channel_id', sa.Integer(), nullable=False),
    sa.Column('external_id', sa.String(length=200), nullable=True),
    sa.Column('start_time', sa.DateTime(), nullable=True),
    sa.Column('end_time', sa.DateTime(), nullable=True),
    sa.Column('withheld', sa.Boolean(), nullable=True),
    sa.Column('direction', postgresql.ENUM('inbound', 'outbound', name='direction_enum'), nullable=False),
    sa.Column('retention_end_date', sa.DateTime(), nullable=True),
    sa.Column('retain_permanently', sa.Boolean(), nullable=True),
    sa.Column('recorded_identifier_id', sa.Integer(), nullable=False),
    sa.Column('third_party_identifier_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['channel_id'], ['channel.id'], ),
    sa.ForeignKeyConstraint(['recorded_identifier_id'], ['identifier.id'], ),
    sa.ForeignKeyConstraint(['third_party_identifier_id'], ['identifier.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('external_id')
    )
    op.create_table('playlist',
    sa.Column('name', sa.String(length=200), nullable=False),
    sa.Column('description', sa.String(length=500), nullable=True),
    sa.Column('created_by_id', sa.Integer(), nullable=False),
    sa.Column('status', postgresql.ENUM('created', 'pending', 'expired', 'failed', name='status_enum'), nullable=True),
    sa.Column('error_message', sa.String(length=500), nullable=True),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['created_by_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id'),
    sa.UniqueConstraint('name')
    )
    op.create_table('refresh_token',
    sa.Column('token', sa.String(length=500), nullable=False),
    sa.Column('user_id', sa.Integer(), nullable=False),
    sa.Column('expires_at', sa.DateTime(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['user_id'], ['user.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    op.create_table('playlist_interaction_association',
    sa.Column('playlist_id', sa.Integer(), nullable=False),
    sa.Column('interaction_id', sa.Integer(), nullable=False),
    sa.Column('id', sa.Integer(), autoincrement=True, nullable=False),
    sa.Column('inserted', sa.DateTime(), nullable=False),
    sa.Column('updated', sa.DateTime(), nullable=False),
    sa.ForeignKeyConstraint(['interaction_id'], ['interaction.id'], ),
    sa.ForeignKeyConstraint(['playlist_id'], ['playlist.id'], ),
    sa.PrimaryKeyConstraint('id')
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('playlist_interaction_association')
    op.drop_table('refresh_token')
    op.drop_table('playlist')
    op.drop_table('interaction')
    op.drop_table('user')
    op.drop_table('role_policies')
    op.drop_table('recorded_contact_retention_policy')
    op.drop_table('recorded_contact_attribute_association')
    op.drop_table('identifier')
    op.drop_index(op.f('ix_token_block_list_jti'), table_name='token_block_list')
    op.drop_table('token_block_list')
    op.drop_table('third_party_contact')
    op.drop_table('role')
    op.drop_table('retention_policy')
    op.drop_table('recorded_contact_attribute')
    op.drop_table('recorded_contact')
    op.drop_table('policy')
    op.drop_table('channel')
    # ### end Alembic commands ###
