"""Persistent registry for built-in and user-created VoiceForge voices."""
import json
from pathlib import Path
from threading import RLock

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
CONFIG_FILE = DATA_DIR / "config.json"
CLONED_DIR = DATA_DIR / "cloned"

BUILTIN_VOICES = [
    {"id":"alba","name":"Alba","gender":"female","language":"en","description":"Clear, versatile female voice","tags":["versatile","clear"]},
    {"id":"cosette","name":"Cosette","gender":"female","language":"en","description":"Soft, gentle female voice","tags":["soft","warm"]},
    {"id":"fantine","name":"Fantine","gender":"female","language":"en","description":"Expressive female voice","tags":["expressive","emotional"]},
    {"id":"eponine","name":"Eponine","gender":"female","language":"en","description":"Bright, energetic female voice","tags":["bright","energetic"]},
    {"id":"azelma","name":"Azelma","gender":"female","language":"en","description":"Light, cheerful female voice","tags":["cheerful","casual"]},
    {"id":"anna","name":"Anna","gender":"female","language":"en","description":"Calm, professional female voice","tags":["calm","professional"]},
    {"id":"vera","name":"Vera","gender":"female","language":"en","description":"Rich, mature female voice","tags":["rich","confident"]},
    {"id":"mary","name":"Mary","gender":"female","language":"en","description":"Friendly female voice","tags":["friendly","podcast"]},
    {"id":"jane","name":"Jane","gender":"female","language":"en","description":"Natural female voice","tags":["natural","smooth"]},
    {"id":"eve","name":"Eve","gender":"female","language":"en","description":"Elegant female voice","tags":["elegant","modern"]},
    {"id":"caro_davy","name":"Caro Davy","gender":"female","language":"en","description":"Distinctive female voice","tags":["distinctive","warm"]},
    {"id":"lola","name":"Lola","gender":"female","language":"en","description":"Vibrant female voice","tags":["vibrant","dynamic"]},
    {"id":"estelle","name":"Estelle","gender":"female","language":"en","description":"Graceful female voice","tags":["graceful","melodic"]},
    {"id":"marius","name":"Marius","gender":"male","language":"en","description":"Strong male voice","tags":["strong","authoritative"]},
    {"id":"javert","name":"Javert","gender":"male","language":"en","description":"Deep male voice","tags":["deep","commanding"]},
    {"id":"jean","name":"Jean","gender":"male","language":"en","description":"Warm male voice","tags":["warm","trustworthy"]},
    {"id":"charles","name":"Charles","gender":"male","language":"en","description":"Refined male voice","tags":["refined","eloquent"]},
    {"id":"paul","name":"Paul","gender":"male","language":"en","description":"Casual male voice","tags":["casual","friendly"]},
    {"id":"george","name":"George","gender":"male","language":"en","description":"Steady male voice","tags":["steady","audiobook"]},
    {"id":"michael","name":"Michael","gender":"male","language":"en","description":"Dynamic male voice","tags":["dynamic","energetic"]},
    {"id":"bill_boerst","name":"Bill Boerst","gender":"male","language":"en","description":"Classic male voice","tags":["classic","broadcast"]},
    {"id":"peter_yearsley","name":"Peter Yearsley","gender":"male","language":"en","description":"Distinguished British male voice","tags":["british","distinguished"]},
    {"id":"stuart_bell","name":"Stuart Bell","gender":"male","language":"en","description":"Clear male voice","tags":["clear","versatile"]},
    {"id":"giovanni","name":"Giovanni","gender":"male","language":"en","description":"Charismatic male voice","tags":["charismatic","expressive"]},
    {"id":"juergen","name":"Juergen","gender":"male","language":"en","description":"Precise male voice","tags":["precise","articulate"]},
    {"id":"rafael","name":"Rafael","gender":"male","language":"en","description":"Natural male voice","tags":["natural","conversational"]},
]

class VoiceRegistry:
    def __init__(self):
        self._lock = RLock()
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        CLONED_DIR.mkdir(parents=True, exist_ok=True)
        if not CONFIG_FILE.exists():
            CONFIG_FILE.write_text(json.dumps({"verified": False, "cloned_voices": []}, indent=2), encoding="utf-8")

    def _read_config(self):
        try:
            value = json.loads(CONFIG_FILE.read_text(encoding="utf-8"))
            if isinstance(value, dict):
                return value
        except (OSError, json.JSONDecodeError):
            pass
        return {"verified": False, "cloned_voices": []}

    def _write_config(self, config):
        temp = CONFIG_FILE.with_suffix(".tmp")
        temp.write_text(json.dumps(config, ensure_ascii=False, indent=2), encoding="utf-8")
        temp.replace(CONFIG_FILE)

    def get_all_voices(self, gender=None, language=None, search=None):
        with self._lock:
            config = self._read_config()
            voices = list(BUILTIN_VOICES)
            for item in config.get("cloned_voices", []):
                if isinstance(item, dict) and item.get("id"):
                    voices.append(item)
            if gender:
                voices = [v for v in voices if v.get("gender") == gender]
            if language:
                voices = [v for v in voices if v.get("language", "en") == language]
            if search:
                query = search.casefold()
                voices = [v for v in voices if query in (v.get("name", "") + " " + v.get("description", "")).casefold()]
            return voices

    def get_voice(self, voice_id):
        return next((v for v in self.get_all_voices() if v.get("id") == voice_id), None)

    def get_languages(self):
        return sorted({v.get("language", "en") for v in self.get_all_voices()})

    def is_verified(self):
        return bool(self._read_config().get("verified", False))

    def set_verified(self, verified=True):
        with self._lock:
            config = self._read_config()
            config["verified"] = bool(verified)
            self._write_config(config)

    def add_cloned_voice(self, voice_id, name, state_path, language="en"):
        voice = {"id": voice_id, "name": name, "gender": "other", "language": language or "en",
                 "description": "User-cloned voice", "is_cloned": True, "state_path": state_path, "tags": ["cloned"]}
        with self._lock:
            config = self._read_config()
            cloned = [v for v in config.get("cloned_voices", []) if v.get("id") != voice_id]
            cloned.append(voice)
            config["cloned_voices"] = cloned
            self._write_config(config)
        return voice

    def remove_cloned_voice(self, voice_id):
        with self._lock:
            config = self._read_config()
            cloned = config.get("cloned_voices", [])
            match = next((v for v in cloned if v.get("id") == voice_id), None)
            if match is None:
                return False
            config["cloned_voices"] = [v for v in cloned if v.get("id") != voice_id]
            self._write_config(config)
            for suffix in (".safetensors", "_reference.wav"):
                try:
                    (CLONED_DIR / f"{voice_id}{suffix}").unlink(missing_ok=True)
                except OSError:
                    pass
            return True
