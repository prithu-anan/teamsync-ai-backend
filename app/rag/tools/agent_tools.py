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
FRONTEND_URL = os.getenv("FRONTEND_URL", "http://135.235.169.115:3000")

class GetCurrentUserInput(BaseModel):
    """Input for getting current user information"""
    description: str = Field(description="No input required for this tool")

class GetUserTasksInput(BaseModel):
    """Input for getting user tasks"""
    description: str = Field(description="No input required for this tool")

class GetPlatformOverviewInput(BaseModel):
    """Input for getting platform overview"""
    description: str = Field(description="No input required for this tool")

class GetProjectsInfoInput(BaseModel):
    """Input for getting projects information"""
    description: str = Field(description="No input required for this tool")

class GetDashboardInfoInput(BaseModel):
    """Input for getting dashboard information"""
    description: str = Field(description="No input required for this tool")

class GetKanbanInfoInput(BaseModel):
    """Input for getting kanban board information"""
    description: str = Field(description="No input required for this tool")

class GetCalendarInfoInput(BaseModel):
    """Input for getting calendar information"""
    description: str = Field(description="No input required for this tool")

class GetSocialFeedInfoInput(BaseModel):
    """Input for getting social feed information"""
    description: str = Field(description="No input required for this tool")

class GetMessagesInfoInput(BaseModel):
    """Input for getting messages information"""
    description: str = Field(description="No input required for this tool")

class GetWhiteboardInfoInput(BaseModel):
    """Input for getting whiteboard information"""
    description: str = Field(description="No input required for this tool")

class GetAIAssistantInfoInput(BaseModel):
    """Input for getting AI assistant information"""
    description: str = Field(description="No input required for this tool")

class GetFoundersInfoInput(BaseModel):
    """Input for getting founders information"""
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

def get_platform_overview() -> str:
    """
    Get a comprehensive overview of the TeamSync platform
    
    Returns:
        Formatted string describing the TeamSync platform
    """
    overview = f"""
# 🚀 TeamSync Platform Overview

**TeamSync** is an AI-powered collaboration platform built for tech companies. It's your all-in-one hub to manage projects, track tasks, chat (group & direct messages), and stay productive.

## 🎯 Core Mission
TeamSync combines project management, task tracking, messaging (DM & group chat), and an intelligent assistant—all in one place to help teams stay productive and aligned.

## 🎯 Ideal Users
- Tech teams and development teams
- Project managers and team leads
- Companies looking for integrated collaboration tools
- Teams that want AI-powered productivity assistance

## 🔑 Key Features

### 📊 **Project Management**
- Create and manage projects with role-based permissions
- Assign team members as admins, owners, or members
- Track project progress and milestones

### ✅ **Task Management**
- Visual Kanban board with drag-and-drop functionality
- AI-assisted task priority and deadline estimation
- Subtasks support with dependency tracking
- Calendar integration for scheduling

### 💬 **Communication**
- Real-time messaging for individuals and groups
- Create channels for team discussions
- AI-powered auto-replies with suggested intents
- Direct messaging for private conversations

### 🤖 **AI Assistant**
- History-aware and context-sensitive AI
- Query data directly from your database
- Navigate through complex workflows
- Multiple knowledge bases (Code Pilot, About Us, Technology & Business)

### 🎨 **Collaboration Tools**
- Collaborative whiteboard for visual planning
- Social feed for team culture building
- Event posts, polls, and celebrations

## 🌟 Why TeamSync?
- **Integrated Experience**: Everything in one platform
- **AI-Powered**: Smart assistance for productivity
- **Visual Management**: Kanban boards and whiteboards
- **Team Culture**: Social features for engagement
- **Scalable**: Grows with your team

**Frontend URL**: {FRONTEND_URL}
"""
    return overview

def get_projects_info() -> str:
    """
    Get information about the Projects section
    
    Returns:
        Formatted string describing the Projects functionality
    """
    projects_info = f"""
# 📁 Projects Management

**URL**: {FRONTEND_URL}/projects

## 🎯 Purpose
Manage projects with comprehensive role-based permissions and team collaboration features.

## 🔧 Capabilities

### 👥 **Role Management**
- **Admins/Owners**: Can create projects and assign tasks
- **Members**: Can view and work on assigned tasks
- **Role-based permissions**: Control who can do what

### 📋 **Project Features**
- Create new projects with descriptions and goals
- Assign team members with specific roles
- Track project progress and milestones
- Manage project settings and permissions

### 🔐 **Security & Permissions**
- Only owners/admins can create or assign tasks
- Role-based access control
- Secure project data and team information

## 🚀 How to Use
1. Navigate to the Projects page
2. Create a new project or select an existing one
3. Assign team members with appropriate roles
4. Start creating and assigning tasks

**Access URL**: {FRONTEND_URL}/projects
"""
    return projects_info

def get_dashboard_info() -> str:
    """
    Get information about the Dashboard section
    
    Returns:
        Formatted string describing the Dashboard functionality
    """
    dashboard_info = f"""
# 📊 Dashboard Overview

**URL**: {FRONTEND_URL}/

## 🎯 Purpose
High-level overview of your work status, projects, and events with quick access to key features.

## 📈 Dashboard Sections

### 🔝 **Top Section**
- Total number of tasks across all projects
- Total number of active projects
- Upcoming events and deadlines

### 🔘 **Top Right Buttons**
- **Schedule Task**: Opens Calendar for task scheduling
- **My Tasks**: Leads directly to Kanban board

### 📋 **Middle Section**
- Your active and completed tasks
- Quick task overview with status
- **View All** button leading to Kanban board

## 🎯 Key Benefits
- **Quick Overview**: See your workload at a glance
- **Fast Navigation**: Quick access to key features
- **Task Management**: Direct links to task creation and viewing
- **Calendar Integration**: Seamless scheduling workflow

## 🚀 Quick Actions
- Click "Schedule Task" to add new tasks to your calendar
- Click "My Tasks" to view your Kanban board
- Click "View All" to see all your tasks

**Access URL**: {FRONTEND_URL}/dashboard
"""
    return dashboard_info

def get_kanban_info() -> str:
    """
    Get information about the Kanban Board section
    
    Returns:
        Formatted string describing the Kanban Board functionality
    """
    kanban_info = f"""
# 📋 Kanban Board

**URL**: {FRONTEND_URL}/kanban

## 🎯 Purpose
Visual task management board with drag-and-drop functionality for intuitive task organization.

## 🎨 Board Features

### 📊 **Columns**
- **Todo**: New tasks waiting to be started
- **In Progress**: Tasks currently being worked on
- **Backlog**: Tasks planned but not yet started
- **Completed**: Finished tasks

### 🖱️ **Drag & Drop**
- Move tasks between columns to update status
- Visual feedback during task movement
- Real-time status updates

### 🔗 **Subtasks Support**
- Create subtasks with deadlines
- Status dependency between parent and child tasks
- Hierarchical task organization

### 🤖 **AI Assistance**
- AI-assisted task priority estimation
- Smart deadline suggestions with explanations
- Intelligent task categorization

## 🎯 Benefits
- **Visual Management**: See all tasks at a glance
- **Intuitive Interface**: Drag-and-drop for easy status updates
- **Task Dependencies**: Manage complex task relationships
- **AI Insights**: Get smart suggestions for task planning

## 🚀 How to Use
1. Navigate to the Kanban board
2. Drag tasks between columns to update status
3. Click on tasks to view details and subtasks
4. Use AI suggestions for priority and deadline setting

**Access URL**: {FRONTEND_URL}/kanban
"""
    return kanban_info

def get_calendar_info() -> str:
    """
    Get information about the Calendar section
    
    Returns:
        Formatted string describing the Calendar functionality
    """
    calendar_info = f"""
# 📅 Calendar

**URL**: {FRONTEND_URL}/calendar

## 🎯 Purpose
Schedule your tasks and events with visual planning and Kanban integration.

## 📆 Calendar Features

### 🎯 **Task Planning**
- Visual calendar interface for task scheduling
- Drag-and-drop task placement
- Time-based task organization

### 🔗 **Kanban Integration**
- Linked with Kanban board deadlines
- Automatic deadline synchronization
- Visual deadline tracking

### 📊 **Event Management**
- Schedule meetings and events
- Set reminders and notifications
- Track important dates

## 🎯 Benefits
- **Visual Planning**: See your schedule at a glance
- **Task Integration**: Seamless connection with Kanban tasks
- **Deadline Management**: Never miss important dates
- **Time Management**: Optimize your work schedule

## 🚀 How to Use
1. Navigate to the Calendar
2. Click on dates to schedule tasks
3. Drag tasks from Kanban to calendar
4. Set reminders and deadlines

**Access URL**: {FRONTEND_URL}/calendar
"""
    return calendar_info

def get_social_feed_info() -> str:
    """
    Get information about the Social Feed section
    
    Returns:
        Formatted string describing the Social Feed functionality
    """
    social_info = f"""
# 🎉 Social Feed

**URL**: {FRONTEND_URL}/social

## 🎯 Purpose
A private social feed to build team culture, celebrate events, and engage with your team.

## 🎊 Social Features

### 🎂 **Event Posts**
- Create birthday celebrations
- Work anniversary announcements
- Team milestone celebrations
- Custom event creation

### 📸 **Media Sharing**
- Upload images and photos
- Share team moments
- Visual content creation

### 📊 **Polls & Engagement**
- Create polls to gather team opinions
- Vote on team decisions
- Interactive team engagement
- Anonymous voting options

## 🎯 Benefits
- **Team Culture**: Build stronger team relationships
- **Celebration**: Recognize team achievements
- **Engagement**: Keep team members connected
- **Fun**: Add enjoyment to work environment

## 🚀 How to Use
1. Navigate to the Social Feed
2. Create event posts for celebrations
3. Upload images and share moments
4. Create polls for team decisions

**Access URL**: {FRONTEND_URL}/social
"""
    return social_info

def get_messages_info() -> str:
    """
    Get information about the Messages section
    
    Returns:
        Formatted string describing the Messages functionality
    """
    messages_info = f"""
# 💬 Messages

**URL**: {FRONTEND_URL}/messages

## 🎯 Purpose
Real-time messaging for individuals and groups with AI-powered auto-replies.

## 💬 Messaging Features

### 👥 **Group Chat**
- Create channels for team discussions
- Organize conversations by topic
- Team-wide announcements

### 💭 **Direct Messaging**
- Private conversations between team members
- One-on-one communication
- Secure private messaging

### 🤖 **AI-Powered Auto-Replies**
- Smart suggested intents
- Context-aware responses
- Automated message suggestions
- Intelligent conversation assistance

## 🎯 Benefits
- **Real-time Communication**: Instant messaging
- **Organized Discussions**: Channel-based organization
- **AI Assistance**: Smart reply suggestions
- **Flexible Communication**: Group and private options

## 🚀 How to Use
1. Navigate to Messages
2. Create channels for team discussions
3. Start direct messages with team members
4. Use AI suggestions for quick replies

**Access URL**: {FRONTEND_URL}/messages
"""
    return messages_info

def get_whiteboard_info() -> str:
    """
    Get information about the Whiteboard section
    
    Returns:
        Formatted string describing the Whiteboard functionality
    """
    whiteboard_info = f"""
# 🎨 Whiteboard

**URL**: {FRONTEND_URL}/whiteboard

## 🎯 Purpose
A collaborative drawing space for brainstorming, visual planning, and creative expression.

## 🖌️ Whiteboard Features

### 🎨 **Freeform Drawing**
- Draw with mouse or touch input
- Multiple drawing tools and colors
- Eraser and undo functionality

### 🧠 **Brainstorming**
- Visual idea organization
- Mind mapping capabilities
- Collaborative ideation

### 💾 **Save & Share**
- Save your creations
- Share with teammates
- Export drawings

### 🎯 **Task Planning**
- Visual task planning
- Whiteboard-style organization
- Creative problem solving

## 🎯 Benefits
- **Creative Expression**: Visual thinking and planning
- **Collaboration**: Team brainstorming sessions
- **Visual Organization**: Complex idea visualization
- **Fun Factor**: Enjoyable creative space

## 🚀 How to Use
1. Navigate to the Whiteboard
2. Start drawing with your mouse or touch
3. Use different tools and colors
4. Save and share your creations

**Vibe**: Feeling creative or bored? This is your space to play or think visually!

**Access URL**: {FRONTEND_URL}/whiteboard
"""
    return whiteboard_info

def get_ai_assistant_info() -> str:
    """
    Get information about the AI Assistant capabilities
    
    Returns:
        Formatted string describing the AI Assistant functionality
    """
    ai_assistant_info = f"""
# 🤖 AI Assistant

**Available in any context throughout the TeamSync platform**

## 🎯 Purpose
Ask questions, get guidance, or auto-complete tasks with our smart AI assistant that is history-aware and context-sensitive.

## 🧠 AI Capabilities

### 🔄 **History-Aware & Context-Sensitive**
- Remembers conversation history
- Understands context from previous interactions
- Provides personalized responses based on your usage

### 🛠️ **Complex Workflow Navigation**
- Navigate you through complex workflows
- Step-by-step guidance for platform features
- Help with multi-step processes

### 🔍 **Database Querying**
- Query data directly from your database
- Get information about your tasks, projects, and team
- Natural language questions about your data

### 🛠️ **Tool Integration**
- Show available tools it can use on your request
- Demonstrate platform capabilities
- Guide you to the right features

## 📚 **Knowledge Bases**

### 💻 **Code Pilot**
- Get help with Linux terminal commands
- Code-related queries and assistance
- Programming and development guidance

### 👥 **About Us**
- Learn about Suhas, Prithu and Riyad
- The three cool founders behind TeamSync
- Company background and team information

### 📈 **Technology & Business**
- Master productivity techniques
- Time management strategies
- Money-making techniques and business insights
- Professional development resources

## 🚀 **Modes of Operation**

### 💬 **Free-form Chat**
- General questions and assistance
- Casual conversation and support
- Platform guidance and help

### 🧠 **Contextual Knowledge-Base Assistant (RAG)**
- Access to specific knowledge bases
- Detailed information from curated content
- Context-aware responses based on knowledge sources

## 🔮 **Upcoming Features**
- Upload your own documents to extend assistant's capabilities
- Custom knowledge base creation
- Personalized learning paths

## 🎯 **How to Use**
- Ask questions in any chat interface
- Request guidance on platform features
- Get help with complex workflows
- Query your data using natural language
- Access knowledge bases for specific topics

## 🌟 **Benefits**
- **Always Available**: Access from anywhere in the platform
- **Context-Aware**: Understands your current situation
- **Knowledge-Rich**: Access to multiple knowledge bases
- **Workflow-Friendly**: Helps with complex processes
- **Personalized**: Learns from your interactions

**The AI Assistant is your intelligent companion throughout the TeamSync platform, ready to help with any question or task!**
"""
    return ai_assistant_info

def get_founders_info() -> str:
    """
    Get information about the founders of TeamSync
    
    Returns:
        Formatted string describing the founders
    """
    founders_info = f"""
# 🚀 TeamSync Founders

**TeamSync** was founded by three passionate individuals:

## 🧠 Suhas Abdullah
- **Role**: Co-Founder & CEO
- **Background**: Trainee Software Engineer at Pridesys, specializing in Backend Development, System Architecture and AI Engineering.
- **Why He Started**: Passion for building scalable, user-friendly platforms
- **Favorite Quote**: "The only way to do great work is to love what you do."

## 🧠 Prithu Anan
- **Role**: Co-Founder & CTO
- **Background**: Specializing in Frontend Development, Cloud Deployment, CI/CD pipelines.
- **Why He Started**: Love for technology and innovation
- **Favorite Quote**: "Innovation is the only way to stay ahead."

## 🧠 Riyad
- **Role**: Co-Founder & CMO
- **Background**: Specializing in Spring Authorization, End-to-End testing
- **Why He Started**: Passion for building great products
- **Favorite Quote**: "Success is not final, failure is not fatal: it is the courage to continue that counts."

## 📚 **For More Detailed Information**
To learn more about the founders, their backgrounds, and detailed stories, please select the **"about_us"** context in the RAG agent. This will give you access to comprehensive information about Suhas, Prithu, and Riyad, including their full profiles, achievements, and the story behind TeamSync.
"""
    return founders_info

def get_available_tools() -> str:
    """
    Get a formatted markdown description of all available tools
    
    Returns:
        Formatted markdown string describing available tools
    """
    tools_description = f"""
# Available Tools

Here are the tools you can use to interact with the TeamSync AI backend and navigate the platform:

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

## 🚀 **get_platform_overview**
**Purpose**: Get comprehensive information about the TeamSync platform

**When to use**:
- When users ask "What is TeamSync?" or "What can I do here?"
- When users want to understand the platform's capabilities
- When users need an overview of available features

**Returns**: Detailed platform description with features and benefits

---

## 📁 **get_projects_info**
**Purpose**: Get information about project management features

**When to use**:
- When users ask about creating or managing projects
- When users want to understand role-based permissions
- When users need guidance on project organization

**Returns**: Project management capabilities and navigation guide

---

## 📊 **get_dashboard_info**
**Purpose**: Get information about the dashboard and quick actions

**When to use**:
- When users ask about their work overview
- When users want to understand quick navigation options
- When users need help with task scheduling

**Returns**: Dashboard features and quick action guide

---

## 📋 **get_kanban_info**
**Purpose**: Get information about the Kanban board

**When to use**:
- When users ask about task management
- When users want to understand drag-and-drop functionality
- When users need help with task organization

**Returns**: Kanban board features and usage guide

---

## 📅 **get_calendar_info**
**Purpose**: Get information about calendar and scheduling

**When to use**:
- When users ask about scheduling tasks
- When users want to understand calendar integration
- When users need help with time management

**Returns**: Calendar features and scheduling guide

---

## 🎉 **get_social_feed_info**
**Purpose**: Get information about the social feed

**When to use**:
- When users ask about team culture features
- When users want to understand social engagement
- When users need help with team celebrations

**Returns**: Social feed features and engagement guide

---

## 💬 **get_messages_info**
**Purpose**: Get information about messaging features

**When to use**:
- When users ask about communication tools
- When users want to understand group vs direct messaging
- When users need help with team communication

**Returns**: Messaging features and communication guide

---

## 🎨 **get_whiteboard_info**
**Purpose**: Get information about the collaborative whiteboard

**When to use**:
- When users ask about visual collaboration
- When users want to understand brainstorming tools
- When users need help with creative planning

**Returns**: Whiteboard features and creative guide

---

## 🤖 **get_ai_assistant_info**
**Purpose**: Get information about the AI Assistant capabilities

**When to use**:
- When users ask about the AI assistant or its capabilities
- When users want to understand how to use the AI assistant
- When users ask about knowledge bases or AI features

**Returns**: Detailed AI Assistant capabilities and knowledge base information

---

## 🚀 **get_founders_info**
**Purpose**: Get information about the founders of TeamSync

**When to use**:
- When users ask about the founders or the company's founding story
- When users want to learn about who started TeamSync
- When users ask about the team behind the platform

**Returns**: Detailed information about Suhas, Prithu, and Riyad including their roles, backgrounds, and favorite quotes

---

## 🔒 **Security Note**
All tools use secure JWT authentication and only return non-sensitive information to protect user privacy.

## 🌐 **Frontend Navigation**
Most tools provide frontend URLs to help users navigate to the appropriate sections of the TeamSync platform.
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
    
    def get_platform_overview_tool() -> str:
        """Get comprehensive information about the TeamSync platform"""
        return get_platform_overview()
    
    def get_projects_info_tool() -> str:
        """Get information about project management features"""
        return get_projects_info()
    
    def get_dashboard_info_tool() -> str:
        """Get information about the dashboard and quick actions"""
        return get_dashboard_info()
    
    def get_kanban_info_tool() -> str:
        """Get information about the Kanban board"""
        return get_kanban_info()
    
    def get_calendar_info_tool() -> str:
        """Get information about calendar and scheduling"""
        return get_calendar_info()
    
    def get_social_feed_info_tool() -> str:
        """Get information about the social feed"""
        return get_social_feed_info()
    
    def get_messages_info_tool() -> str:
        """Get information about messaging features"""
        return get_messages_info()
    
    def get_whiteboard_info_tool() -> str:
        """Get information about the collaborative whiteboard"""
        return get_whiteboard_info()
    
    def get_ai_assistant_info_tool() -> str:
        """Get information about the AI Assistant capabilities"""
        return get_ai_assistant_info()
    
    def get_founders_info_tool() -> str:
        """Get information about the founders of TeamSync"""
        return get_founders_info()
    
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
            name="get_platform_overview",
            description="Get comprehensive information about the TeamSync platform including features, benefits, and navigation. ALWAYS use this when users ask 'What is TeamSync?', 'What can I do here?', 'Tell me about the platform', or want to understand what TeamSync is and what it offers.",
            func=get_platform_overview_tool,
        ),
        StructuredTool.from_function(
            name="get_projects_info",
            description="Get detailed information about project management features including URLs and navigation. ALWAYS use this when users ask about creating/managing projects, role-based permissions, project organization, or how to work with projects.",
            func=get_projects_info_tool,
        ),
        StructuredTool.from_function(
            name="get_dashboard_info",
            description="Get detailed information about the dashboard including URLs and quick actions. ALWAYS use this when users ask about their work overview, quick navigation, task scheduling, or the main dashboard features.",
            func=get_dashboard_info_tool,
        ),
        StructuredTool.from_function(
            name="get_kanban_info",
            description="Get detailed information about the Kanban board including URLs and task management features. ALWAYS use this when users ask about task management, drag-and-drop functionality, task organization, adding tasks, or where to manage their tasks.",
            func=get_kanban_info_tool,
        ),
        StructuredTool.from_function(
            name="get_calendar_info",
            description="Get detailed information about calendar and scheduling including URLs and features. ALWAYS use this when users ask about scheduling tasks, calendar integration, time management, or where to schedule their work.",
            func=get_calendar_info_tool,
        ),
        StructuredTool.from_function(
            name="get_social_feed_info",
            description="Get detailed information about the social feed including URLs and team culture features. ALWAYS use this when users ask about team culture, social engagement, team celebrations, or social features.",
            func=get_social_feed_info_tool,
        ),
        StructuredTool.from_function(
            name="get_messages_info",
            description="Get detailed information about messaging features including URLs and communication tools. ALWAYS use this when users ask about communication tools, group vs direct messaging, team communication, or messaging features.",
            func=get_messages_info_tool,
        ),
        StructuredTool.from_function(
            name="get_whiteboard_info",
            description="Get detailed information about the collaborative whiteboard including URLs and creative features. ALWAYS use this when users ask about visual collaboration, brainstorming tools, creative planning, or the whiteboard.",
            func=get_whiteboard_info_tool,
        ),
        StructuredTool.from_function(
            name="get_ai_assistant_info",
            description="Get detailed information about the AI Assistant capabilities, including its history-awareness, context-sensitivity, and knowledge bases. ALWAYS use this when users ask about the AI assistant, its capabilities, or how to use it.",
            func=get_ai_assistant_info_tool,
        ),
        StructuredTool.from_function(
            name="get_founders_info",
            description="Get detailed information about the founders of TeamSync, including their roles, backgrounds, and favorite quotes. ALWAYS use this when users ask about the founders or the company's founding story.",
            func=get_founders_info_tool,
        ),
        StructuredTool.from_function(
            name="get_available_tools",
            description="Get a formatted markdown description of all available tools. Use this when users ask about what tools are available, what they can do, or how to use the system.",
            func=get_available_tools_tool,
        ),
    ]
    
    return tools