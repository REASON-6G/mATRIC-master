from fastapi import APIRouter

from app.api.routes import (
    items, login, users, utils, token, users_new, agent, third_party_apps, agent_update, 
    agent_details_router, agent_data_router, send_command_router, emulator
)

api_router = APIRouter()
api_router.include_router(login.router, tags=["login"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(utils.router, prefix="/utils", tags=["utils"])
api_router.include_router(items.router, prefix="/items", tags=["items"])
# Include the routers from the routes folder
api_router.include_router(token.router, prefix="/token", tags=["token"])
api_router.include_router(users_new.router, prefix="/users_ne", tags=["users"])
api_router.include_router(agent.router, prefix="/agents", tags=["agents"])
api_router.include_router(third_party_apps.router, prefix="/third_party_apps", tags=["third_party_apps"])
api_router.include_router(agent_update.router, prefix="/agent_update", tags=["agent_update"])
api_router.include_router(agent_details_router, prefix="/agent_details", tags=["agent_details"])
api_router.include_router(agent_data_router, prefix="/agent_data", tags=["agent_data"])
api_router.include_router(send_command_router, prefix="/send_command", tags=["send_command"])
api_router.include_router(emulator.router, prefix="/emulator", tags=["emulator"])
# Include the callback routers
api_router.include_router(agent_data_callback_router, prefix="/callback/agent_data", tags=["agent_data_callback"])
api_router.include_router(agent_details_callback_router, prefix="/callback/agent_details", tags=["agent_details_callback"])
api_router.include_router(agent_details_callback_router, prefix="/callback/emulator", tags=["emulator_callback"])

