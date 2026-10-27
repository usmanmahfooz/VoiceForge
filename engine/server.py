"""
VoiceForge FastAPI server.
Runs the local web interface and provides speech generation, voice, and history routes.
"""
import asyncio
import json
import logging
import os
import time
import uuid
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
LOG_DIR = BASE_DIR / "logs"
LOG_DIR.mkdir(parents=True, exist_ok=True)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.FileHandler(LOG_DIR / "engine.log", encoding="utf-8")],
)
logger = logging.getLogger("voiceforge")
import sys
sys.path.insert(0, str(Path(__file__).parent))

from fastapi import FastAPI, UploadFile, File, Form, HTTPException, Request
from fastapi.responses import FileResponse, Response, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

from voice_registry import VoiceRegistry
from tts_engine import TTSEngine

STATIC_DIR = BASE_DIR / "static"
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = DATA_DIR / "output"
CLONED_DIR = DATA_DIR / "cloned"
CONFIG_FILE = DATA_DIR / "config.json"
BGM_DIR = DATA_DIR / "bgm"
for directory in (OUTPUT_DIR, CLONED_DIR, BGM_DIR):
    directory.mkdir(parents=True, exist_ok=True)

app = FastAPI(title="VoiceForge", version="1.0.0", docs_url="/api/docs", redoc_url=None)
registry = VoiceRegistry()
engine = TTSEngine()

# The intended default is a local-only app. If exposed publicly, configure a specific
# trusted origin list, authentication, and rate limiting before deployment.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://127.0.0.1:7860", "http://localhost:7860"],
    allow_methods=["GET", "POST", "DELETE"],
    allow_headers=["Content-Type"],
)
app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")


@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = STATIC_DIR / "index.html"
    if index_path.exists():
        return HTMLResponse(content=index_path.read_text(encoding="utf-8"))
    return HTMLResponse(content="<h1>VoiceForge - index.html not found</h1>", status_code=404)


@app.get("/api/health")
async def health_check():
    status = engine.get_status()
    return {
        "status": "healthy",
        "server": "running",
        "model_loaded": status["model_loaded"],
        "total_voices": len(registry.get_all_voices()),
        "version": "1.0.0",
    }


@app.get("/api/setup-status")
async def setup_status():
    status = engine.get_status()
    return {
        "progress": status["setup_progress"],
        "status": status["setup_status"],
        "model_loaded": status["model_loaded"],
        "loading": status["loading"],
        "voice_cloning": status.get("voice_cloning", False),
    }


@app.get("/api/clone-status")
async def clone_status():
    status = engine.get_status()
    available = status.get("voice_cloning", False)
    return {"available": available, "message": "Voice cloning is available" if available else "Voice cloning requires an authorized Pocket TTS setup."}


class TokenRequest(BaseModel):
    token: str


@app.post("/api/set-token")
async def set_token(req: TokenRequest):
    token = req.token.strip()
    if not token.startswith("hf_"):
        raise HTTPException(status_code=400, detail="Invalid token format.")
    os.environ["HF_TOKEN"] = token
    try:
        from huggingface_hub import login
        login(token=token, add_to_git_credential=False)
        engine.model_loaded = False
        await engine.load_model()
        if not engine.get_status().get("voice_cloning", False):
            raise ValueError("Token was accepted but voice cloning remains unavailable. Check the model access requirements.")
        return {"success": True, "message": "Authentication successful."}
    except Exception as exc:
        logger.exception("Hugging Face authentication failed")
        raise HTTPException(status_code=400, detail=str(exc))


@app.post("/api/reset-token")
async def reset_token():
    os.environ.pop("HF_TOKEN", None)
    try:
        from huggingface_hub import logout
        logout()
    except Exception:
        logger.info("Hugging Face logout was not available")
    engine.voice_cloning_available = False
    engine.model_loaded = False
    return {"success": True, "message": "Authentication reset."}


@app.post("/api/setup-start")
async def start_setup():
    if not engine.model_loaded and not engine.loading:
        asyncio.create_task(engine.load_model())
    return {"message": "Setup started"}


@app.get("/api/verify")
async def check_verification():
    return {"verified": registry.is_verified()}


@app.post("/api/verify")
async def set_verification():
    registry.set_verified(True)
    return {"verified": True, "message": "Welcome to VoiceForge!"}


@app.get("/api/voices")
async def list_voices(gender: str = None, language: str = None, search: str = None):
    voices = registry.get_all_voices(gender=gender, language=language, search=search)
    return {"total": len(voices), "voices": voices}


@app.get("/api/voices/{voice_id}")
async def get_voice(voice_id: str):
    voice = registry.get_voice(voice_id)
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice


@app.get("/api/languages")
async def list_languages():
    return {"languages": registry.get_languages()}


@app.post("/api/generate")
async def generate_speech(request: Request):
    body = await request.json()
    text = str(body.get("text", "")).strip()
    voice_id = str(body.get("voice_id", "alba"))
    speed = float(body.get("speed", 1.0))
    language = str(body.get("language", "en"))
    pitch = float(body.get("pitch", 1.0))
    reverb = float(body.get("reverb", 0.0))
    bgm_file = body.get("bgm_file")
    output_format = str(body.get("output_format", "wav")).lower()
    if not text:
        raise HTTPException(status_code=400, detail="Text is required")
    if len(text) > 5000:
        raise HTTPException(status_code=400, detail="Text too long (max 5000 characters)")
    if output_format not in {"wav", "mp3"}:
        raise HTTPException(status_code=400, detail="Output format must be wav or mp3")
    bgm_path = None
    if bgm_file:
        safe_name = Path(str(bgm_file)).name
        candidate = (BGM_DIR / safe_name).resolve()
        if candidate.parent == BGM_DIR.resolve() and candidate.is_file():
            bgm_path = str(candidate)
    try:
        audio_bytes, duration = await engine.generate(text, voice_id, speed, language, pitch, reverb, bgm_path, output_format)
        file_id = f"voiceforge_{int(time.time())}_{uuid.uuid4().hex[:6]}"
        (OUTPUT_DIR / f"{file_id}.{output_format}").write_bytes(audio_bytes)
        meta = {
            "id": file_id, "text": text[:100], "voice_id": voice_id, "duration": round(duration, 2),
            "speed": speed, "pitch": pitch, "reverb": reverb, "language": language,
            "format": output_format, "timestamp": int(time.time()),
        }
        (OUTPUT_DIR / f"{file_id}.json").write_text(json.dumps(meta), encoding="utf-8")
        media_type = "audio/mpeg" if output_format == "mp3" else "audio/wav"
        return Response(content=audio_bytes, media_type=media_type, headers={
            "X-Duration": str(round(duration, 2)),
            "X-File-Id": file_id,
            "Content-Disposition": f'attachment; filename="{file_id}.{output_format}"',
        })
    except RuntimeError as exc:
        logger.exception("Speech generation failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.get("/api/preview/{voice_id}")
async def preview_voice(voice_id: str):
    safe_id = Path(voice_id).name
    preview_path = DATA_DIR / "voices" / f"{safe_id}_preview.wav"
    if preview_path.is_file():
        return FileResponse(str(preview_path), media_type="audio/wav")
    try:
        wav_bytes = await engine.generate_preview(safe_id)
        if not wav_bytes:
            raise HTTPException(status_code=500, detail="Preview generation failed")
        preview_path.parent.mkdir(parents=True, exist_ok=True)
        preview_path.write_bytes(wav_bytes)
        return Response(content=wav_bytes, media_type="audio/wav")
    except HTTPException:
        raise
    except Exception as exc:
        logger.exception("Voice preview failed")
        raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/clone")
async def clone_voice(audio: UploadFile = File(...), name: str = Form(...), language: str = Form("en")):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    ext = Path(audio.filename).suffix.lower()
    if ext not in {".wav", ".mp3", ".ogg", ".flac", ".m4a", ".webm"}:
        raise HTTPException(status_code=400, detail=f"Unsupported audio format: {ext}")
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio is empty")
    if len(audio_bytes) > 50 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 50MB)")
    voice_id = f"cloned_{uuid.uuid4().hex[:8]}"
    try:
        state_path = await engine.clone_voice(audio_bytes, voice_id, audio.filename)
        voice = registry.add_cloned_voice(voice_id, name.strip(), str(state_path), language)
        return {"success": True, "voice": voice, "message": "Voice created successfully."}
    except RuntimeError as exc:
        logger.exception("Voice cloning failed")
        raise HTTPException(status_code=500, detail=str(exc))
    finally:
        await audio.close()


@app.get("/api/cloned-voices")
async def list_cloned_voices():
    return {"voices": [v for v in registry.get_all_voices() if v.get("is_cloned")]}


@app.delete("/api/cloned-voices/{voice_id}")
async def delete_cloned_voice(voice_id: str):
    if registry.remove_cloned_voice(voice_id):
        return {"success": True, "message": "Voice removed"}
    raise HTTPException(status_code=404, detail="Voice not found")


@app.get("/api/history")
async def generation_history():
    history = []
    if OUTPUT_DIR.exists():
        for meta_file in sorted(OUTPUT_DIR.glob("*.json"), reverse=True)[:50]:
            try:
                meta = json.loads(meta_file.read_text(encoding="utf-8"))
                file_id = Path(str(meta.get("id", ""))).name
                meta["has_audio"] = any((OUTPUT_DIR / f"{file_id}{ext}").is_file() for ext in (".wav", ".mp3"))
                meta["audio_url"] = f"/api/history/{file_id}/audio"
                history.append(meta)
            except (OSError, json.JSONDecodeError):
                logger.warning("Skipping invalid history metadata file %s", meta_file.name)
    return {"history": history}


@app.get("/api/history/{file_id}/audio")
async def get_history_audio(file_id: str):
    safe_id = Path(file_id).name
    for ext in (".wav", ".mp3"):
        audio_path = OUTPUT_DIR / f"{safe_id}{ext}"
        if audio_path.is_file():
            media_type = "audio/mpeg" if ext == ".mp3" else "audio/wav"
            return FileResponse(str(audio_path), media_type=media_type)
    raise HTTPException(status_code=404, detail="Audio not found")


@app.get("/api/history/download-all")
async def download_all_history():
    import io
    import zipfile
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for path in OUTPUT_DIR.iterdir():
            if path.is_file() and path.suffix.lower() in {".wav", ".mp3", ".json"}:
                archive.write(path, path.name)
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="VoiceForge_History.zip"'})


@app.get("/api/bgm")
async def list_bgm():
    files = sorted(p.name for p in BGM_DIR.iterdir() if p.is_file() and p.suffix.lower() in {".wav", ".mp3", ".ogg"})
    return {"bgm_files": files}


@app.post("/api/bgm/upload")
async def upload_bgm(audio: UploadFile = File(...)):
    if not audio.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")
    filename = Path(audio.filename).name.replace(" ", "_")
    if Path(filename).suffix.lower() not in {".wav", ".mp3", ".ogg"}:
        raise HTTPException(status_code=400, detail="Background music must be WAV, MP3, or OGG.")
    audio_bytes = await audio.read()
    if not audio_bytes:
        raise HTTPException(status_code=400, detail="Uploaded audio is empty")
    if len(audio_bytes) > 20 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File too large (max 20MB)")
    target = BGM_DIR / filename
    target.write_bytes(audio_bytes)
    return {"success": True, "filename": filename}


@app.post("/api/batch")
async def generate_batch(request: Request):
    body = await request.json()
    texts = body.get("texts", [])
    if not isinstance(texts, list) or not texts:
        raise HTTPException(status_code=400, detail="Texts array is required")
    if len(texts) > 100:
        raise HTTPException(status_code=400, detail="Maximum 100 lines per batch")
    voice_id = str(body.get("voice_id", "alba"))
    speed = float(body.get("speed", 1.0))
    language = str(body.get("language", "en"))
    pitch = float(body.get("pitch", 1.0))
    reverb = float(body.get("reverb", 0.0))
    output_format = str(body.get("output_format", "wav")).lower()
    if output_format not in {"wav", "mp3"}:
        raise HTTPException(status_code=400, detail="Output format must be wav or mp3")
    bgm_file = body.get("bgm_file")
    bgm_path = None
    if bgm_file:
        safe_name = Path(str(bgm_file)).name
        candidate = (BGM_DIR / safe_name).resolve()
        if candidate.parent == BGM_DIR.resolve() and candidate.is_file():
            bgm_path = str(candidate)
    import io
    import zipfile
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED) as archive:
        for index, raw_text in enumerate(texts):
            text = str(raw_text).strip()
            if not text:
                continue
            if len(text) > 5000:
                raise HTTPException(status_code=400, detail=f"Batch item {index + 1} exceeds 5000 characters")
            try:
                audio_bytes, _ = await engine.generate(text, voice_id, speed, language, pitch, reverb, bgm_path, output_format)
                slug = "".join(c for c in text[:30] if c.isalnum() or c in " _-").strip() or f"line-{index+1}"
                archive.writestr(f"{index+1:03d}_{slug}.{output_format}", audio_bytes)
            except Exception:
                logger.exception("Batch item %d failed", index + 1)
                raise HTTPException(status_code=500, detail=f"Failed to generate batch item {index + 1}")
    buffer.seek(0)
    return Response(content=buffer.getvalue(), media_type="application/zip",
                    headers={"Content-Disposition": 'attachment; filename="VoiceForge_Batch.zip"'})


if __name__ == "__main__":
    import uvicorn
    logger.info("Starting VoiceForge on http://127.0.0.1:7860")
    print("VoiceForge: http://127.0.0.1:7860")
    uvicorn.run(app, host="127.0.0.1", port=7860, log_level="warning", access_log=False)
