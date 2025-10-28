# Deployment Guide

This document shows two straightforward ways to deploy the Valo Spectator Ghost Flask demo.

Option A — Render (recommended, easy)

1. Create a Render account (https://render.com).
2. Create a new Web Service and connect your GitHub repository `solaimon-sharifi/valo-project-1-`.
3. Set the build and start commands (Render defaults usually work):

   Build Command: pip install -r requirements.txt
   Start Command: gunicorn app:app --bind 0.0.0.0:$PORT

4. Add your OpenAI API key as a secret env var in the Render service settings:
   - Key: OPENAI_API_KEY
   - Value: sk-...

5. Deploy — Render will build and run the service and provide a public URL.

Option B — Docker (portable)

1. Build locally:

   docker build -t valo-spectator-ghost .

2. Run locally (map port 5000):

   docker run -e OPENAI_API_KEY=sk-... -p 5000:5000 valo-spectator-ghost

3. For a production container, push to Docker Hub or GitHub Container Registry and configure your cloud provider to run it.

Quick notes
- Add `OPENAI_API_KEY` to platform secrets — never store keys in the repo.
- For simple demos, Render is fast and requires minimal config.

Demo mode
---------

If you don't want to provide an `OPENAI_API_KEY` (for example when sharing
the repo or during a classroom demo), the app will run in a safe demo mode
and return deterministic example responses. This is useful for showing the
UI without exposing secrets or using real API calls.

Files included for deployment
-----------------------------

- `Dockerfile` — builds a container image that runs the app with Gunicorn.
- `Procfile` — for Render/Heroku-style platforms that use Procfiles.

