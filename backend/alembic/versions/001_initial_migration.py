"""Initial migration - create all tables

Revision ID: 001
Revises: 
Create Date: 2025-11-03

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '001'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # Create users table
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('email', sa.String(), nullable=False),
        sa.Column('username', sa.String(), nullable=False),
        sa.Column('full_name', sa.String(), nullable=False),
        sa.Column('password_hash', sa.String(), nullable=False),
        sa.Column('role', sa.Enum('USER', 'ADMIN', name='userrole'), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_users_id'), 'users', ['id'], unique=False)
    op.create_index(op.f('ix_users_email'), 'users', ['email'], unique=True)
    op.create_index(op.f('ix_users_username'), 'users', ['username'], unique=True)

    # Create projects table
    op.create_table(
        'projects',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('owner_id', sa.Integer(), nullable=False),
        sa.Column('status', sa.Enum('ACTIVE', 'COMPLETED', 'ON_HOLD', name='projectstatus'), nullable=False),
        sa.Column('start_date', sa.DateTime(), nullable=False),
        sa.Column('end_date', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['owner_id'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_projects_id'), 'projects', ['id'], unique=False)
    op.create_index(op.f('ix_projects_name'), 'projects', ['name'], unique=False)

    # Create tasks table
    op.create_table(
        'tasks',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('assigned_to', sa.Integer(), nullable=True),
        sa.Column('status', sa.Enum('TODO', 'IN_PROGRESS', 'DONE', name='taskstatus'), nullable=False),
        sa.Column('priority', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='taskpriority'), nullable=False),
        sa.Column('progress', sa.Float(), nullable=False),
        sa.Column('deadline', sa.DateTime(), nullable=False),
        sa.Column('last_progress_update', sa.DateTime(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.ForeignKeyConstraint(['assigned_to'], ['users.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_tasks_id'), 'tasks', ['id'], unique=False)
    op.create_index(op.f('ix_tasks_name'), 'tasks', ['name'], unique=False)

    # Create forecast_logs table
    op.create_table(
        'forecast_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('task_id', sa.Integer(), nullable=False),
        sa.Column('risk_level', sa.Enum('LOW', 'MEDIUM', 'HIGH', 'CRITICAL', name='risklevel'), nullable=False),
        sa.Column('risk_percentage', sa.Float(), nullable=False),
        sa.Column('predicted_delay_days', sa.Integer(), nullable=False),
        sa.Column('analysis', sa.Text(), nullable=False),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['task_id'], ['tasks.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_forecast_logs_id'), 'forecast_logs', ['id'], unique=False)
    op.create_index(op.f('ix_forecast_logs_created_at'), 'forecast_logs', ['created_at'], unique=False)

    # Create automation_logs table
    op.create_table(
        'automation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('workflow_name', sa.String(), nullable=False),
        sa.Column('status', sa.Enum('SUCCESS', 'FAILED', 'RUNNING', name='automationstatus'), nullable=False),
        sa.Column('input_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('output_data', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_automation_logs_id'), 'automation_logs', ['id'], unique=False)
    op.create_index(op.f('ix_automation_logs_workflow_name'), 'automation_logs', ['workflow_name'], unique=False)
    op.create_index(op.f('ix_automation_logs_executed_at'), 'automation_logs', ['executed_at'], unique=False)

    # Create simulation_logs table
    op.create_table(
        'simulation_logs',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('project_id', sa.Integer(), nullable=False),
        sa.Column('scenario', sa.Text(), nullable=False),
        sa.Column('affected_task_ids', postgresql.JSON(astext_type=sa.Text()), nullable=True),
        sa.Column('total_delay_days', sa.Integer(), nullable=False),
        sa.Column('analysis', sa.Text(), nullable=False),
        sa.Column('recommendations', sa.Text(), nullable=True),
        sa.Column('simulated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['project_id'], ['projects.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_simulation_logs_id'), 'simulation_logs', ['id'], unique=False)
    op.create_index(op.f('ix_simulation_logs_simulated_at'), 'simulation_logs', ['simulated_at'], unique=False)


def downgrade() -> None:
    # Drop tables in reverse order
    op.drop_index(op.f('ix_simulation_logs_simulated_at'), table_name='simulation_logs')
    op.drop_index(op.f('ix_simulation_logs_id'), table_name='simulation_logs')
    op.drop_table('simulation_logs')
    
    op.drop_index(op.f('ix_automation_logs_executed_at'), table_name='automation_logs')
    op.drop_index(op.f('ix_automation_logs_workflow_name'), table_name='automation_logs')
    op.drop_index(op.f('ix_automation_logs_id'), table_name='automation_logs')
    op.drop_table('automation_logs')
    
    op.drop_index(op.f('ix_forecast_logs_created_at'), table_name='forecast_logs')
    op.drop_index(op.f('ix_forecast_logs_id'), table_name='forecast_logs')
    op.drop_table('forecast_logs')
    
    op.drop_index(op.f('ix_tasks_name'), table_name='tasks')
    op.drop_index(op.f('ix_tasks_id'), table_name='tasks')
    op.drop_table('tasks')
    
    op.drop_index(op.f('ix_projects_name'), table_name='projects')
    op.drop_index(op.f('ix_projects_id'), table_name='projects')
    op.drop_table('projects')
    
    op.drop_index(op.f('ix_users_username'), table_name='users')
    op.drop_index(op.f('ix_users_email'), table_name='users')
    op.drop_index(op.f('ix_users_id'), table_name='users')
    op.drop_table('users')
    
    # Drop enums
    sa.Enum(name='risklevel').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='automationstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskpriority').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='taskstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='projectstatus').drop(op.get_bind(), checkfirst=True)
    sa.Enum(name='userrole').drop(op.get_bind(), checkfirst=True)
