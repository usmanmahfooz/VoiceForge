"""
VoiceForge TTS Engine
Wraps Kyutai Pocket TTS for text-to-speech generation and voice cloning.
"""
import logging
import os
import time
from pathlib import Path
import numpy as np

logger = logging.getLogger("voiceforge.engine")
DATA_DIR = Path(__file__).parent.parent / "data"
CLONED_DIR = DATA_DIR / "cloned"
OUTPUT_DIR = DATA_DIR / "output"
VOICES_DIR = DATA_DIR / "voices"

POCKET_TTS_VOICES = [
    "cosette", "marius", "javert", "alba", "jean", "anna", "vera",
    "fantine", "charles", "paul", "eponine", "azelma", "george", "mary",
    "jane", "michael", "eve", "bill_boerst", "peter_yearsley",
    "stuart_bell", "caro_davy", "giovanni", "lola", "juergen", "rafael", "estelle",
]


class TTSEngine:
    """Pocket TTS engine with voice cloning support."""
    def __init__(self):
        self.model = None
        self.model_loaded = False
        self.loading = False
        self.setup_progress = 0
        self.setup_status = "idle"
        self.voice_cloning_available = False
        self._voice_states = {}

    def get_status(self) -> dict:
        return {
            "model_loaded": self.model_loaded,
            "loading": self.loading,
            "setup_progress": self.setup_progress,
            "setup_status": self.setup_status,
            "voice_cloning": self.voice_cloning_available,
        }

    async def load_model(self):
        if self.model_loaded or self.loading:
            return
        self.loading = True
        self.setup_status = "Initializing Pocket TTS…"
        self.setup_progress = 10
        try:
            from pocket_tts import TTSModel
            self.setup_status = "Loading speech model…"
            self.setup_progress = 60
            self.model = TTSModel.load_model()
            self.setup_status = "Model ready"
            self.setup_progress = 100
            self.model_loaded = True
            self.voice_cloning_available = bool(getattr(self.model, "has_voice_cloning", False))
            logger.info("Pocket TTS loaded. Voice cloning available: %s", self.voice_cloning_available)
        except ImportError:
            self.setup_status = "Pocket TTS is not installed. Install requirements first."
            self.setup_progress = -1
            logger.exception("Pocket TTS import failed")
        except Exception as exc:
            self.setup_status = f"Error loading model: {exc}"
            self.setup_progress = -1
            logger.exception("Failed to load TTS model")
        finally:
            self.loading = False

    def _get_voice_state(self, voice_id: str):
        if voice_id in self._voice_states:
            return self._voice_states[voice_id]
        if voice_id in POCKET_TTS_VOICES:
            try:
                state = self.model.get_state_for_audio_prompt(voice_id)
                self._voice_states[voice_id] = state
                return state
            except Exception:
                logger.exception("Failed to load built-in voice %s", voice_id)
                return None
        if self.voice_cloning_available:
            state_path = CLONED_DIR / f"{voice_id}.safetensors"
            if state_path.exists():
                try:
                    from pocket_tts import import_model_state
                    state = import_model_state(str(state_path))
                    self._voice_states[voice_id] = state
                    return state
                except Exception:
                    logger.exception("Failed to load cloned voice state")
            audio_path = CLONED_DIR / f"{voice_id}_reference.wav"
            if audio_path.exists():
                try:
                    state = self.model.get_state_for_audio_prompt(str(audio_path))
                    self._voice_states[voice_id] = state
                    return state
                except Exception:
                    logger.exception("Failed to load voice from reference audio")
        logger.warning("Voice %s not found; falling back to alba", voice_id)
        if "alba" not in self._voice_states:
            try:
                self._voice_states["alba"] = self.model.get_state_for_audio_prompt("alba")
            except Exception:
                logger.exception("Failed to load fallback voice")
                return None
        return self._voice_states.get("alba")

    async def generate(self, text: str, voice_id: str = "alba", speed: float = 1.0,
                       language: str = "en", pitch: float = 1.0, reverb: float = 0.0,
                       bgm_path: str = None, output_format: str = "wav") -> tuple[bytes, float]:
        if output_format not in {"wav", "mp3"}:
            raise ValueError("output_format must be wav or mp3")
        if not self.model_loaded:
            await self.load_model()
        if not self.model_loaded:
            raise RuntimeError("TTS model failed to load")
        start_time = time.time()
        try:
            voice_state = self._get_voice_state(voice_id)
            audio = self.model.generate_audio(voice_state, text)
            if hasattr(audio, "detach"):
                audio = audio.detach().cpu().numpy()
            elif hasattr(audio, "numpy"):
                audio = audio.numpy()
            audio_np = np.asarray(audio).squeeze()
            if speed != 1.0 and speed > 0:
                n = len(audio_np)
                new_len = int(n / speed)
                if new_len > 0:
                    audio_np = np.interp(np.linspace(0, n - 1, new_len), np.arange(n), audio_np)
            sample_rate = int(getattr(self.model, "sample_rate", 24000))
            duration = len(audio_np) / sample_rate
            import soundfile as sf
            import subprocess
            import tempfile
            import uuid
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            temp_id = uuid.uuid4().hex[:8]
            temp_wav = OUTPUT_DIR / f"temp_{temp_id}.wav"
            out_file = OUTPUT_DIR / f"temp_out_{temp_id}.{output_format}"
            sf.write(str(temp_wav), audio_np, sample_rate, format="WAV", subtype="PCM_16")
            filters = []
            if pitch != 1.0:
                filters.append(f"rubberband=pitch={pitch}")
            if reverb > 0.0:
                decay = 0.2 + (reverb * 0.4)
                filters.append(f"aecho=0.8:0.9:60:{decay}")
            filter_str = ",".join(filters)
            cmd = ["ffmpeg", "-y", "-i", str(temp_wav)]
            if bgm_path and Path(bgm_path).is_file():
                cmd.extend(["-i", str(bgm_path)])
                if filter_str:
                    complex_filter = (f"[0:a]{filter_str}[voice];[1:a]volume=0.8[bg];"
                                      f"[bg][voice]sidechaincompress=threshold=0.03:ratio=4:attack=5:release=50[ducked];"
                                      f"[voice][ducked]amix=inputs=2:duration=first[out]")
                else:
                    complex_filter = ("[1:a]volume=0.8[bg];[bg][0:a]sidechaincompress=threshold=0.03:ratio=4:attack=5:release=50[ducked];"
                                      "[0:a][ducked]amix=inputs=2:duration=first[out]")
                cmd.extend(["-filter_complex", complex_filter, "-map", "[out]"])
            elif filter_str:
                cmd.extend(["-af", filter_str])
            if output_format == "mp3":
                cmd.extend(["-c:a", "libmp3lame", "-q:a", "2"])
            else:
                cmd.extend(["-c:a", "pcm_s16le"])
            cmd.append(str(out_file))
            try:
                subprocess.run(cmd, check=True, capture_output=True)
                result = out_file.read_bytes()
            except (FileNotFoundError, subprocess.CalledProcessError):
                logger.exception("FFmpeg processing failed; returning WAV audio")
                result = temp_wav.read_bytes()
            finally:
                temp_wav.unlink(missing_ok=True)
                out_file.unlink(missing_ok=True)
            logger.info("Generated %.1fs of audio in %.2fs for voice=%s", duration, time.time()-start_time, voice_id)
            return result, duration
        except Exception as exc:
            logger.exception("Speech generation failed")
            raise RuntimeError(f"Speech generation failed: {exc}") from exc

    async def clone_voice(self, audio_bytes: bytes, voice_id: str, filename: str = "upload.wav") -> str:
        if not self.model_loaded:
            await self.load_model()
        if not self.model_loaded:
            raise RuntimeError("TTS model failed to load")
        if not self.voice_cloning_available:
            raise RuntimeError("Voice cloning is unavailable. Check Pocket TTS access requirements and authentication.")
        try:
            import subprocess
            CLONED_DIR.mkdir(parents=True, exist_ok=True)
            raw_audio_path = CLONED_DIR / f"{voice_id}_raw{Path(filename).suffix or '.wav'}"
            raw_audio_path.write_bytes(audio_bytes)
            temp_audio = CLONED_DIR / f"{voice_id}_reference.wav"
            try:
                result = subprocess.run(
                    ["ffmpeg", "-y", "-i", str(raw_audio_path), "-ar", "24000", "-ac", "1", "-c:a", "pcm_s16le", str(temp_audio)],
                    capture_output=True, text=True, check=False
                )
                if result.returncode:
                    raise RuntimeError("FFmpeg failed to convert reference audio: " + result.stderr[-500:])
            finally:
                raw_audio_path.unlink(missing_ok=True)
            voice_state = self.model.get_state_for_audio_prompt(str(temp_audio))
            from pocket_tts import export_model_state
            state_path = str(CLONED_DIR / f"{voice_id}.safetensors")
            export_model_state(voice_state, state_path)
            self._voice_states[voice_id] = voice_state
            logger.info("Voice cloned: %s", voice_id)
            return state_path
        except Exception as exc:
            logger.exception("Voice cloning failed")
            raise RuntimeError(f"Voice cloning failed: {exc}") from exc

    async def generate_preview(self, voice_id: str) -> bytes | None:
        preview_text = "Hello, this is a preview of my voice. I can bring your text to life with natural speech."
        try:
            wav_bytes, _ = await self.generate(preview_text, voice_id)
            return wav_bytes
        except Exception:
            logger.exception("Preview generation failed for %s", voice_id)
            return None
