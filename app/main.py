import logging
import asyncio
import signal
from typing import Optional

from pathlib import Path
from uvicorn import Config, Server

from modules.agent import AgentSessionManager
from modules.message_dispatcher import MessageDispatcher
from modules.constants import TELEGRAM_BOT_TOKEN, SERVICE_API_PORT, AGENT_API_URL

from modules.chatbots.telegram import TelegramChatbotConnector
from modules.server import asgi


logger = logging.getLogger(__name__)
dispatcher = MessageDispatcher()
agent_session_manager = AgentSessionManager()

async def on_chatbot_message(message: Optional[str], chat_id: str) -> None:
    if not message:
        return

    # Garante que a sessão existe
    await agent_session_manager.create_session(chat_id, AGENT_API_URL)

    session = await agent_session_manager.get_session(chat_id)
    if not session:
        logger.error(f"No agent session found for {chat_id}")
        return

    async def agent_response_handler(response: str):
        logger.info(f"Agent response: {response}")
        await dispatcher.dispatch_message(response, chat_id)

    await session.set_agent_response_listener(agent_response_handler)
    await session.send_message(message)
# Function to run FastAPI server
async def run_fastapi():
    config = Config(app=asgi, host="0.0.0.0",
                    port=int(SERVICE_API_PORT), loop="asyncio")
    server = Server(config)
    await server.serve()

async def main():
    loop = asyncio.get_running_loop()
    stop_event = asyncio.Event()

    dispatcher.add_connector('telegram.connector', TelegramChatbotConnector(TELEGRAM_BOT_TOKEN, on_chatbot_message))

    def shutdown():
        print("Shutdown signal received.")
        stop_event.set()

    for sig in (signal.SIGINT, signal.SIGTERM):
        loop.add_signal_handler(sig, shutdown)

    tasks = []

    fastapi_task = asyncio.create_task(run_fastapi())
    bot_tasks = dispatcher.start_listening()

    tasks.extend(bot_tasks)

    await stop_event.wait()

    print("Cancelando tarefas...")

    for task in bot_tasks:
        task.cancel()

    try:
        await asyncio.gather(*tasks, fastapi_task)
    except asyncio.CancelledError:
        print("Tarefas canceladas com sucesso.")


if __name__ == "__main__":
    try:

        logs_path = Path(__file__).parent / "logs"
        logs_path.mkdir(parents=True, exist_ok=True)
        logs_path = logs_path / "app.log"
        logs_path.touch()

        logging.basicConfig(
            level=logging.INFO,
            format="(%(asctime)s) %(levelname)s %(message)s",
            datefmt="%m/%d/%y - %H:%M:%S %Z",
            # filename=logs_path
        )


        asyncio.run(main())
    except KeyboardInterrupt:
        print("Encerrado pelo usuário.")
