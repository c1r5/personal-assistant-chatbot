from typing import Optional
from pydantic import BaseModel


class UserMessage(BaseModel):
    message_id: int
    # chat_id: int  # This field is not used in the current context, but can be added if needed
    message: Optional[str] = None 
    
class BotMessage(BaseModel):
    message: str
    # chat_id: int 
    reply_to_message_id: Optional[int] = None