from matching_service_emulator.main import app
import uvicorn

uvicorn.run(app, host="0.0.0.0", port=6000)