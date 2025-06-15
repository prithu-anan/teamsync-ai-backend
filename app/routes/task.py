from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.models import Task, Project
from pydantic import BaseModel
from typing import Optional, List
import re
from collections import Counter
from app.deps import get_db
from app.llm.factory import get_llm_provider

router = APIRouter()
llm = get_llm_provider("deepseek")

# Request model for input validation
class EstimateDeadlineRequest(BaseModel):
    title: str
    description: str
    project_id: int
    parent_task_id: Optional[int] = None

# Fetch example tasks for few-shot prompting
def get_example_tasks(db: Session, project_id: int, parent_task_id: Optional[int], limit: int = 3) -> List[Task]:
    query = db.query(Task).filter(Task.project_id == project_id, Task.priority.isnot(None), Task.time_estimate.isnot(None))
    if parent_task_id:
        parent_task = db.query(Task).filter(Task.id == parent_task_id, Task.project_id == project_id).first()
        if parent_task:
            examples = [parent_task]
            siblings = db.query(Task).filter(Task.parent_task_id == parent_task_id, Task.project_id == project_id).limit(limit - 1).all()
            print(f"siblings : {siblings}")
            examples.extend(siblings)
            return examples[:limit]
    return query.limit(limit).all()

# Construct prompt for LLM
def construct_prompt(project: Project, example_tasks: List[Task], new_task: EstimateDeadlineRequest) -> str:
    prompt = "You are an AI assistant for an IT farm. Your task is to estimate the priority and time required for a new task based on its title, description, and related tasks in the project.\n\n"
    prompt += "Here is the project information:\n\n"
    prompt += f"Project Title: {project.title}\n"
    prompt += f"Project Description: {project.description or 'No description available'}\n\n"
    if example_tasks:
        prompt += "Here are some example tasks in the project:\n\n"
        for i, task in enumerate(example_tasks, 1):
            prompt += f"Task {i}:\n"
            prompt += f"Title: {task.title}\n"
            prompt += f"Description: {task.description or 'No description'}\n"
            prompt += f"Priority: {task.priority}\n"
            prompt += f"Time Estimate: {task.time_estimate}\n\n"
    prompt += "Now, here is the new task:\n\n"
    prompt += f"Title: {new_task.title}\n"
    prompt += f"Description: {new_task.description}\n\n"
    prompt += "Based on the above information, please estimate the priority (choose from 'low', 'medium', 'high', 'urgent') and the estimated time (in hours) for this new task. Also, provide a brief explanation for your reasoning.\n\n"
    prompt += "Please format your response as follows:\n\n"
    prompt += "Priority: [priority]\n"
    prompt += "Estimated Time: [time] hours\n"
    prompt += "Comment: [explanation]\n"
    return prompt

# Parse LLM response into structured data
def parse_response(response: str) -> Optional[dict]:
    priority_match = re.search(r"Priority:\s*(\w+)", response, re.IGNORECASE)
    time_match = re.search(r"Estimated Time:\s*([\d.]+)\s*hours", response, re.IGNORECASE)
    comment_match = re.search(r"Comment:\s*(.+)", response, re.DOTALL)
    if priority_match and time_match and comment_match:
        priority = priority_match.group(1).lower()
        allowed_priorities = {"low", "medium", "high", "urgent"}
        if priority not in allowed_priorities:
            return None
        try:
            time = float(time_match.group(1))
            if time <= 0:
                return None
        except ValueError:
            return None
        comment = comment_match.group(1).strip()
        return {"priority": priority, "estimated_time": time, "comment": comment}
    return None

# Format time into hours or days
def format_time(hours: float) -> str:
    if hours >= 24:
        days = hours / 24
        return f"{days:.1f} days"
    return f"{hours:.1f} hours"

# Aggregate multiple LLM responses
def aggregate_responses(parsed_responses: List[dict]) -> dict:
    if not parsed_responses:
        return None
    priorities = [resp["priority"] for resp in parsed_responses]
    times = [resp["estimated_time"] for resp in parsed_responses]
    priority_counter = Counter(priorities)
    most_common_priority = priority_counter.most_common(1)[0][0]
    average_time = sum(times) / len(times)
    formatted_time = format_time(average_time)
    comment = parsed_responses[0]["comment"]  # Use first comment
    return {
        "priority": most_common_priority,
        "estimated_time": formatted_time,
        "comment": comment
    }

# API endpoint
@router.post("/tasks/estimate-deadline")
def estimate_deadline(request: EstimateDeadlineRequest, db: Session = Depends(get_db)):
    # Fetch project
    project = db.query(Project).filter(Project.id == request.project_id).first()
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    # Fetch example tasks for few-shot prompting
    example_tasks = get_example_tasks(db, request.project_id, request.parent_task_id)

    # Construct LLM prompt
    prompt = construct_prompt(project, example_tasks, request)

    print(f"prompt : {prompt}")

    # Get LLM responses
    try:
        responses = llm.generate(prompt)
        print(f"llm said {responses}")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM request failed: {str(e)}")

    # Parse responses
    parsed_responses = [parse_response(resp) for resp in responses if parse_response(resp)]
    print(f"parsing: {parsed_responses}")
    if not parsed_responses:
        raise HTTPException(status_code=500, detail="Failed to parse valid responses from LLM")

    # Aggregate results
    result = aggregate_responses(parsed_responses)
    print(f"aggregate: {result}")
    if not result:
        raise HTTPException(status_code=500, detail="Failed to aggregate LLM responses")

    return result