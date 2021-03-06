"""empty message

Revision ID: 599c198f193c
Revises: 
Create Date: 2020-09-01 18:07:02.296551

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = '599c198f193c'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table('users',
                    sa.Column('id', sa.String(), nullable=False),
                    sa.Column('name', sa.String(), nullable=False),
                    sa.Column('email', sa.String(), nullable=False),
                    sa.PrimaryKeyConstraint('id'),
                    sa.UniqueConstraint('email')
                    )
    op.create_table('todos',
                    sa.Column('id', sa.Integer(), nullable=False),
                    sa.Column('owner_id', sa.String(), nullable=True),
                    sa.Column('title', sa.String(), nullable=False),
                    sa.Column('done', sa.Boolean(), nullable=False),
                    sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
                    sa.PrimaryKeyConstraint('id')
                    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table('todos')
    op.drop_table('users')
    # ### end Alembic commands ###
