import os
import logging

from aiostream import stream
from fastapi import APIRouter, Depends, HTTPException, Request, status
from llama_index.core.llms import MessageRole
from llama_index.core.chat_engine.types import BaseChatEngine
from llama_index.core.vector_stores.types import MetadataFilters, MetadataFilter
from app.engine import get_chat_engine
from app.api.routers.vercel_response import VercelStreamResponse
from app.api.routers.events import EventCallbackHandler
from app.api.routers.models import (
    ChatData,
    ChatConfig,
    SourceNodes,
    Result,
    Message,
)

from typing import Dict, List

# Initialize a dictionary to store chat histories
chat_histories: Dict[str, List[Message]] = {}

chat_router = r = APIRouter()

logger = logging.getLogger("uvicorn")


# streaming endpoint - delete if not needed
@r.post("")
async def chat(
    request: Request,
    data: ChatData,
):
    try:
        last_message_content = data.get_last_message_content()
        messages = data.get_history_messages()

        doc_ids = data.get_chat_document_ids()
        filters = generate_filters(doc_ids)
        logger.info("Creating chat engine with filters", filters.dict())
        chat_engine = get_chat_engine(filters=filters)

        event_handler = EventCallbackHandler()
        chat_engine.callback_manager.handlers.append(event_handler)  # type: ignore
        response = await chat_engine.astream_chat(last_message_content, messages, tool_choice="JapanTravelTips")

        return VercelStreamResponse(request, event_handler, response)
    except Exception as e:
        logger.exception("Error in chat engine", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error in chat engine: {e}",
        ) from e


def generate_filters(doc_ids):
    if len(doc_ids) > 0:
        filters = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="private",
                    value="true",
                    operator="!=",  # type: ignore
                ),
                MetadataFilter(
                    key="doc_id",
                    value=doc_ids,
                    operator="in",  # type: ignore
                ),
            ],
            condition="or",  # type: ignore
        )
    else:
        filters = MetadataFilters(
            filters=[
                MetadataFilter(
                    key="private",
                    value="true",
                    operator="!=",  # type: ignore
                ),
            ]
        )

    return filters

def add_chat_history(chat_id: str, message: str, role="user"):
    # Store the user message in the chat history
    if chat_id not in chat_histories:
        chat_histories[chat_id] = []
    
    if role == "user":
        user_message = Message(role=MessageRole.USER, content=message)
    else:
        user_message = Message(role=MessageRole.ASSISTANT, content=message)
    chat_histories[chat_id].append(user_message)

# non-streaming endpoint - delete if not needed
@r.post("/request")
async def chat_request(
    data: ChatData,
    chat_engine: BaseChatEngine = Depends(get_chat_engine),
) -> Result:
    last_message_content = data.get_last_message_content()
    messages = data.get_history_messages()
    response = await chat_engine.achat(last_message_content, messages, tool_choice="JapanTravelTips")
    return Result(
        result=Message(role=MessageRole.ASSISTANT, content=response.response),
        nodes=SourceNodes.from_source_nodes(response.source_nodes),
    )


@r.get("/config")
async def chat_config() -> ChatConfig:
    starter_questions = None
    conversation_starters = os.getenv("CONVERSATION_STARTERS")
    if conversation_starters and conversation_starters.strip():
        starter_questions = conversation_starters.strip().split("\n")
    return ChatConfig(starter_questions=starter_questions)
