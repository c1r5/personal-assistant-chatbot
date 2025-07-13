from fastapi import FastAPI, Request, WebSocket, Depends
from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

from modules.bot import telegram_chat
from modules.bot.telegram.models.chat_message import BotMessage, UserMessage
from modules.server.controllers.send import send_route
from modules.server.rate_limiter import limiter

from modules.server.security import get_api_key

import logging

logger = logging.getLogger(__name__)

app_instance = FastAPI(
    title="Chatbot Service API",
    description="API para interagir com o chatbot via HTTP e WebSocket.",
    version="1.0.0"
)

app_instance.state.limiter = limiter
app_instance.add_middleware(SlowAPIMiddleware)
app_instance.include_router(send_route)


@app_instance.get("/auth", tags=["Authentication"])
async def auth_test(key_info: dict = Depends(get_api_key)):
    """
    Endpoint de teste para verificar a autenticação com a chave de API.
    A chave deve ser enviada no header `X-API-Key`.
    """
    return {"message": "Você está autenticado!", "key_info": key_info}

@app_instance.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket, key_info: dict = Depends(get_api_key)):
    """
    Endpoint de WebSocket para comunicação em tempo real.

    A autenticação é feita através da dependência `get_api_key`, que espera
    o header `X-API-Key`. Se a chave for inválida, a conexão será rejeitada
    com um status HTTP 403.
    """
    await websocket.accept()
    websocket.state.key_info = key_info

    async def on_message_listener(message: UserMessage):
        try:
            await websocket.send_text(message.model_dump_json())
        except Exception as e:
            logger.error(f"Error sending message to client: {e}")

    telegram_chat.add_on_message_listener(on_message_listener)

    try:
        while True:
            data = await websocket.receive_text()
            if data == "close":
                break
            try:
                bot_message = BotMessage.model_validate_json(data)
                await telegram_chat.send_message(bot_message)
            except Exception as e:
                print(f"Error processing message from client: {e}")
                await websocket.send_text(f'{{"error": "Error processing message: {str(e)}"}}')
    except Exception as e:
        # Captura exceções de desconexão do cliente, etc.
        print(f"WebSocket connection closed unexpectedly: {e}")
    finally:
        logger.info("Client disconnected, cleaning up listener.")
        telegram_chat.remove_on_message_listener(on_message_listener)
        pass

@app_instance.get("/version", tags=["Monitoring"])
async def version_check(request: Request):
    """Verifica a versão do serviço."""
    return {"version": "1.0.0"}

@app_instance.get("/health", tags=["Monitoring"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Verifica a saúde do serviço."""
    return {"status": "ok"}

@app_instance.exception_handler(429)
async def rate_limit_exceeded(request: Request, exc):
    """Handler para quando o limite de requisições é excedido."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )
