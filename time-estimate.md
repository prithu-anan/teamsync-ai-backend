I am using fast api based ai-backend. The code structure can be found in **digest.txt**. We will implement a new api in **task.py** , specification of which is given below: 

GET endpoint: /tasks/estimate-deadline

the request body contains the following fields: 

* `title` (short and precise summary of the task)
* `description` (detailed info—LLMs need this for understanding complexity)
* `project_id` (could hint at domain/complexity by using project metadata)
* `parent_task_id` (if given, fetch title + description + time estimates of the parent or sibling tasks for few shot prompting)

**response**

```json
{
    "priority": "high,medium,low,urgent",
    "estimated time": "in days or hours",
    "comment": "explanation of the reasoning" 
}
```

**Relevant tables structure**

```sql
CREATE TYPE task_status AS ENUM ('backlog', 'todo', 'in_progress', 'in_review', 'blocked', 'completed');
CREATE TYPE task_priority AS ENUM ('low', 'medium', 'high', 'urgent');
-- Tasks table
CREATE TABLE tasks (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    status task_status NOT NULL,
    deadline TIMESTAMP WITH TIME ZONE,
    priority task_priority,
    time_estimate VARCHAR(50),
    ai_time_estimate VARCHAR(50),
    ai_priority task_priority,
    smart_deadline TIMESTAMP WITH TIME ZONE,
    project_id INTEGER NOT NULL REFERENCES Projects(id) ON DELETE CASCADE,
    assigned_to INTEGER REFERENCES Users(id) ON DELETE SET NULL,
    assigned_by INTEGER REFERENCES Users(id) ON DELETE SET NULL,
    assigned_at TIMESTAMP WITH TIME ZONE,
    parent_task_id INTEGER REFERENCES Tasks(id) ON DELETE SET NULL,
    attachments TEXT[]
);

-- TaskStatusHistory table
CREATE TABLE taskstatushistory (
    id SERIAL PRIMARY KEY,
    task_id INTEGER NOT NULL REFERENCES Tasks(id) ON DELETE CASCADE,
    status task_status NOT NULL,
    changed_by INTEGER NOT NULL REFERENCES Users(id) ON DELETE RESTRICT,
    changed_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    comment TEXT
);

CREATE TABLE projects (
    id SERIAL PRIMARY KEY,
    title VARCHAR(255) NOT NULL,
    description TEXT,
    created_by INTEGER NOT NULL REFERENCES Users(id) ON DELETE RESTRICT,
    created_at TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP
);

```

We will use the following template to converse with LLM except the api key must be loaded from environment variable **DEEPSEEK_API_KEY** -

```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<OPENROUTER_API_KEY>",
)

completion = client.chat.completions.create(
  extra_body={},
  model="deepseek/deepseek-r1-0528:free",
  messages=[
    {
      "role": "user",
      "content": "What is the meaning of life?"
    }
  ]
)
print(completion.choices[0].message.content)

```

Your task is to implement the api considering the below points: 

1. LLM will play the role of an AI assistant for an IT farm. Based on the task detail it will classify the priority from one of these four categories (high,medium,low,urgent) and the estimated time.

2. The factors affecting the time estimate for a task are, 

- nature of the parent task (can be found by fetching the parent task using parent_task_id when provided)
- nature of its sibling tasks
- the metadata of the project (from project_id)

3. Use few shot strategy to stabilize output

4. Generate multiple answer and then perform majority voting