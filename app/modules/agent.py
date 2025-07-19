from typing import Awaitable, Callable, Optional
from pydantic import BaseModel
import websockets
import logging
import asyncio

logger = logging.getLogger(__name__)

AgentResponseListener = Callable[[str], Awaitable[None]]

class AgentInputMessage(BaseModel):
    content: str
    connector: Optional[str] = None

class AgentOutputMessage(BaseModel):
    content: str

class AgentSession:
    def __init__(self, user_id: str, ws: websockets.ClientConnection):
        self.user_id = user_id
        self.status = None
        self.__ws = ws
        self.agent_response_listener: Optional[AgentResponseListener] = None
        self._listener_task: Optional[asyncio.Task] = None

    async def set_agent_response_listener(self, listener: AgentResponseListener):
        self.agent_response_listener = listener

    async def send_message(self, message: str):
        input_message = AgentInputMessage(content=message, connector=None)
        await self.__ws.send(input_message.model_dump_json())

    async def on_agent_response(self, message: str):
        if self.agent_response_listener:
            await self.agent_response_listener(message)
        else:
            logger.warning(f"Sem listener definido para resposta do agente: {message}")

    async def start_receiving(self, on_close: Callable[[], Awaitable[None]]):
        try:
            async for message in self.__ws:
                await self.on_agent_response(str(message))
        except websockets.ConnectionClosed:
            logger.info(f"Conexão com agente fechada para {self.user_id}")
        except Exception as e:
            logger.exception(f"Erro ao receber mensagem para {self.user_id}: {e}")
        finally:
            await on_close()

    async def close_session(self):
        await self.__ws.close()

class AgentSessionManager:
    def __init__(self):
        self.__sessions: dict[str, AgentSession] = {}

    async def create_session(self, session_id: str, url: str):
        if session_id in self.__sessions:
            return  # Já existe

        ws = await websockets.connect(url)
        logger.info(f"Created agent session for user {session_id}")
        session = AgentSession(session_id, ws)
        self.__sessions[session_id] = session

        asyncio.create_task(self._listen_to_agent(session_id, ws))

    async def _listen_to_agent(self, session_id: str, ws):
        try:
            async for message in ws:
                session = self.__sessions.get(session_id)
                if session:
                    agent_output_message = AgentOutputMessage.model_validate_json(message)
                    await session.on_agent_response(agent_output_message.content)

        except Exception as e:
            logger.error(f"Error on session {session_id}: {e}")
        finally:
            await self.delete_session(session_id)

    async def get_session(self, session_id: str) -> Optional[AgentSession]:
        return self.__sessions.get(session_id)

    async def delete_session(self, session_id: str) -> None:
        session = self.__sessions.pop(session_id, None)
        if session:
            await session.close_session()
