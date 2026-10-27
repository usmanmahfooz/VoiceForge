# Deploying VoiceForge

VoiceForge runs a Python/FastAPI backend and a browser-based frontend. Static hosting alone cannot run the Python speech engine; use a Python-capable container or application host.

## Before deploying

- Confirm the TTS model and its license terms permit your intended use.
- Configure persistent storage only for data that must survive restarts.
- Keep secrets in the host's secret manager or environment variables, never in Git.
- Add authentication, request-size limits, rate limits, and access controls before exposing endpoints publicly.
- Consider CPU and RAM requirements for model loading and concurrent generation.
- Store generated audio in an appropriate object store if it must persist, and apply retention limits.
- Do not expose the development server directly to the public internet.

## Container-oriented deployment

1. Build a container containing the `engine/`, `static/`, and `requirements.txt`.
2. Install Python dependencies during the image build.
3. Configure the service to start the FastAPI application using the project's supported entry point.
4. Provide writable temporary/output storage and any required model cache.
5. Set health checks and resource limits, then test startup and generation under realistic load.

The exact start command and model setup can vary by host and dependency version. Verify these details in the source and target platform before deploying.

## Firebase note

Firebase Hosting is suitable for static assets, but it does not itself run the Python TTS backend. A separate Python-capable service is required for the complete application.

## SaaS hardening checklist

- User authentication and authorization
- Per-user quotas and rate limiting
- Background jobs for long-running generation
- Persistent storage and cleanup policies
- Logging with private paths, audio, and secrets redacted
- Dependency and model license review
- Monitoring for latency, errors, resource use, and abuse
