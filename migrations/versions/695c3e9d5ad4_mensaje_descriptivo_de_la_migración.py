"""Mensaje descriptivo de la migración

Revision ID: 695c3e9d5ad4
Revises: 3b10962ceab9
Create Date: 2024-08-03 09:03:19.400117

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql

# revision identifiers, used by Alembic.
revision = '695c3e9d5ad4'
down_revision = '3b10962ceab9'
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column('service', sa.Column('image_url', sa.String(length=255), nullable=True))
    op.alter_column('service', 'type',
               existing_type=mysql.ENUM('valor1', 'valor2', 'ambos'),
               type_=sa.Enum('telemedicina', 'domicilio', 'ambos'),
               nullable=False)
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.alter_column('service', 'type',
               existing_type=sa.Enum('telemedicina', 'domicilio', 'ambos'),
               type_=mysql.ENUM('valor1', 'valor2', 'ambos'),
               nullable=True)
    op.drop_column('service', 'image_url')
    # ### end Alembic commands ###
