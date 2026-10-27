# VoiceForge

**A local-first AI text-to-speech studio for generating natural-sounding audio, managing voices, and creating speech in batches.**

VoiceForge is a browser-based text-to-speech application built with Python, FastAPI, and a modular TTS engine. This repository contains the application source, frontend assets, setup scripts, and deployment guidance.

## Features

- Browser-based speech generation studio
- Voice library and voice management interface
- Voice cloning workflow (availability depends on the configured engine)
- Batch text-to-speech workflow
- Audio preview and playback controls
- Modular Python engine and voice registry
- Windows setup script
- Cloud deployment notes

## Technology

- Python
- FastAPI
- HTML, CSS, and JavaScript
- Pocket TTS integration in the speech engine

## Requirements

- Python 3.11 or another Python version supported by the dependencies and TTS engine
- `pip`
- Internet connection for dependency/model downloads when required

## Quick start

### Windows

1. Download or clone this repository.
2. Open the project directory.
3. Run `Setup.bat` and follow the prompts.
4. Start the server using the command shown by the setup instructions.
5. Open the local URL printed by the server in your browser.

### Manual setup

```bash
python -m venv .venv
```

Activate the environment:

```powershell
.venv\\Scripts\\Activate.ps1
```

On macOS/Linux:

```bash
source .venv/bin/activate
```

Install dependencies:

```bash
python -m pip install --upgrade pip
pip install -r requirements.txt
```

Then follow the startup instructions in `CLOUD_DEPLOYMENT.md` or the setup script. The exact runtime requirements depend on the configured TTS engine and operating system.

## Project structure

```text
VoiceForge/
├── engine/                 # TTS engine, API server, voice registry
├── static/                 # Browser UI, styles, JavaScript, assets
├── data/bgm/               # Optional background music directory
├── preload_model.py        # Optional model preloading helper
├── requirements.txt        # Python dependencies
├── Setup.bat               # Windows setup helper
├── VoiceForge.vbs          # Windows launcher helper
├── CLOUD_DEPLOYMENT.md     # Deployment notes
└── README.md               # Project documentation
```

## Configuration and privacy

Do not commit API keys, passwords, personal voice recordings, generated audio, runtime logs, virtual environments, or local user data. Review `data/` and your configuration files before pushing changes. Use environment variables or a local untracked configuration file for secrets.

Voice cloning should only be used with voice recordings you own or have explicit permission to process. Check the licenses and usage terms of each model and dependency before commercial use.

## Deployment

See [`CLOUD_DEPLOYMENT.md`](CLOUD_DEPLOYMENT.md) for deployment notes. For public hosting, configure persistent storage and resource limits as required by the selected TTS engine. Do not expose a development server directly to the internet without appropriate security controls.

## Troubleshooting

- If package installation fails, confirm your Python version and platform match the dependencies.
- If the model does not load, review the terminal logs and follow the model's documented download/setup process.
- If audio generation fails, check that the configured TTS engine is installed and that the process can write to its output directory.

## Contributing

Issues and pull requests are welcome. Include reproduction steps, platform details, and relevant error messages, while removing tokens, private audio, and personal data.

## License

No license is currently included. Unless a license is added, all rights remain with the copyright holder and reuse permissions should not be assumed.

---

**Topics:** `text-to-speech`, `tts`, `voice-cloning`, `speech-synthesis`, `fastapi`, `python`, `pocket-tts`, `audio-generation`, `ai-audio`, `voice-generator`
