from fastapi.responses import JSONResponse
from slowapi.middleware import SlowAPIMiddleware

from modules.server.controllers.send import send_route
from modules.server.rate_limiter import limiter
from modules.server.security import get_api_key

import logging

logger = logging.getLogger(__name__)

from fastapi import FastAPI, Depends, Request

asgi = FastAPI(
    title="Chatbot Service API",
    description="API para interagir com o chatbot via HTTP e WebSocket.",
    version="1.0.0"
)

asgi.state.limiter = limiter
asgi.add_middleware(SlowAPIMiddleware)
asgi.include_router(send_route)


@asgi.get("/auth", tags=["Authentication"])
async def auth_test(key_info: dict = Depends(get_api_key)):
    """
    Endpoint de teste para verificar a autenticação com a chave de API.
    A chave deve ser enviada no header `X-API-Key`.
    """
    return {"message": "Você está autenticado!", "key_info": key_info}

@asgi.get("/version", tags=["Monitoring"])
async def version_check(request: Request):
    """Verifica a versão do serviço."""
    return {"version": "1.0.0"}

@asgi.get("/health", tags=["Monitoring"])
@limiter.limit("10/minute")
async def health_check(request: Request):
    """Verifica a saúde do serviço."""
    return {"status": "ok"}

@asgi.exception_handler(429)
async def rate_limit_exceeded(request: Request, exc):
    """Handler para quando o limite de requisições é excedido."""
    return JSONResponse(
        status_code=429,
        content={"detail": "Rate limit exceeded. Try again later."},
    )
