# Contributing to VoiceForge

Thanks for helping improve VoiceForge.

## Before opening an issue

- Search existing issues first.
- Include operating system, Python version, setup method, and reproduction steps.
- Share sanitized logs only. Do not include tokens, credentials, private audio, or personal data.

## Changes

- Keep pull requests focused.
- Test Python syntax with `python -m compileall -q engine preload_model.py`.
- Test the voice registry with `pytest` after installing `requirements-dev.txt`.
- Do not commit virtual environments, model weights, generated audio, local logs, or cloned voice profiles.
- Document any new configuration variables and deployment requirements.

## Voice and audio data

Only use voices and audio recordings that you own or have explicit permission to process. Do not submit private reference recordings as repository test fixtures.
