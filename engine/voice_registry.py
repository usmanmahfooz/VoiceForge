"""
VoiceForge Voice Registry
Manages built-in and cloned voices for Pocket TTS.
"""
import json
import os
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
CONFIG_FILE = DATA_DIR / "config.json"
CLONED_DIR = DATA_DIR / "cloned"

BUILTIN_VOICES = [
    {"id": "alba", "name": "Alba", "gender": "female", "language": "en", "description": "Clear, versatile female voice", "tags": ["versatile", "clear"]},
    {"id": "cosette", "name": "Cosette", "gender": "female", "language": "en", "description": "Soft, gentle female voice", "tags": ["soft", "warm"]},
    {"id": "fantine", "name": "Fantine", "gender": "female", "language": "en", "description": "Expressive female voice", "tags": ["expressive", "emotional"]},
    {"id": "eponine", "name": "Eponine", "gender": "female", "language": "en", "description": "Bright, energetic female voice", "tags": ["bright", "energetic"]},
    {"id": "azelma", "name": "Azelma", "gender": "female", "language": "en", "description": "Light, cheerful female voice", "tags": ["cheerful", "casual"]},
    {"id": "anna", "name": "Anna", "gender": "female", "language": "en", "description": "Calm, professional female voice", "tags": ["calm", "professional"]},
    {"id": "vera", "name": "Vera", "gender": "female", "language": "en", "description": "Rich, mature female voice", "tags": ["rich", "confident"]},
    {"id": "mary", "name": "Mary", "gender": "female", "language": "en", "description": "Friendly female voice", "tags": ["friendly", "podcast"]},
    {"id": "jane", "name": "Jane", "gender": "female", "language": "en", "description": "Natural female voice", "tags": ["natural", "smooth"]},
    {"id": "eve", "name": "Eve", "gender": "female", "language": "en", "description": "Elegant female voice", "tags": ["elegant", "modern"]},
    {"id": "caro_davy", "name": "Caro Davy", "gender": "female", "language": "en", "description": "Distinctive female voice", "tags": ["distinctive", "warm"]},
    {"id": "lola", "name": "Lola", "gender": "female", "language": "en", "description": "Vibrant female voice", "tags": ["vibrant", "dynamic"]},
    {"id": "estelle", "name": "Estelle", "gender": "female", "language": "en", "description": "Graceful female voice", "tags": ["graceful", "melodic"]},
    {"id": "marius", "name": "Marius", "gender": "male", "language": "en", "description": "Strong male voice", "tags": ["strong", "authoritative"]},
    {"id": "javert", "name": "Javert", "gender": "male", "language": "en", "description": "Deep male voice", "tags": ["deep", "commanding"]},
    {"id": "jean", "name": "Jean", "gender": "male", "language": "en", "description": "Warm male voice", "tags": ["warm", "trustworthy"]},
    {"id": "charles", "name": "Charles", "gender": "male", "language": "en", "description": "Refined male voice", "tags": ["refined", "eloquent"]},
    {"id": "paul", "name": "Paul", "gender": "male", "language": "en", "description": "Casual male voice", "tags": ["casual", "friendly"]},
    {"id": "george", "name": "George", "gender": "male", "language": "en", "description": "Steady male voice", "tags": ["steady", "audiobook"]},
    {"id": "michael", "name": "Michael", "gender": "male", "language": "en", "description": "Dynamic male voice", "tags": ["dynamic", "energetic"]},
    {"id": "bill_boerst", "name": "Bill Boerst", "gender": "male", "language": "en", "description": "Classic male voice", "tags": ["classic", "broadcast"]},
    {"id": "peter_yearsley", "name": "Peter Yearsley", "gender": "male", "language": "en", "description": "Distinguished British male voice", "tags": ["british", "distinguished"]},
    {"id": "stuart_bell", "name": "Stuart Bell", "gender": "male", "language": "en", "description": "Clear male voice", "tags": ["clear", "versatile"]},
    {"id": "giovanni", "name": "Giovanni", "gender": "male", "language": "en", "description": "Charismatic male voice", "tags": ["charismatic", "expressive"]},
    {"id": "juergen", "name": "Juergen", "gender": "male", "language": "en", "description": "Precise male voice", "tags": ["precise", "articulate"]},
]

def get_voices():
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    voices = list(BUILTIN_VOICES)
    if CONFIG_FILE.exists():
        try:
            config = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            cloned = config.get("cloned_voices", [])
            for voice in cloned:
                if isinstance(voice, dict) and voice.get("id"):
                    voices.append(voice)
        except (OSError, json.JSONDecodeError):
            pass
    return voices
