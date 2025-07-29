"""
Agent Tools for Backend API Integration

This module provides tools that can be used by LangChain agents to interact with the backend API.
All tools require JWT authentication for making API calls.
"""

import os
import aiohttp
import asyncio
from typing import Dict, Any, Optional
from langchain_core.tools import StructuredTool
from pydantic import BaseModel, Field

# Get base server URL from environment
BASE_SERVER_URL = os.getenv("BASE_SERVER_URL", "http://localhost:8080")

class GetCurrentUserInput(BaseModel):
    """Input for getting current user information"""
    description: str = Field(description="No input required for this tool")

class GetUserTasksInput(BaseModel):
    """Input for getting user tasks"""
    description: str = Field(description="No input required for this tool")

async def make_authenticated_request(
    endpoint: str, 
    jwt_token: str, 
    method: str = "GET",
    data: Optional[Dict] = None
) -> Dict[str, Any]:
    """
    Make an authenticated request to the backend API
    
    Args:
        endpoint: API endpoint (e.g., "/auth/me")
        jwt_token: JWT token for authentication
        method: HTTP method (GET, POST, PUT, DELETE)
        data: Request data for POST/PUT requests
    
    Returns:
        API response as dictionary
    """
    url = f"{BASE_SERVER_URL}{endpoint}"
    headers = {
        "Authorization": f"Bearer {jwt_token}",
        "Content-Type": "application/json"
    }
    
    try:
        async with aiohttp.ClientSession() as session:
            if method.upper() == "GET":
                async with session.get(url, headers=headers) as response:
                    return await response.json()
            elif method.upper() == "POST":
                async with session.post(url, headers=headers, json=data) as response:
                    return await response.json()
            elif method.upper() == "PUT":
                async with session.put(url, headers=headers, json=data) as response:
                    return await response.json()
            elif method.upper() == "DELETE":
                async with session.delete(url, headers=headers) as response:
                    return await response.json()
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")
                
    except Exception as e:
        return {
            "error": f"Failed to make API request: {str(e)}",
            "status": "error"
        }

async def get_current_user(jwt_token: str) -> str:
    """
    Get current user information from the backend API
    
    Args:
        jwt_token: JWT token for authentication
    
    Returns:
        Formatted string with user information (excluding sensitive data like IDs)
    """
    try:
        response = await make_authenticated_request("/auth/me", jwt_token)
        
        if response.get("code") == 200:
            user_data = response.get("data", {})
            # Only return non-sensitive information
            name = user_data.get('name', 'Unknown')
            email = user_data.get('email', 'Unknown')
            return f"Current user: {name} (Email: {email})"
        else:
            return f"Failed to get user information: {response.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"Error getting user information: {str(e)}"

async def get_user_tasks(jwt_token: str) -> str:
    """
    Get tasks assigned to the current user from the backend API
    
    Args:
        jwt_token: JWT token for authentication
    
    Returns:
        Formatted string with user tasks information (excluding sensitive data like user IDs)
    """
    try:
        response = await make_authenticated_request(f"/tasks/user/assigned", jwt_token)

        # print(f"user tasks {response}")
        
        if response.get("code") == 200:
            tasks_data = response.get("data", [])
            
            if not tasks_data:
                return "No tasks found for the current user."
            
            # Handle list of tasks
            if isinstance(tasks_data, list):
                tasks_info = []
                for i, task in enumerate(tasks_data, 1):
                    title = task.get('title', 'Unknown')
                    status = task.get('status', 'Unknown')
                    priority = task.get('priority', 'Unknown')
                    deadline = task.get('deadline', 'Unknown')
                    description = task.get('description', 'No description')
                    
                    task_info = f"{i}. {title} - Status: {status} - Priority: {priority} - Deadline: {deadline} - Description: {description}"
                    tasks_info.append(task_info)
                
                return f"User has {len(tasks_data)} task(s):\n" + "\n".join(tasks_info)
            else:
                # Handle single task (fallback)
                task_data = tasks_data
                return f"Task: {task_data.get('title', 'Unknown')} - Status: {task_data.get('status', 'Unknown')} - Priority: {task_data.get('priority', 'Unknown')} - Deadline: {task_data.get('deadline', 'Unknown')}"
        else:
            return f"Failed to get user tasks: {response.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"Error getting user tasks: {str(e)}"

def get_available_tools() -> str:
    """
    Get a formatted markdown description of all available tools
    
    Returns:
        Formatted markdown string describing available tools
    """
    tools_description = """
# Available Tools

Here are the tools you can use to interact with the TeamSync AI backend:

## 🔗 **get_current_user**
**Purpose**: Retrieve current user information from the backend API

**When to use**: 
- When users ask about their profile, account, or personal information

**Returns**: User's name and email address

---

## 📋 **get_user_tasks**
**Purpose**: Get all tasks assigned to the current user from the backend API

**When to use**:
- When users ask about their tasks, assignments, or work items
- When users want to see what they need to work on
- When users ask about their workload or responsibilities

**Returns**: A formatted list of tasks including:
- Task title and description
- Current status (todo, in_progress, completed, etc.)
- Priority level (low, medium, high, urgent)
- Deadline information

---

## 🔒 **Security Note**
All tools use secure JWT authentication and only return non-sensitive information to protect user privacy.
"""
    return tools_description

# Create LangChain tools
def create_agent_tools(jwt_token: str):
    """
    Create LangChain tools with JWT authentication
    
    Args:
        jwt_token: JWT token for authentication
    
    Returns:
        List of StructuredTool instances
    """
    
    def get_current_user_tool() -> str:
        """Get current user information from the backend API"""
        try:
            # Run async function in sync context
            import asyncio
            import concurrent.futures
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(get_current_user(jwt_token))
                finally:
                    loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async)
                return future.result()
        except Exception as e:
            return f"Error getting user information: {str(e)}"
    
    def get_user_tasks_tool() -> str:
        """Get tasks assigned to the current user from the backend API"""
        try:
            # Run async function in sync context
            import asyncio
            import concurrent.futures
            
            def run_async():
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(get_user_tasks(jwt_token))
                finally:
                    loop.close()
            
            with concurrent.futures.ThreadPoolExecutor() as executor:
                future = executor.submit(run_async)
                return future.result()
        except Exception as e:
            return f"Error getting user tasks: {str(e)}"
    
    def get_available_tools_tool() -> str:
        """Get a formatted description of all available tools"""
        return get_available_tools()
    
    tools = [
        StructuredTool.from_function(
            name="get_current_user",
            description="Get current user information from the backend API. Use this when the user asks about their profile, account, or personal information.",
            func=get_current_user_tool,
        ),
        StructuredTool.from_function(
            name="get_user_tasks",
            description="Get tasks for the current user from the backend API. Use this when the user asks about their tasks, assignments, or work items.",
            func=get_user_tasks_tool,
        ),
        StructuredTool.from_function(
            name="get_available_tools",
            description="Get a formatted markdown description of all available tools. Use this when users ask about what tools are available, what they can do, or how to use the system.",
            func=get_available_tools_tool,
        ),
    ]
    
    return tools