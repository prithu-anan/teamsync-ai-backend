from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional, List, Union
from app.models.channel import Channel
from app.models.message import Message
from app.models.user import User
from app.llm.factory import get_llm_provider
from sqlalchemy import desc,or_
import json
from app.deps import get_db
import re

router = APIRouter()
llm = get_llm_provider("gemini")


# Request models for input validation
class ChannelAutoReplyRequest(BaseModel):
    channel_id: int
    sender_id: int
    parent_thread_id: Optional[int] = None


class DirectMessageAutoReplyRequest(BaseModel):
    recipient_id: int
    sender_id: int
    parent_thread_id: Optional[int] = None


# Response model
class ReplySuggestion(BaseModel):
    reply: str
    tone: str


class AutoReplyResponse(BaseModel):
    suggestions: List[ReplySuggestion]


# Fetch conversation context

# Fetch conversation context
def get_conversation_context(db: Session, channel_id: Optional[int] = None, recipient_id: Optional[int] = None, sender_id: Optional[int] = None, parent_thread_id: Optional[int] = None, limit: int = 10) -> List[Message]:
    query = db.query(Message)
    if channel_id:
        query = query.filter(Message.channel_id == channel_id)
    if recipient_id and sender_id:
        query = query.filter(
            or_(
                (Message.sender_id == sender_id) & (Message.recipient_id == recipient_id),
                (Message.sender_id == recipient_id) & (Message.recipient_id == sender_id)
            )
        )
    if parent_thread_id:
        query = query.filter(Message.thread_parent_id == parent_thread_id)
    return query.order_by(desc(Message.timestamp)).limit(limit).all()

# Construct LLM prompt
def construct_prompt(
    messages: List[Message], sender: User, recipient: Optional[User] = None
) -> str:
    prompt = """You are an expert communication assistant helping users craft quick replies in messaging channels. Your task is to generate 3 relevant, concise response suggestions for the sender based on the conversation context.

### Sender Information:
Name: {sender_name}
Role: {sender_role}

### Conversation Context:
""".format(
        sender_name=sender.name, sender_role=sender.designation or "Not specified"
    )
    for message in reversed(messages):  # Reverse to show oldest first
        sender_name = message.sender.name if message.sender else "Unknown"
        prompt += f"{sender_name} ({message.timestamp}): {message.content}\n"

    if recipient:
        prompt += f"\n### Recipient Information:\nName: {recipient.name}\nRole: {recipient.designation or 'Not specified'}\n"

    prompt += """
### Instructions:
1. Analyze the conversation flow and tone
2. Generate 3 distinct reply options that would be appropriate next responses for the sender
3. Vary the suggestions to cover different possible intents:
   - One straightforward continuation
   - One more detailed/expanded response
   - One alternative approach (question, humorous, etc.)
4. Keep suggestions brief (1-2 sentences max)
5. Match the tone of the existing conversation
6. Format response as JSON:
```json
[
    {"reply": "suggestion", "tone": "formal"},
    {"reply": "suggestion", "tone": "diplomatic"},
    {"reply": "suggestion", "tone": "friendly"}
]
"""
    return prompt


# Parse LLM response
# Parse LLM response
def parse_llm_response(response: str) -> List[ReplySuggestion]:
    try:
        # Remove markdown code fences and any surrounding text
        cleaned_response = re.sub(
            r"```json\n|\n```", "", response, flags=re.MULTILINE
        ).strip()
        suggestions = json.loads(cleaned_response)
        return [ReplySuggestion(reply=s["reply"], tone=s["tone"]) for s in suggestions]
    except json.JSONDecodeError as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to parse LLM response: {str(e)}"
        )


# API endpoint
@router.post("/channels/auto-reply", response_model=AutoReplyResponse)
def auto_reply(
    request: Union[ChannelAutoReplyRequest, DirectMessageAutoReplyRequest],
    db: Session = Depends(get_db),
):
    channel_id = getattr(request, "channel_id", None)
    recipient_id = getattr(request, "recipient_id", None)
    parent_thread_id = request.parent_thread_id
    sender_id = request.sender_id

    # Validate input
    if channel_id and recipient_id:
        raise HTTPException(
            status_code=400, detail="Cannot specify both channel_id and recipient_id"
        )
    if not (channel_id or recipient_id):
        raise HTTPException(
            status_code=400, detail="Must specify either channel_id or recipient_id"
        )

    # Validate sender exists
    sender = db.query(User).filter(User.id == sender_id).first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender not found")

    # Validate channel or recipient exists
    if channel_id:
        channel = db.query(Channel).filter(Channel.id == channel_id).first()
        if not channel:
            raise HTTPException(status_code=404, detail="Channel not found")
    if recipient_id:
        recipient = db.query(User).filter(User.id == recipient_id).first()
        if not recipient:
            raise HTTPException(status_code=404, detail="Recipient not found")
    else:
        recipient = None

    # Fetch conversation context
    messages = get_conversation_context(db, channel_id, recipient_id, sender_id,parent_thread_id)

    # Construct LLM prompt
    prompt = construct_prompt(messages, sender, recipient)

    print(f"prompt: {prompt}")

    # Get LLM response
    try:
        responses = llm.generate(prompt)
        print(f"llm said: {responses[0]}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"LLM request failed: {str(e)}")

    # Parse response
    suggestions = parse_llm_response(responses[0] if responses else "[]")

    return AutoReplyResponse(suggestions=suggestions)
