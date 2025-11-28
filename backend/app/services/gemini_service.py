"""
Gemini AI Service for task risk analysis and scenario simulation.
"""
import os
import json
import re
import requests
from typing import Dict, Any, List, Optional
from datetime import datetime

from app.config import settings


class GeminiService:
    """Service for interacting with Google Gemini AI API"""
    
    def __init__(self):
        self.api_key = settings.GEMINI_API_KEY
        self.base_url = "https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash-lite:generateContent"
        self.timeout = 30
        
        if not self.api_key:
            raise ValueError("GEMINI_API_KEY is not set in environment variables")
    
    def generate_content(self, prompt: str) -> str:
        """
        Call Gemini API with prompt and return text response.
        
        Args:
            prompt: Text prompt for AI
            
        Returns:
            str: AI response text
            
        Raises:
            Exception: If API call fails
        """
        headers = {
            "Content-Type": "application/json",
        }
        
        payload = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 2048,
                "topP": 0.95,
                "topK": 40
            }
        }
        
        url = f"{self.base_url}?key={self.api_key}"
        
        try:
            response = requests.post(
                url,
                headers=headers,
                json=payload,
                timeout=self.timeout
            )
            
            if response.status_code == 200:
                result = response.json()
                
                if "candidates" in result and len(result["candidates"]) > 0:
                    candidate = result["candidates"][0]
                    if "content" in candidate and "parts" in candidate["content"]:
                        text = candidate["content"]["parts"][0].get("text", "")
                        return text
                
                raise Exception("Invalid response format from Gemini API")
                
            else:
                error_detail = response.text
                raise Exception(f"Gemini API error (status {response.status_code}): {error_detail}")
                
        except requests.exceptions.Timeout:
            raise Exception("Gemini API request timeout")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Gemini API request failed: {str(e)}")
    
    def analyze_task_risk(self, tasks: List[Dict]) -> List[Dict]:
        """
        Analyze risk level for a list of tasks using AI.
        
        Args:
            tasks: List of task dictionaries with keys: id, name, progress, deadline, status, priority
            
        Returns:
            List[Dict]: List of risk analysis results with keys:
                - task_id
                - risk_level (low/medium/high/critical)
                - risk_percentage (0-100)
                - predicted_delay_days
                - analysis
                - recommendations
        """
        if not tasks:
            return []
        
        prompt = f"""Bạn là chuyên gia quản lý dự án. Phân tích các task sau và dự đoán nguy cơ trễ deadline:

{self._format_tasks(tasks)}

Với mỗi task, đánh giá:
- risk_level: "low", "medium", "high", hoặc "critical"
- risk_percentage: 0-100 (số thực)
- predicted_delay_days: số ngày dự đoán trễ (0 nếu không trễ)
- analysis: phân tích ngắn gọn bằng tiếng Việt (2-3 câu)
- recommendations: khuyến nghị cụ thể bằng tiếng Việt (2-3 điểm)

Trả về CHÍNH XÁC định dạng JSON array sau, không thêm text nào khác:
[
  {{
    "task_id": 1,
    "risk_level": "high",
    "risk_percentage": 75.5,
    "predicted_delay_days": 3,
    "analysis": "Task đang ở 60% sau 80% thời gian, tiến độ chậm",
    "recommendations": "Cần bổ sung nhân lực hoặc giảm scope"
  }}
]"""
        
        try:
            response = self.generate_content(prompt)
            result = self._parse_json_response(response)
            
            # Validate and ensure all tasks have results
            if isinstance(result, list):
                return result
            else:
                # If AI didn't return list, create fallback
                return self._create_fallback_risk_analysis(tasks, "AI response format invalid")
                
        except Exception as e:
            # Return fallback on error
            return self._create_fallback_risk_analysis(tasks, str(e))
    
    def analyze_bottleneck(self, stale_tasks: List[Dict]) -> str:
        """
        Analyze why tasks are stalled (bottleneck analysis).
        
        Args:
            stale_tasks: List of tasks that haven't been updated
            
        Returns:
            str: Analysis text in Vietnamese
        """
        if not stale_tasks:
            return "Không có task nào bị treo."
        
        prompt = f"""Các task sau không được cập nhật tiến độ trong thời gian dài:

{self._format_tasks(stale_tasks)}

Phân tích bằng tiếng Việt:
1. Nguyên nhân có thể gây bottleneck
2. Tác động đến dự án
3. Giải pháp đề xuất (3-5 điểm cụ thể)

Trả lời ngắn gọn, súc tích, dễ hiểu."""
        
        try:
            response = self.generate_content(prompt)
            return response.strip()
        except Exception as e:
            return f"Không thể phân tích bottleneck: {str(e)}"
    
    def simulate_scenario(self, project_data: Dict, scenario: str) -> Dict:
        """
        Simulate a what-if scenario for project.
        
        Args:
            project_data: Dictionary with keys: id, name, tasks (list of task dicts)
            scenario: Scenario description in Vietnamese
            
        Returns:
            Dict with keys:
                - affected_task_ids: List[int]
                - total_delay_days: int
                - analysis: str
                - recommendations: str
        """
        tasks = project_data.get("tasks", [])
        project_name = project_data.get("name", "Unknown")
        
        if not tasks:
            return {
                "affected_task_ids": [],
                "total_delay_days": 0,
                "analysis": "Dự án không có task nào để mô phỏng.",
                "recommendations": "Vui lòng thêm tasks vào dự án."
            }
        
        prompt = f"""Dự án hiện tại:
Tên: {project_name}
Tasks: 
{self._format_tasks(tasks)}

Kịch bản giả định: "{scenario}"

Phân tích bằng tiếng Việt:
1. Tasks nào bị ảnh hưởng? (liệt kê ID)
2. Dự án sẽ trễ bao nhiêu ngày?
3. Phân tích tác động chi tiết
4. Khuyến nghị giải pháp cụ thể

Trả về JSON format:
{{
  "affected_task_ids": [1, 3, 5],
  "total_delay_days": 7,
  "analysis": "Chi tiết phân tích bằng tiếng Việt",
  "recommendations": "Các khuyến nghị cụ thể bằng tiếng Việt"
}}"""
        
        try:
            response = self.generate_content(prompt)
            result = self._parse_json_response(response)
            
            # Validate result structure
            if isinstance(result, dict):
                return {
                    "affected_task_ids": result.get("affected_task_ids", []),
                    "total_delay_days": result.get("total_delay_days", 0),
                    "analysis": result.get("analysis", "Không có phân tích."),
                    "recommendations": result.get("recommendations", "Không có khuyến nghị.")
                }
            else:
                return self._create_fallback_simulation(tasks, scenario)
                
        except Exception as e:
            return self._create_fallback_simulation(tasks, scenario, str(e))
    
    def generate_summary(self, forecasts: List[Dict], tasks: List[Dict]) -> str:
        """
        Generate summary report of project status.
        
        Args:
            forecasts: List of forecast log dictionaries
            tasks: List of task dictionaries
            
        Returns:
            str: Summary text in Vietnamese (3-5 sentences)
        """
        if not forecasts and not tasks:
            return "Chưa có dữ liệu để tạo báo cáo."
        
        prompt = f"""Tạo báo cáo tóm tắt ngắn gọn (3-5 câu) bằng tiếng Việt về tình hình dự án:

Dự đoán rủi ro: {len(forecasts)} tasks được phân tích
Tasks đang thực hiện: {len(tasks)} tasks

Chi tiết:
{self._format_summary_data(forecasts, tasks)}

Format: Văn bản súc tích, dễ hiểu, highlight điểm quan trọng. Sử dụng emoji nếu phù hợp."""
        
        try:
            response = self.generate_content(prompt)
            return response.strip()
        except Exception as e:
            return f"Không thể tạo báo cáo tóm tắt: {str(e)}"
    
    def _format_tasks(self, tasks: List[Dict]) -> str:
        """Format tasks for prompt"""
        formatted = []
        for task in tasks:
            task_info = f"""- Task ID: {task.get('id', 'N/A')}
  Tên: {task.get('name', 'N/A')}
  Tiến độ: {task.get('progress', 0)}%
  Deadline: {task.get('deadline', 'N/A')}
  Ưu tiên: {task.get('priority', 'N/A')}
  Trạng thái: {task.get('status', 'N/A')}"""
            
            if 'last_progress_update' in task:
                task_info += f"\n  Cập nhật lần cuối: {task.get('last_progress_update', 'N/A')}"
            
            formatted.append(task_info)
        
        return "\n\n".join(formatted)
    
    def _format_summary_data(self, forecasts: List[Dict], tasks: List[Dict]) -> str:
        """Format data for summary prompt"""
        high_risk = [f for f in forecasts if f.get('risk_level') in ['high', 'critical']]
        in_progress = [t for t in tasks if t.get('status') == 'in_progress']
        done = [t for t in tasks if t.get('status') == 'done']
        
        return f"""- Tasks có rủi ro cao: {len(high_risk)}
- Tasks đang thực hiện: {len(in_progress)}
- Tasks hoàn thành: {len(done)}
- Tổng tasks: {len(tasks)}"""
    
    def _parse_json_response(self, response: str) -> Any:
        """
        Parse JSON from AI response with multiple strategies.
        
        Args:
            response: Raw AI response text
            
        Returns:
            Parsed JSON object (dict or list)
            
        Raises:
            Exception: If JSON cannot be parsed
        """
        # Strategy 1: Try direct JSON parse
        try:
            return json.loads(response)
        except json.JSONDecodeError:
            pass
        
        # Strategy 2: Extract JSON using regex (find array or object)
        json_patterns = [
            r'\[\s*\{.*?\}\s*\]',  # Array of objects
            r'\{.*?\}',  # Single object
        ]
        
        for pattern in json_patterns:
            match = re.search(pattern, response, re.DOTALL)
            if match:
                try:
                    json_str = match.group(0)
                    return json.loads(json_str)
                except json.JSONDecodeError:
                    continue
        
        # Strategy 3: Try to extract JSON from code blocks
        code_block_pattern = r'```(?:json)?\s*([\[\{].*?[\]\}])\s*```'
        match = re.search(code_block_pattern, response, re.DOTALL)
        if match:
            try:
                return json.loads(match.group(1))
            except json.JSONDecodeError:
                pass
        
        raise Exception(f"Cannot parse JSON from AI response: {response[:200]}")
    
    def _create_fallback_risk_analysis(self, tasks: List[Dict], error_msg: str = "") -> List[Dict]:
        """Create fallback risk analysis when AI fails"""
        results = []
        for task in tasks:
            progress = task.get('progress', 0)
            
            # Simple heuristic-based risk calculation
            if progress < 30:
                risk_level = "medium"
                risk_percentage = 50.0
            elif progress < 60:
                risk_level = "high"
                risk_percentage = 70.0
            else:
                risk_level = "low"
                risk_percentage = 30.0
            
            results.append({
                "task_id": task.get('id'),
                "risk_level": risk_level,
                "risk_percentage": risk_percentage,
                "predicted_delay_days": 0,
                "analysis": f"Phân tích tự động dựa trên tiến độ: {progress}%. (Lỗi AI: {error_msg})",
                "recommendations": "Theo dõi tiến độ thường xuyên và cập nhật kịp thời."
            })
        
        return results
    
    def _create_fallback_simulation(self, tasks: List[Dict], scenario: str, error_msg: str = "") -> Dict:
        """Create fallback simulation result when AI fails"""
        # Select first 2-3 tasks as affected
        affected = tasks[:min(3, len(tasks))]
        affected_ids = [t.get('id') for t in affected]
        
        return {
            "affected_task_ids": affected_ids,
            "total_delay_days": 5,
            "analysis": f"""Phân tích mô phỏng tự động cho kịch bản: "{scenario}"

Kết quả ước lượng:
- Số tasks bị ảnh hưởng: {len(affected_ids)}
- Thời gian trễ dự kiến: 5 ngày

(Lưu ý: Đây là phân tích dự phòng do lỗi AI: {error_msg})""",
            "recommendations": """Khuyến nghị:
1. Xem xét các task phụ thuộc
2. Chuẩn bị kế hoạch dự phòng
3. Tăng cường giám sát tiến độ"""
        }


# Singleton instance
gemini_service = GeminiService()
