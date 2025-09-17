from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, agent, third_party_apps, token, agent_update
from app.routes.agent_details import router as agent_details_router  # Route for agent details
from app.routes.agent_data import router as agent_data_router  # Route for agent data
from app.routes.send_command import router as send_command_router  # Route for sending commands
from app.routes.agent_data_callback import router as agent_data_callback_router  # Agent data callback route
from app.routes.agent_details_callback import router as agent_details_callback_router  # Agent details callback route
from app.routes import emulator
from app.config import settings
from fastapi.openapi.utils import get_openapi
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm


app = FastAPI()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="mATRIC API",
        version="1.0.0",
        description="Handles mATRIC calls",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT"
        }
    }
    openapi_schema["security"] = [{"BearerAuth": []}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

# Set CORS enabled origins if specified in settings
# if settings.backend_cors_origins:
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include the routers from the routes folder
app.include_router(token.router, prefix="/api/v1/token", tags=["token"])
app.include_router(users.router, prefix="/api/v1/users", tags=["users"])
app.include_router(agent.router, prefix="/api/v1/agents", tags=["agents"])
app.include_router(third_party_apps.router, prefix="/api/v1/third_party_apps", tags=["third_party_apps"])
app.include_router(agent_update.router, prefix="/api/v1/agent_update", tags=["agent_update"])
app.include_router(agent_details_router, prefix="/api/v1/agent_details", tags=["agent_details"])
app.include_router(agent_data_router, prefix="/api/v1/agent_data", tags=["agent_data"])
app.include_router(send_command_router, prefix="/api/v1/send_command", tags=["send_command"])
app.include_router(emulator.router, prefix="/api/v1/emulator", tags=["emulator"])
# Include the callback routers
app.include_router(agent_data_callback_router, prefix="/api/v1/callback/agent_data", tags=["agent_data_callback"])
app.include_router(agent_details_callback_router, prefix="/api/v1/callback/agent_details", tags=["agent_details_callback"])
app.include_router(agent_details_callback_router, prefix="/api/v1/callback/emulator", tags=["emulator_callback"])
