"""
SimulationLog model - stores scenario simulation results.
"""
from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.database import Base

class SimulationLog(Base):
    """
    SimulationLog model for storing what-if scenario simulations.
    
    Attributes:
        id: Primary key
        project_id: Foreign key to project
        scenario: Scenario description
        affected_task_ids: List of affected task IDs
        total_delay_days: Total predicted delay
        analysis: AI analysis of scenario impact
        recommendations: AI recommendations
        simulated_at: Simulation timestamp
    """
    __tablename__ = "simulation_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, ForeignKey("projects.id"), nullable=False)
    scenario = Column(Text, nullable=False)
    affected_task_ids = Column(JSON)  # List of task IDs
    total_delay_days = Column(Integer, default=0, nullable=False)
    analysis = Column(Text, nullable=False)
    recommendations = Column(Text)
    simulated_at = Column(DateTime, default=datetime.utcnow, nullable=False, index=True)
    
    # Relationships
    project = relationship("Project", back_populates="simulation_logs")
