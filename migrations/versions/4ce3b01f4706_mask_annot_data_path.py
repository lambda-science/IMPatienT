"""Mask Annot Data Path

Revision ID: 4ce3b01f4706
Revises: 77cb4925bb52
Create Date: 2021-10-11 11:05:25.253541

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '4ce3b01f4706'
down_revision = '77cb4925bb52'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    #op.drop_table('sqlite_sequence')
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.add_column(sa.Column('mask_annot_path', sa.String(length=4096), nullable=True))
        batch_op.create_unique_constraint(batch_op.f('uq_image_mask_annot_path'), ['mask_annot_path'])

    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table('image', schema=None) as batch_op:
        batch_op.drop_constraint(batch_op.f('uq_image_mask_annot_path'), type_='unique')
        batch_op.drop_column('mask_annot_path')

    #op.create_table('sqlite_sequence',
    #sa.Column('name', sa.NullType(), nullable=True),
    #sa.Column('seq', sa.NullType(), nullable=True)
    #)
    # ### end Alembic commands ###
