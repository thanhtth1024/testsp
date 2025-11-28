"""
Automation logs router - handles n8n workflow execution logs.
"""
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.models.user import User
from app.models.automation_log import AutomationLog, AutomationStatus
from app.schemas.automation_log import AutomationLogResponse, AutomationLogListResponse
from app.utils.auth import get_current_user

router = APIRouter(prefix="/api/automation-logs", tags=["automation-logs"])

@router.get("", response_model=AutomationLogListResponse)
async def get_automation_logs(
    workflow_name: Optional[str] = Query(None, description="Filter by workflow name"),
    status_filter: Optional[str] = Query(None, alias="status", description="Filter by status"),
    skip: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=500),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy danh sách logs từ các n8n workflows.
    
    Endpoint này để xem lịch sử automation execution.
    
    Args:
        workflow_name: Lọc theo tên workflow
        status_filter: Lọc theo trạng thái (success/failed/running)
        skip: Số lượng bản ghi bỏ qua
        limit: Số lượng bản ghi tối đa
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        AutomationLogListResponse: Danh sách logs và tổng số
    """
    query = db.query(AutomationLog)
    
    # Apply filters
    if workflow_name:
        query = query.filter(AutomationLog.workflow_name.ilike(f"%{workflow_name}%"))
    
    if status_filter:
        try:
            status_enum = AutomationStatus(status_filter)
            query = query.filter(AutomationLog.status == status_enum)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Trạng thái không hợp lệ. Chọn: success, failed, hoặc running"
            )
    
    # Order by executed_at descending (newest first)
    query = query.order_by(AutomationLog.executed_at.desc())
    
    # Get total count
    total = query.count()
    
    # Get paginated results
    logs = query.offset(skip).limit(limit).all()
    
    # Build response
    logs_response = []
    for log in logs:
        log_dict = {
            "id": log.id,
            "workflow_name": log.workflow_name,
            "status": log.status.value,
            "input_data": log.input_data,
            "output_data": log.output_data,
            "error_message": log.error_message,
            "executed_at": log.executed_at
        }
        logs_response.append(AutomationLogResponse(**log_dict))
    
    return AutomationLogListResponse(logs=logs_response, total=total)

@router.get("/{log_id}", response_model=AutomationLogResponse)
async def get_automation_log(
    log_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Lấy chi tiết một automation log.
    
    Args:
        log_id: ID của log
        db: Database session
        current_user: Người dùng hiện tại
        
    Returns:
        AutomationLogResponse: Chi tiết log
        
    Raises:
        HTTPException 404: Nếu log không tồn tại
    """
    log = db.query(AutomationLog).filter(AutomationLog.id == log_id).first()
    
    if not log:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Không tìm thấy log"
        )
    
    log_dict = {
        "id": log.id,
        "workflow_name": log.workflow_name,
        "status": log.status.value,
        "input_data": log.input_data,
        "output_data": log.output_data,
        "error_message": log.error_message,
        "executed_at": log.executed_at
    }
    
    return AutomationLogResponse(**log_dict)
