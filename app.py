from dotenv import load_dotenv
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from fastapi_server.ai import router as ai_router
from fastapi import FastAPI
import os
import time
import bcrypt
load_dotenv()
'''def load_custom_openapi(): 
    with open("backend/openapi(1).json", "r") as file:
        return json.load(file)'''

app = FastAPI(docs_url="/api/docs",openapi_url="/api/openapi.json")
'''app.openapi_schema = app.openapi()
app.openapi_schema["security"] = [{"OAuth2PasswordBearer": []}]'''

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Разрешить все источники
    allow_credentials=True,
    allow_methods=["*"],    
    allow_headers=["*"],
)
app.include_router(ai_router, prefix="/api/ai", tags=["AI"])


if __name__ == "__main__":
    host, port = os.getenv("FAST_API_HOST"), os.getenv("FAST_API_PORT")
    uvicorn.run(app, host=host, port=int(port))
    