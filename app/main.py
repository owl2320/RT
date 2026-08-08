from fastapi import FastAPI,status
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request
from fastapi.responses import JSONResponse
import logging

# from app.core.config import settings
from app.core.logging import start_logging
from app.api.chat import router as chat_router
from app.api.auth import router as auth_router
from fastapi.middleware.cors import CORSMiddleware


start_logging()
logger = logging.getLogger(__name__)

app = FastAPI(title="RT AI")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5500"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.include_router(chat_router)
app.include_router(auth_router)

app.mount(
    "/static",
    StaticFiles(directory="app/static"),
    name="static"
)
templates = Jinja2Templates(
    directory="app/templates"
)

@app.exception_handler(Exception)
async def global_exception_handler(request:Request,e:Exception):
    logger.error("Unhandled error on %s %s: %s.",request.method,request.url,e,exc_info=True)

    return JSONResponse(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                        content={"detail":"Internal Server Error"})


@app.get("/health")
def health():
    return {
        "status":"running"
    }

@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        name="index.html",
        request=request
    )

@app.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        name="login.html",
        request=request
    )


@app.get("/signup")
def signup_page(request: Request):
    return templates.TemplateResponse(
        name="signup.html",
        request=request
    )