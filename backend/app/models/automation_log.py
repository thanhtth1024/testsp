"""
AutomationLog model - logs n8n workflow executions.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, Enum, JSON
from datetime import datetime
import enum
from app.database import Base

class AutomationStatus(str, enum.Enum):
    """Automation status enumeration"""
    SUCCESS = "success"
    FAILED = "failed"
    RUNNING = "running"

class AutomationLog(Base):
    """
    AutomationLog model for tracking n8n workflow executions.
    
    Attributes:
        id: Primary key
        workflow_name: Name of the n8n workflow
        status: Execution status
        input_data: Input data as JSON
        output_data: Output data as JSON
        error_message: Error message if failed
        executed_at: Execution timestamp
    """
    __tablename__ = "automation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    workflow_name = Column(String, nullable=False, index=True)
    status = Column(Enum(AutomationStatus), nullable=False)
    input_data = Column(JSON)
    output_data = Column(JSON)
    error_message = Column(Text)
    executed_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
