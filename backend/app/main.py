from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.config import settings
from app.database import init_db
from app.api import auth, documents, chat, events, templates, media

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Hệ thống phân tích và tóm tắt văn bản pháp lý - Multimodal RAG + LLM",
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS.split(","),
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router)
app.include_router(documents.router)
app.include_router(chat.router)
app.include_router(events.router)
app.include_router(templates.router)
app.include_router(media.router)


@app.on_event("startup")
def on_startup():
    init_db()
    try:
        from app.seed import seed
        seed()
    except Exception as e:
        print(f"[!] Seed warning: {e}")

    # Preload embedding model in background so first chat request doesn't time out
    import threading
    def _preload_embeddings():
        try:
            from app.ai.embeddings import _get_model
            print("[*] Loading BGE-M3 embedding model...")
            _get_model()
            print("[✓] BGE-M3 model ready.")
        except Exception as e:
            print(f"[!] Embedding model preload failed: {e}")
    threading.Thread(target=_preload_embeddings, daemon=True).start()


@app.get("/")
def root():
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "docs": "/docs",
    }


@app.get("/health")
def health():
    return {"status": "ok"}
