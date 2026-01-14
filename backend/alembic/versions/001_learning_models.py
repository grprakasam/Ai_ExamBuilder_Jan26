"""Add learning models and authentication fields

Revision ID: 001_learning_models
Revises: 
Create Date: 2026-01-14

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

# revision identifiers
revision = '001_learning_models'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Create concept table
    op.create_table(
        'concept',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('concept_id', sa.String(), nullable=False, unique=True, index=True),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text()),
        sa.Column('parent_concept_id', sa.String(), sa.ForeignKey('concept.concept_id'), nullable=True),
        sa.Column('subject', sa.String()),
        sa.Column('grade_level_min', sa.Integer()),
        sa.Column('grade_level_max', sa.Integer()),
        sa.Column('exam_standard', sa.String()),
        sa.Column('prerequisite_concept_ids', sa.JSON()),
        sa.Column('learning_resources', sa.JSON()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Create mastery_record table
    op.create_table(
        'mastery_record',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_id', sa.String(36), sa.ForeignKey('test.id'), nullable=False),
        sa.Column('concept_id', sa.String(), sa.ForeignKey('concept.concept_id'), nullable=False),
        sa.Column('current_level', sa.Float(), default=0.0),
        sa.Column('questions_attempted', sa.Integer(), default=0),
        sa.Column('questions_correct', sa.Integer(), default=0),
        sa.Column('streak_current', sa.Integer(), default=0),
        sa.Column('streak_best', sa.Integer(), default=0),
        sa.Column('last_practiced', sa.DateTime()),
        sa.Column('next_review_due', sa.DateTime()),
        sa.Column('ease_factor', sa.Float(), default=2.5),
        sa.Column('interval_days', sa.Integer(), default=1),
        sa.Column('repetitions', sa.Integer(), default=0),
        sa.Column('avg_time_to_correct', sa.Float()),
        sa.Column('improvement_rate', sa.Float()),
        sa.Column('first_attempt_date', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('mastery_achieved_date', sa.DateTime()),
        sa.Column('is_mastered', sa.Boolean(), default=False),
        sa.Column('needs_review', sa.Boolean(), default=False),
        sa.Column('updated_at', sa.DateTime(timezone=True), onupdate=sa.func.now())
    )
    
    # Create exam_attempt table
    op.create_table(
        'exam_attempt',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_id', sa.String(36), sa.ForeignKey('test.id'), nullable=False),
        sa.Column('access_code', sa.String(8), nullable=False),
        sa.Column('attempt_number', sa.Integer(), nullable=False),
        sa.Column('started_at', sa.DateTime(timezone=True), server_default=sa.func.now()),
        sa.Column('completed_at', sa.DateTime()),
        sa.Column('session_hash', sa.String(), index=True),
        sa.Column('answers', sa.JSON()),
        sa.Column('score', sa.Float()),
        sa.Column('time_taken_seconds', sa.Integer()),
        sa.Column('is_completed', sa.Boolean(), default=False),
        sa.Column('is_passed', sa.Boolean())
    )
    
    # Create attempt_request table
    op.create_table(
        'attempt_request',
        sa.Column('id', sa.String(36), primary_key=True),
        sa.Column('test_id', sa.String(36), sa.ForeignKey('test.id'), nullable=False),
        sa.Column('access_code', sa.String(8), nullable=False),
        sa.Column('current_attempts', sa.Integer(), nullable=False),
        sa.Column('requested_attempts', sa.Integer(), nullable=False),
        sa.Column('reason', sa.Text()),
        sa.Column('status', sa.String(), default='pending'),
        sa.Column('reviewed_by', sa.String(36), sa.ForeignKey('user.id')),
        sa.Column('reviewed_at', sa.DateTime()),
        sa.Column('admin_notes', sa.Text()),
        sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.func.now())
    )
    
    # Add new columns to test table
    op.add_column('test', sa.Column('access_code', sa.String(8), unique=True, index=True))
    op.add_column('test', sa.Column('max_attempts', sa.Integer(), default=3))
    op.add_column('test', sa.Column('code_expiration', sa.DateTime()))
    op.add_column('test', sa.Column('is_active', sa.Boolean(), default=True))
    op.add_column('test', sa.Column('exam_standard', sa.String(), default='ncdpi'))
    op.add_column('test', sa.Column('time_limit_minutes', sa.Integer()))
    op.add_column('test', sa.Column('passing_score', sa.Float(), default=0.6))
    op.add_column('test', sa.Column('shuffle_questions', sa.Boolean(), default=False))
    op.add_column('test', sa.Column('shuffle_options', sa.Boolean(), default=False))
    
    # Add new columns to question table
    op.add_column('question', sa.Column('concept_ids', sa.JSON()))
    op.add_column('question', sa.Column('prerequisite_concepts', sa.JSON()))
    op.add_column('question', sa.Column('learning_objective', sa.Text()))
    op.add_column('question', sa.Column('bloom_level', sa.String()))
    op.add_column('question', sa.Column('difficulty_score', sa.Float()))
    op.add_column('question', sa.Column('explanation_correct', sa.Text()))
    op.add_column('question', sa.Column('explanation_wrong', sa.JSON()))
    op.add_column('question', sa.Column('common_misconceptions', sa.JSON()))
    op.add_column('question', sa.Column('worked_example', sa.Text()))
    op.add_column('question', sa.Column('hint', sa.Text()))
    op.add_column('question', sa.Column('times_attempted', sa.Integer(), default=0))
    op.add_column('question', sa.Column('times_correct', sa.Integer(), default=0))
    op.add_column('question', sa.Column('avg_time_seconds', sa.Float()))


def downgrade():
    # Drop new columns from question table
    op.drop_column('question', 'avg_time_seconds')
    op.drop_column('question', 'times_correct')
    op.drop_column('question', 'times_attempted')
    op.drop_column('question', 'hint')
    op.drop_column('question', 'worked_example')
    op.drop_column('question', 'common_misconceptions')
    op.drop_column('question', 'explanation_wrong')
    op.drop_column('question', 'explanation_correct')
    op.drop_column('question', 'difficulty_score')
    op.drop_column('question', 'bloom_level')
    op.drop_column('question', 'learning_objective')
    op.drop_column('question', 'prerequisite_concepts')
    op.drop_column('question', 'concept_ids')
    
    # Drop new columns from test table
    op.drop_column('test', 'shuffle_options')
    op.drop_column('test', 'shuffle_questions')
    op.drop_column('test', 'passing_score')
    op.drop_column('test', 'time_limit_minutes')
    op.drop_column('test', 'exam_standard')
    op.drop_column('test', 'is_active')
    op.drop_column('test', 'code_expiration')
    op.drop_column('test', 'max_attempts')
    op.drop_column('test', 'access_code')
    
    # Drop tables
    op.drop_table('attempt_request')
    op.drop_table('exam_attempt')
    op.drop_table('mastery_record')
    op.drop_table('concept')
