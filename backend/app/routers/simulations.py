"""
Simulations router - handles scenario simulation with AI integration.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime

from app.database import get_db
from app.models.user import User
from app.models.project import Project
from app.models.task import Task
from app.models.simulation_log import SimulationLog
from app.models.automation_log import AutomationLog, AutomationStatus
from app.schemas.simulation import SimulationRequest, SimulationResponse, SimulationListResponse
from app.utils.auth import get_current_user
from app.services.gemini_service import gemini_service

router = APIRouter(prefix="/api/simulations", tags=["simulations"])

@router.get("", response_model=SimulationListResponse)
async def get_simulations(
    project_id: Optional[int] = Query(None, description="Filter by project ID"),
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách các mô phỏng kịch bản đã chạy.
    
    User chỉ thấy simulations của projects mình sở hữu.
    Admin thấy tất cả.
    
    Args:
        project_id: Lọc theo project ID
        skip: Số lượng bản ghi bỏ qua
        limit: Số lượng bản ghi tối đa
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        SimulationListResponse: Danh sách simulations và tổng số
    """
    query = db.query(SimulationLog)
    
    # Apply authorization filter
    if current_user.role != "admin":
        query = query.join(Project).filter(Project.owner_id == current_user.id)
    
    # Apply filters
    if project_id:
        query = query.filter(SimulationLog.project_id == project_id)
    
    # Order by simulated_at descending (newest first)
    query = query.order_by(SimulationLog.simulated_at.desc())
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    simulations = query.offset(skip).limit(limit).all()
    
    # Build response
    simulations_response = []
    for sim in simulations:
        sim_dict = {
            "id": sim.id,
            "project_id": sim.project_id,
            "scenario": sim.scenario,
            "affected_task_ids": sim.affected_task_ids or [],
            "total_delay_days": sim.total_delay_days,
            "analysis": sim.analysis,
            "recommendations": sim.recommendations,
            "simulated_at": sim.simulated_at
        }
        simulations_response.append(SimulationResponse(**sim_dict))
    
    return SimulationListResponse(simulations=simulations_response, total=total)

@router.post("/run", response_model=SimulationResponse, status_code=status.HTTP_201_CREATED)
async def run_simulation(
    simulation_data: SimulationRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Chạy mô phỏng kịch bản "What-if" sử dụng AI.
    
    Sử dụng Gemini AI để phân tích tác động của kịch bản giả định.
    
    Args:
        simulation_data: Thông tin mô phỏng
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        SimulationResponse: Kết quả mô phỏng
        
    Raises:
        HTTPException 404: Nếu project không tồn tại
        HTTPException 403: Nếu không có quyền truy cập
    """
    # Verify project exists and user has access
    project = db.query(Project).filter(Project.id == simulation_data.project_id).first()
    if not project:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy dự án"
        )
    
    if current_user.role != "admin" and project.owner_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Không có quyền chạy mô phỏng cho dự án này"
        )
    
    # Get project tasks for context
    tasks = db.query(Task).filter(Task.project_id == project.id).all()
    
    # Prepare data for AI
    task_data = []
    for task in tasks:
        task_data.append({
            "id": task.id,
            "name": task.name,
            "progress": task.progress,
            "deadline": task.deadline.isoformat() if task.deadline else None,
            "status": task.status.value if hasattr(task.status, 'value') else task.status,
            "priority": task.priority.value if hasattr(task.priority, 'value') else task.priority,
        })
    
    project_data = {
        "id": project.id,
        "name": project.name,
        "tasks": task_data
    }
    
    # Log automation start
    automation_log = AutomationLog(
        workflow_name="AI Scenario Simulation",
        status=AutomationStatus.RUNNING,
        input_data={
            "project_id": project.id,
            "scenario": simulation_data.scenario,
            "task_count": len(tasks)
        }
    )
    db.add(automation_log)
    db.commit()
    
    # Call AI service
    try:
        ai_result = gemini_service.simulate_scenario(project_data, simulation_data.scenario)
        
        # Save simulation log
        new_simulation = SimulationLog(
            project_id=simulation_data.project_id,
            scenario=simulation_data.scenario,
            affected_task_ids=ai_result.get("affected_task_ids", []),
            total_delay_days=ai_result.get("total_delay_days", 0),
            analysis=ai_result.get("analysis", ""),
            recommendations=ai_result.get("recommendations", "")
        )
        
        db.add(new_simulation)
        
        # Update automation log success
        automation_log.status = AutomationStatus.SUCCESS
        automation_log.output_data = {
            "simulation_id": new_simulation.id,
            "affected_tasks": len(ai_result.get("affected_task_ids", [])),
            "delay_days": ai_result.get("total_delay_days", 0)
        }
        
        db.commit()
        db.refresh(new_simulation)
        
        # Build response
        sim_dict = {
            "id": new_simulation.id,
            "project_id": new_simulation.project_id,
            "scenario": new_simulation.scenario,
            "affected_task_ids": new_simulation.affected_task_ids or [],
            "total_delay_days": new_simulation.total_delay_days,
            "analysis": new_simulation.analysis,
            "recommendations": new_simulation.recommendations,
            "simulated_at": new_simulation.simulated_at
        }
        
        return SimulationResponse(**sim_dict)
        
    except Exception as e:
        # Update automation log failure
        automation_log.status = AutomationStatus.FAILED
        automation_log.error_message = str(e)
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Lỗi khi chạy mô phỏng AI: {str(e)}"
        )
