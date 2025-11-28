"""
Webhooks router - handles callbacks from n8n workflows.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field
from typing import Optional, Any
from datetime import datetime

from app.database import get_db
from app.models.task import Task
from app.models.forecast_log import ForecastLog, RiskLevel
from app.models.automation_log import AutomationLog, AutomationStatus
from app.schemas.auth import MessageResponse

router = APIRouter(prefix="/api/webhooks/n8n", tags=["webhooks"])

class NewUserWebhook(BaseModel):
    """Schema for new user webhook from n8n"""
    user_id: int
    email_sent: bool = False
    demo_project_created: bool = False

class ForecastCompleteWebhook(BaseModel):
    """Schema for forecast complete webhook from n8n"""
    task_id: int
    risk_level: str
    risk_percentage: float = Field(..., ge=0, le=100)
    predicted_delay_days: int = 0
    ai_analysis: str
    recommendations: Optional[str] = None

class DeploySuccessWebhook(BaseModel):
    """Schema for deployment success webhook from GitHub Actions"""
    service: str  # "frontend" or "backend"
    status: str = "success"
    commit_sha: str
    deployed_at: str

class AutomationLogWebhook(BaseModel):
    """Schema for general automation log webhook"""
    workflow_name: str
    status: str  # "success", "failed", "running"
    input_data: Optional[Any] = None
    output_data: Optional[Any] = None
    error_message: Optional[str] = None
    execution_time_ms: Optional[int] = None

@router.post("/new-user", response_model=MessageResponse)
async def handle_new_user(
    webhook_data: NewUserWebhook,
    db: Session = Depends(get_db)
):
    """
    Nhận thông báo từ n8n sau khi xử lý user mới.
    
    Được gọi từ n8n Flow 3 (User Registration Automation).
    
    Args:
        webhook_data: Thông tin từ n8n
        db: Database session
        
    Returns:
        MessageResponse: Thông báo xác nhận
    """
    # Log automation execution
    log = AutomationLog(
        workflow_name="User Registration Automation",
        status=AutomationStatus.SUCCESS if webhook_data.email_sent and webhook_data.demo_project_created else AutomationStatus.FAILED,
        input_data={"user_id": webhook_data.user_id},
        output_data={
            "email_sent": webhook_data.email_sent,
            "demo_project_created": webhook_data.demo_project_created
        }
    )
    
    db.add(log)
    db.commit()
    
    return MessageResponse(
        message=f"Đã xử lý user ID {webhook_data.user_id} thành công",
        success=True
    )

@router.post("/forecast-complete", response_model=MessageResponse)
async def handle_forecast_complete(
    webhook_data: ForecastCompleteWebhook,
    db: Session = Depends(get_db)
):
    """
    Nhận kết quả forecast từ n8n.
    
    Được gọi từ n8n Flow 1 (Quick Progress Forecast).
    Lưu forecast log vào database.
    
    Args:
        webhook_data: Kết quả forecast từ n8n
        db: Database session
        
    Returns:
        MessageResponse: Thông báo xác nhận
        
    Raises:
        HTTPException 404: Nếu task không tồn tại
        HTTPException 400: Nếu risk_level không hợp lệ
    """
    # Verify task exists
    task = db.query(Task).filter(Task.id == webhook_data.task_id).first()
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Task ID {webhook_data.task_id} không tồn tại"
        )
    
    # Validate risk level
    try:
        risk_level_enum = RiskLevel(webhook_data.risk_level)
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Risk level không hợp lệ: {webhook_data.risk_level}"
        )
    
    # Create forecast log
    forecast = ForecastLog(
        task_id=webhook_data.task_id,
        risk_level=risk_level_enum,
        risk_percentage=webhook_data.risk_percentage,
        predicted_delay_days=webhook_data.predicted_delay_days,
        analysis=webhook_data.ai_analysis,
        recommendations=webhook_data.recommendations
    )
    
    db.add(forecast)
    
    # Log automation execution
    automation_log = AutomationLog(
        workflow_name="Quick Progress Forecast",
        status=AutomationStatus.SUCCESS,
        input_data={"task_id": webhook_data.task_id},
        output_data={
            "risk_level": webhook_data.risk_level,
            "risk_percentage": webhook_data.risk_percentage
        }
    )
    
    db.add(automation_log)
    db.commit()
    
    return MessageResponse(
        message=f"Đã lưu forecast cho task ID {webhook_data.task_id}",
        success=True
    )

@router.post("/deploy-success", response_model=MessageResponse)
async def handle_deploy_success(
    webhook_data: DeploySuccessWebhook,
    db: Session = Depends(get_db)
):
    """
    Nhận thông báo deploy thành công từ GitHub Actions.
    
    Được gọi từ n8n Flow 6 (CI/CD Deployment Notification).
    
    Args:
        webhook_data: Thông tin deployment
        db: Database session
        
    Returns:
        MessageResponse: Thông báo xác nhận
    """
    # Log automation execution
    log = AutomationLog(
        workflow_name="CI/CD Deployment",
        status=AutomationStatus.SUCCESS if webhook_data.status == "success" else AutomationStatus.FAILED,
        input_data={
            "service": webhook_data.service,
            "commit_sha": webhook_data.commit_sha
        },
        output_data={
            "deployed_at": webhook_data.deployed_at
        }
    )
    
    db.add(log)
    db.commit()
    
    return MessageResponse(
        message=f"Đã ghi nhận deployment {webhook_data.service}",
        success=True
    )

@router.post("/automation-log", response_model=MessageResponse)
async def handle_automation_log(
    webhook_data: AutomationLogWebhook,
    db: Session = Depends(get_db)
):
    """
    Endpoint tổng quát để nhận logs từ bất kỳ n8n workflow nào.
    
    Args:
        webhook_data: Thông tin automation log
        db: Database session
        
    Returns:
        MessageResponse: Thông báo xác nhận
    """
    try:
        status_enum = AutomationStatus(webhook_data.status)
    except ValueError:
        status_enum = AutomationStatus.FAILED
    
    log = AutomationLog(
        workflow_name=webhook_data.workflow_name,
        status=status_enum,
        input_data=webhook_data.input_data,
        output_data=webhook_data.output_data,
        error_message=webhook_data.error_message
    )
    
    db.add(log)
    db.commit()
    
    return MessageResponse(
        message=f"Đã ghi log cho workflow '{webhook_data.workflow_name}'",
        success=True
    )
