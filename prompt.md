hey buddy my goal is to create an ai model that can predict the estimated time needed for completing a task of an it farm. 

a task is defined in the following way in the database: 


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
---

## ✅ PHASE 1: LLM-Based Time Estimation

---

### **1. Prompt Engineering: What Attributes to Include in LLM Prompt?**

To get high-quality estimates, you should **construct a detailed and structured prompt** with relevant attributes that an LLM can reason about. Here's a list of recommended fields:

#### 🧠 Recommended Prompt Fields for LLM

* `title` (short and precise summary of the task)
* `description` (detailed info—LLMs need this for understanding complexity)
* `status` (mainly for context)
* `priority` (affects urgency and task allocation)
* `assigned_to` (optional but may affect estimate if user-specific modeling is possible)
* `project_id` (could hint at domain/complexity if you encode project metadata later)
* `parent_task_id` (if present, provide title + time eistimates of the parent or sibling tasks)
* `historical_average_time_estimate` of similar tasks (once you accumulate some history)
* Any known `dependencies` or `blocked` info

#### 🧱 Example Prompt Structure for LLM

```python
"""
You are an AI assistant for an IT farm. Based on the task details below, estimate the amount of time (in hours or days) this task would likely take to complete.

Title: Build user login endpoint
Description: Implement login API in FastAPI using JWT auth and bcrypt for hashing. Include input validation and error handling.
Priority: Medium
Status: todo
Project: Internal Admin Portal
Dependencies: None
Parent Task: "Implement authentication module" (Estimated Time: 10 hours)

Please return your estimated time (in hours or days) in a concise numeric format.
"""
```

Use a few-shot strategy with examples if needed to stabilize output.

---

### **2. Should `deadline = assigned_at + time_estimate`?**

Yes, **in most cases, yes** – but with **exceptions**.

#### ✅ Recommended Strategy:

* **`smart_deadline = assigned_at + ai_time_estimate`** (default)
* However, allow overrides in these cases:

  * If `deadline` is provided manually by a PM
  * If the task is `blocked`, inherit `smart_deadline` from dependencies or adjust based on parent
  * If it's a subtask (`parent_task_id` exists), see point 3

Store both manual and smart deadlines so users can compare or override them.

---

### **3. Does `parent_task_id` affect deadline?**

Yes, **absolutely. Here’s how**:

#### 🌲 Inheritance & Influence from Parent Tasks

* A child task **should not exceed the parent’s deadline.**
* If the parent has a smart deadline, then:

  * `smart_deadline(child) <= smart_deadline(parent)`
* Parent task estimate can be split into chunks for children.

  * Ex: Parent task estimated 10 hrs → has 2 children → assume 5 hrs each (unless otherwise specified)
* This relationship is useful for **chained dependencies** or **epic decomposition**.

Later, this logic can be encoded as part of your feature engineering.

---

## 🚀 PHASE 2: Model-Based Estimation (ML Pipeline)

Once enough data has been collected, you can shift to a machine learning model.

---

### **4. ML Model Design (Preprocessing, Feature Engineering, etc.)**

#### 📦 Inputs (Raw Fields From DB)

From `Tasks` and `TaskStatusHistory`, extract:

* `title`, `description` (textual)
* `priority`, `status`, `project_id`, `parent_task_id`
* `assigned_to` (optional)
* `time_taken` = time between first `in_progress` and `completed` in TaskStatusHistory
* `assigned_at`, `deadline`
* Parent/sibling task data (if parent\_task\_id exists)

#### 🔨 Preprocessing

##### Textual Fields:

* `title`, `description` → **BERT embeddings or TF-IDF**
* Optionally fine-tune a sentence transformer to your domain for better encoding

##### Categorical:

* `priority` → One-hot or ordinal encoding
* `status` → Could be used as context but not a strong predictor unless early status shifts matter
* `project_id` → Use embeddings if many projects or treat as categorical

##### Numerical:

* `time_taken` → Target variable
* `estimated_time` → Can be used as a feature

##### Derived Features:

* Word count in description
* Avg. time of similar past tasks
* Time since `assigned_at`
* Parent task estimated time (if any)
* Number of sibling subtasks

---

### 🧠 Model Choices

Start simple:

* **Baseline**: Linear Regression with basic features
* **Intermediate**: XGBoost or RandomForest
* **Advanced**:

  * `MultiModal Transformer` (text + structured inputs)
  * or a hybrid MLP with numerical + BERT features

---

### 🎯 Output

* Predict:

  * `estimated_time` (in hours or days)
  * Optionally: classification (quick, medium, long tasks)

---

### ⚙️ Deployment (FastAPI Integration)

* Create `/predict-time-estimate` endpoint
* Accept JSON with task details
* Return numeric estimate + confidence score
* Log input-output pairs for future fine-tuning

---

## 🔄 Transition Plan

| Phase   | Method    | Estimation Field                                   | Notes                                       |
| ------- | --------- | -------------------------------------------------- | ------------------------------------------- |
| Phase 1 | LLM-based | `ai_time_estimate`                                 | Also set `smart_deadline`                   |
| Phase 2 | ML model  | `ai_time_estimate`                                 | Trained on `time_taken` from status history |
| Future  | Hybrid    | `ai_time_estimate` + confidence + LLM explanations | Advanced ensemble                           |

---

If you want, I can help you design the FastAPI route, model schema, and preprocessing script.

Let me know!

```python
from openai import OpenAI

client = OpenAI(
  base_url="https://openrouter.ai/api/v1",
  api_key="<OPENROUTER_API_KEY>",
)

completion = client.chat.completions.create(
  extra_headers={
    "HTTP-Referer": "<YOUR_SITE_URL>", # Optional. Site URL for rankings on openrouter.ai.
    "X-Title": "<YOUR_SITE_NAME>", # Optional. Site title for rankings on openrouter.ai.
  },
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