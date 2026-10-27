import asyncio
import sys
from pathlib import Path

# Add engine to path.
sys.path.append(str(Path(__file__).parent / "engine"))
from tts_engine import TTSEngine


async def main():
    print("Initializing neural weights...")
    engine = TTSEngine()
    await engine.load_model()
    if engine.model_loaded:
        print("Success: neural weights are ready.")
    else:
        print("Error: failed to load neural weights.")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
