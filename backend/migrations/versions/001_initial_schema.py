"""initial database schema for ScholarPulse

Revision ID: 001_initial_schema
Revises: 
Create Date: 2026-10-17 15:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '001_initial_schema'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. users table
    op.create_table(
        'users',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('email', sa.String(length=255), nullable=False),
        sa.Column('password_hash', sa.Text(), nullable=False),
        sa.Column('role', sa.String(length=50), nullable=False, server_default='user'),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default='1'),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_users_email', 'users', ['email'], unique=True)
    op.create_index('ix_users_role', 'users', ['role'])

    # 2. papers table
    op.create_table(
        'papers',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('title', sa.Text(), nullable=False),
        sa.Column('abstract', sa.Text(), nullable=True),
        sa.Column('publication_year', sa.SmallInteger(), nullable=True),
        sa.Column('doi', sa.String(length=255), nullable=True),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('source_url', sa.Text(), nullable=True),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('document_type', sa.String(length=50), nullable=True),
        sa.Column('language', sa.String(length=20), nullable=True, server_default='en'),
        sa.Column('raw_metadata', sa.JSON(), nullable=True),
        sa.Column('normalized_text', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_papers_doi', 'papers', ['doi'], unique=True)
    op.create_index('ix_papers_publication_year', 'papers', ['publication_year'])
    op.create_index('ix_papers_source_name', 'papers', ['source_name'])
    op.create_index('ix_papers_external_id', 'papers', ['external_id'])

    # 3. authors table
    op.create_table(
        'authors',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('display_name', sa.Text(), nullable=False),
        sa.Column('normalized_name', sa.Text(), nullable=False),
        sa.Column('external_id', sa.String(length=255), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_authors_normalized_name', 'authors', ['normalized_name'])
    op.create_index('ix_authors_external_id', 'authors', ['external_id'])

    # 4. paper_authors table
    op.create_table(
        'paper_authors',
        sa.Column('paper_id', sa.Uuid(), nullable=False),
        sa.Column('author_id', sa.Uuid(), nullable=False),
        sa.Column('author_order', sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(['author_id'], ['authors.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('paper_id', 'author_id'),
        sa.UniqueConstraint('paper_id', 'author_order', name='uq_paper_author_order'),
    )

    # 5. keywords table
    op.create_table(
        'keywords',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('display_term', sa.Text(), nullable=False),
        sa.Column('normalized_term', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_keywords_normalized_term', 'keywords', ['normalized_term'], unique=True)

    # 6. paper_keywords table
    op.create_table(
        'paper_keywords',
        sa.Column('paper_id', sa.Uuid(), nullable=False),
        sa.Column('keyword_id', sa.Uuid(), nullable=False),
        sa.Column('origin', sa.String(length=50), nullable=False, server_default='source'),
        sa.ForeignKeyConstraint(['keyword_id'], ['keywords.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('paper_id', 'keyword_id', 'origin'),
    )

    # 7. categories table
    op.create_table(
        'categories',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('name', sa.String(length=100), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_categories_name', 'categories', ['name'], unique=True)

    # 8. paper_categories table
    op.create_table(
        'paper_categories',
        sa.Column('paper_id', sa.Uuid(), nullable=False),
        sa.Column('category_id', sa.Uuid(), nullable=False),
        sa.Column('label_source', sa.String(length=50), nullable=False, server_default='verified'),
        sa.Column('confidence', sa.Float(), nullable=True),
        sa.Column('model_version', sa.String(length=50), nullable=True),
        sa.ForeignKeyConstraint(['category_id'], ['categories.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('paper_id', 'category_id', 'label_source'),
    )

    # 9. saved_papers table
    op.create_table(
        'saved_papers',
        sa.Column('user_id', sa.Uuid(), nullable=False),
        sa.Column('paper_id', sa.Uuid(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['user_id'], ['users.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('user_id', 'paper_id'),
    )

    # 10. ingestion_runs table
    op.create_table(
        'ingestion_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('source_name', sa.String(length=100), nullable=False),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='started'),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('records_seen', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_created', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_updated', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('records_skipped', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('error_count', sa.Integer(), nullable=False, server_default='0'),
        sa.Column('summary', sa.JSON(), nullable=True),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_ingestion_runs_source_name', 'ingestion_runs', ['source_name'])
    op.create_index('ix_ingestion_runs_status', 'ingestion_runs', ['status'])

    # 11. relevance_judgments table
    op.create_table(
        'relevance_judgments',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('query_id', sa.String(length=100), nullable=False),
        sa.Column('paper_id', sa.Uuid(), nullable=False),
        sa.Column('relevance_grade', sa.SmallInteger(), nullable=False),
        sa.Column('judge_id', sa.String(length=100), nullable=True),
        sa.Column('dataset_version', sa.String(length=50), nullable=False),
        sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('query_id', 'paper_id', 'dataset_version', name='uq_query_paper_dataset'),
    )
    op.create_index('ix_relevance_judgments_query_id', 'relevance_judgments', ['query_id'])
    op.create_index('ix_relevance_judgments_dataset_version', 'relevance_judgments', ['dataset_version'])

    # 12. evaluation_runs table
    op.create_table(
        'evaluation_runs',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evaluation_type', sa.String(length=50), nullable=False),
        sa.Column('dataset_version', sa.String(length=50), nullable=False),
        sa.Column('query_set_version', sa.String(length=50), nullable=True),
        sa.Column('model_or_ranker', sa.String(length=100), nullable=False),
        sa.Column('parameters', sa.JSON(), nullable=True),
        sa.Column('started_at', sa.DateTime(timezone=True), nullable=False),
        sa.Column('finished_at', sa.DateTime(timezone=True), nullable=True),
        sa.Column('status', sa.String(length=50), nullable=False, server_default='completed'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evaluation_runs_evaluation_type', 'evaluation_runs', ['evaluation_type'])
    op.create_index('ix_evaluation_runs_model_or_ranker', 'evaluation_runs', ['model_or_ranker'])

    # 13. evaluation_metrics table
    op.create_table(
        'evaluation_metrics',
        sa.Column('id', sa.Uuid(), nullable=False),
        sa.Column('evaluation_run_id', sa.Uuid(), nullable=False),
        sa.Column('metric_name', sa.String(length=100), nullable=False),
        sa.Column('cutoff_k', sa.Integer(), nullable=True),
        sa.Column('metric_value', sa.Float(), nullable=False),
        sa.Column('details', sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(['evaluation_run_id'], ['evaluation_runs.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evaluation_metrics_metric_name', 'evaluation_metrics', ['metric_name'])


def downgrade() -> None:
    op.drop_table('evaluation_metrics')
    op.drop_table('evaluation_runs')
    op.drop_table('relevance_judgments')
    op.drop_table('ingestion_runs')
    op.drop_table('saved_papers')
    op.drop_table('paper_categories')
    op.drop_table('categories')
    op.drop_table('paper_keywords')
    op.drop_table('keywords')
    op.drop_table('paper_authors')
    op.drop_table('authors')
    op.drop_table('papers')
    op.drop_table('users')
