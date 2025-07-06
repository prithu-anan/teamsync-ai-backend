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
    Get tasks for the current user from the backend API
    
    Args:
        jwt_token: JWT token for authentication
    
    Returns:
        Formatted string with user tasks information (excluding sensitive data like user IDs)
    """
    try:
        # First get the current user to get their ID
        user_response = await make_authenticated_request("/auth/me", jwt_token)
        
        if user_response.get("code") != 200:
            return f"Failed to get user information: {user_response.get('message', 'Unknown error')}"
        
        user_data = user_response.get("data", {})
        user_id = user_data.get('id')
        
        if not user_id:
            return "Failed to get user ID"
        
        # Now get the user's tasks using the ID internally
        response = await make_authenticated_request(f"/tasks/{user_id}", jwt_token)
        
        if response.get("code") == 200:
            task_data = response.get("data", {})
            # Return task information without exposing the user ID
            return f"Task: {task_data.get('title', 'Unknown')} - Status: {task_data.get('status', 'Unknown')} - Priority: {task_data.get('priority', 'Unknown')} - Deadline: {task_data.get('deadline', 'Unknown')}"
        else:
            return f"Failed to get user tasks: {response.get('message', 'Unknown error')}"
            
    except Exception as e:
        return f"Error getting user tasks: {str(e)}"

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
        """Get tasks for the current user from the backend API"""
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
    ]
    
    return tools