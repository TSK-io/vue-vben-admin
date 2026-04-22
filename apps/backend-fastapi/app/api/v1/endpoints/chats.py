import time
from typing import Annotated

from fastapi import APIRouter, Depends, Query, Request, WebSocket, WebSocketException, status

from app.core.deps import get_current_user, get_current_user_from_token
from app.schemas.chat import (
    ChatSendMessageRequest,
    CallSignalEventRequest,
    CreateChatBlacklistRequest,
    CreateChatReportRequest,
    CreateCallSessionRequest,
    CreateConversationRequest,
    EndCallSessionRequest,
    MarkMessageReadRequest,
    UpdateChatMuteRequest,
)
from app.schemas.common import ApiResponse, MetaPayload
from app.schemas.user import UserProfile
from app.services.chat import (
    create_blacklist_record,
    create_call_session,
    create_or_get_conversation,
    create_report_record,
    end_call_session,
    get_call_session_detail,
    get_conversation_detail,
    get_unread_summary,
    handle_call_signal,
    list_call_history,
    list_relationships,
    list_conversations,
    list_online_states,
    list_recommended_contacts,
    manager,
    mark_messages_read,
    rate_limiter,
    remove_blacklist_record,
    search_chat_users,
    send_message,
    update_conversation_mute,
    websocket_loop,
)

router = APIRouter(prefix="/chats")


def response_meta(request: Request) -> MetaPayload:
    return MetaPayload(
        request_id=getattr(request.state, "request_id", None),
        timestamp=int(time.time() * 1000),
    )


@router.get("/users/search", response_model=ApiResponse)
async def search_users(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    keyword: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=50),
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in search_chat_users(user, keyword, limit)],
        meta=response_meta(request),
    )


@router.get("/users/recommendations", response_model=ApiResponse)
async def get_recommendations(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    limit: int = Query(default=10, ge=1, le=20),
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_recommended_contacts(user, limit)],
        meta=response_meta(request),
    )


@router.post("/conversations", response_model=ApiResponse)
async def create_conversation(
    payload: CreateConversationRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=create_or_get_conversation(user, payload).model_dump(), meta=response_meta(request))


@router.get("/conversations", response_model=ApiResponse)
async def get_conversations(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=[item.model_dump() for item in list_conversations(user)], meta=response_meta(request))


@router.get("/conversations/{conversation_id}", response_model=ApiResponse)
async def get_conversation(
    conversation_id: str,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    page: int = Query(default=1, ge=1),
    page_size: int = Query(default=20, ge=1, le=100),
) -> ApiResponse:
    return ApiResponse(
        data=get_conversation_detail(user, conversation_id, page, page_size).model_dump(),
        meta=response_meta(request),
    )


@router.post("/conversations/{conversation_id}/messages", response_model=ApiResponse)
async def post_message(
    conversation_id: str,
    payload: ChatSendMessageRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    rate_limiter.check(user.user_id)
    data = send_message(user, conversation_id, payload)
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "message",
            "data": data.model_dump(),
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.post("/conversations/{conversation_id}/mute", response_model=ApiResponse)
async def mute_conversation(
    conversation_id: str,
    payload: UpdateChatMuteRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = update_conversation_mute(user, conversation_id, payload)
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.post("/conversations/{conversation_id}/read", response_model=ApiResponse)
async def post_read(
    conversation_id: str,
    payload: MarkMessageReadRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = mark_messages_read(user, conversation_id, payload)
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": "read",
            "data": {
                "conversation_id": conversation_id,
                "user_id": user.user_id,
                "last_read_message_id": payload.last_read_message_id,
                **data.model_dump(),
            },
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.post("/calls", response_model=ApiResponse)
async def post_call(
    payload: CreateCallSessionRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = create_call_session(user, payload)
    await manager.broadcast_to_conversation(
        payload.conversation_id,
        {
            "event": "call.invite",
            "data": data.model_dump(),
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/calls/{call_session_id}", response_model=ApiResponse)
async def get_call(
    call_session_id: str,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=get_call_session_detail(user, call_session_id).model_dump(), meta=response_meta(request))


@router.get("/calls", response_model=ApiResponse)
async def get_calls(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    conversation_id: str | None = Query(default=None),
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_call_history(user, conversation_id)],
        meta=response_meta(request),
    )


@router.post("/calls/{call_session_id}/end", response_model=ApiResponse)
async def post_end_call(
    call_session_id: str,
    payload: EndCallSessionRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data = end_call_session(user, call_session_id, payload)
    await manager.broadcast_to_conversation(
        data.conversation_id,
        {
            "event": "call.end",
            "data": data.model_dump(),
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.post("/calls/signal", response_model=ApiResponse)
async def post_call_signal(
    payload: CallSignalEventRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    data, conversation_id = handle_call_signal(user, payload)
    await manager.broadcast_to_conversation(
        conversation_id,
        {
            "event": payload.event,
            "data": data.model_dump(),
        },
    )
    return ApiResponse(data=data.model_dump(), meta=response_meta(request))


@router.get("/unread-summary", response_model=ApiResponse)
async def unread_summary(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=get_unread_summary(user).model_dump(), meta=response_meta(request))


@router.get("/online-states", response_model=ApiResponse)
async def online_states(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
    user_ids: list[str] = Query(default_factory=list),
) -> ApiResponse:
    return ApiResponse(
        data=[item.model_dump() for item in list_online_states(user, user_ids or None)],
        meta=response_meta(request),
    )


@router.get("/relationships", response_model=ApiResponse)
async def get_relationships(
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=[item.model_dump() for item in list_relationships(user)], meta=response_meta(request))


@router.post("/blacklist", response_model=ApiResponse)
async def add_blacklist(
    payload: CreateChatBlacklistRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=create_blacklist_record(user, payload).model_dump(), meta=response_meta(request))


@router.delete("/blacklist/{target_user_id}", response_model=ApiResponse)
async def remove_blacklist(
    target_user_id: str,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=remove_blacklist_record(user, target_user_id).model_dump(), meta=response_meta(request))


@router.post("/report", response_model=ApiResponse)
async def create_report(
    payload: CreateChatReportRequest,
    request: Request,
    user: Annotated[UserProfile, Depends(get_current_user)],
) -> ApiResponse:
    return ApiResponse(data=create_report_record(user, payload).model_dump(), meta=response_meta(request))


@router.websocket("/ws")
async def chat_websocket(websocket: WebSocket, token: str) -> None:
    try:
        user = get_current_user_from_token(token)
    except Exception as exc:  # pragma: no cover
        raise WebSocketException(code=status.WS_1008_POLICY_VIOLATION) from exc
    await websocket_loop(user, websocket)
