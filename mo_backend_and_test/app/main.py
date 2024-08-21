from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routes import users, agent, third_party_apps, token, agent_update
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
if settings.backend_cors_origins:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[settings.backend_cors_origin],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include the routers from the routes folder
app.include_router(token.router, prefix="/token", tags=["token"])
app.include_router(users.router, prefix="/users", tags=["users"])
app.include_router(agent.router, prefix="/agents", tags=["agents"])
app.include_router(third_party_apps.router, prefix="/third_party_apps", tags=["third_party_apps"])
app.include_router(agent_update.router, prefix="/agent_update", tags=["agent_update"])
