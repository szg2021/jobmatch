"""创建推荐系统配置表

Revision ID: 547f931c52bb
Revises: previous_revision
Create Date: 2023-09-01 11:23:58.123456

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import func


# revision identifiers, used by Alembic.
revision = '547f931c52bb'
down_revision = None  # 替换为实际的前一个迁移版本
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'recommendation_configs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('learning_rate', sa.Float(), nullable=False, server_default='0.05'),
        sa.Column('loss_function', sa.String(), nullable=False, server_default='warp'),
        sa.Column('embedding_dim', sa.Integer(), nullable=False, server_default='64'),
        sa.Column('user_alpha', sa.Float(), nullable=False, server_default='0.000001'),
        sa.Column('item_alpha', sa.Float(), nullable=False, server_default='0.000001'),
        sa.Column('epochs', sa.Integer(), nullable=False, server_default='30'),
        sa.Column('num_threads', sa.Integer(), nullable=False, server_default='4'),
        sa.Column('vector_weight', sa.Float(), nullable=False, server_default='0.6'),
        sa.Column('lightfm_weight', sa.Float(), nullable=False, server_default='0.4'),
        sa.Column('training_schedule', sa.String(), nullable=False, server_default='0 2 * * *'),
        sa.Column('train_on_startup', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('max_recommendations', sa.Integer(), nullable=False, server_default='10'),
        sa.Column('active', sa.Boolean(), nullable=False, server_default='true'),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=func.now(), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    
    # 创建一个默认配置
    op.execute("""
    INSERT INTO recommendation_configs (
        learning_rate, loss_function, embedding_dim, user_alpha, item_alpha, 
        epochs, num_threads, vector_weight, lightfm_weight, 
        training_schedule, train_on_startup, max_recommendations, active
    ) VALUES (
        0.05, 'warp', 64, 0.000001, 0.000001, 
        30, 4, 0.6, 0.4, 
        '0 2 * * *', true, 10, true
    )
    """)


def downgrade():
    op.drop_table('recommendation_configs') 