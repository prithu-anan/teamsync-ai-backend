I want to create the following api endpoint.

POST: /channels/auto-reply

request body:

```json
{
    "channel_id": 1,
    "parent_thread_id": 2 (optional)
}
```

reply: 3 reply suggestions and tone from the LLM based on the previous messages context

```json
{
    {
        "reply-1": "suggestion",
        "tone": "formal"
    },
     {"reply-2": "suggestion",
     "tone": "diplomatic"},
     {"reply-3": "suggestion",
     "tone": "friendly"}
}

```

- Relevant tables in the database

```sql
-- Channels table
CREATE TABLE Channels (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    type channel_type NOT NULL,
    project_id INTEGER REFERENCES Projects(id) ON DELETE SET NULL,
    members INTEGER[] -- Could be normalized into a ChannelMembers junction table
);

-- Messages table
CREATE TABLE Messages (
    id SERIAL PRIMARY KEY,
    sender_id INTEGER NOT NULL REFERENCES Users(id) ON DELETE RESTRICT,
    channel_id INTEGER REFERENCES Channels(id) ON DELETE SET NULL,
    recipient_id INTEGER REFERENCES Users(id) ON DELETE SET NULL,
    content TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL DEFAULT CURRENT_TIMESTAMP,
    thread_parent_id INTEGER REFERENCES Messages(id) ON DELETE SET NULL,
    CHECK (channel_id IS NOT NULL OR recipient_id IS NOT NULL) -- Ensure at least one is set
);

CREATE TABLE Users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL,
    profile_picture VARCHAR(255),
    designation VARCHAR(255),
    birthdate DATE,
    join_date DATE,
    mood_score FLOAT,
    predicted_burnout_risk BOOLEAN
);

```

Consider the following factors while designing the prompt:

You are an expert communication assistant helping users craft quick replies in messaging channels. Your task is to generate 3 relevant, concise response suggestions based on the conversation context.

### Conversation Context:
[Insert the last 5-10 messages from the channel/thread here, with sender names and timestamps]

### User Information:
[Optional: Include relevant user info if available, like name/role]

### Instructions:
1. Analyze the conversation flow and tone
2. Generate 3 distinct reply options that would be appropriate next responses
3. Vary the suggestions to cover different possible intents:
   - One straightforward continuation
   - One more detailed/expanded response
   - One alternative approach (question, humorous, etc.)
4. Keep suggestions brief (1-2 sentences max)
5. Match the tone of the existing conversation

