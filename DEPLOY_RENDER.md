# Deploying to Render (automatic via GitHub Actions)

This repository includes a GitHub Actions workflow that can trigger deployments to Render when you push to `main`.

What you need to do:

1. Create a Web Service on Render
   - Log in to https://render.com and create a new Web Service.
   - Connect your GitHub account and select this repository.
   - For the build command, use the default or ensure dependencies are installed via `pip install -r requirements.txt`.
   - For the start command, use: `gunicorn app:app --bind 0.0.0.0:$PORT` (or `python app.py` for a simple run).

2. Obtain the Service ID and an API Key
   - Service ID: In the Render dashboard, open your service and look for the service details. The service ID is available in the service settings or the service URL. Copy it.
   - API Key: Generate an API key from the Render dashboard (Account → API Keys). Create a new key and copy it.

3. Add repository secrets on GitHub
   - Go to your GitHub repository → Settings → Secrets and variables → Actions → New repository secret.
   - Add two secrets:
     - `RENDER_SERVICE_ID` — the service id you copied from Render
     - `RENDER_API_KEY` — the Render API key you generated

4. Trigger a deploy
   - Push to `main` (or use the Actions tab to manually run the workflow via `workflow_dispatch`).
   - The workflow will call the Render API to create a new deploy for your service.

Notes
-----
- The workflow uses the Render REST API endpoint `POST https://api.render.com/v1/services/{serviceId}/deploys` to create a deploy. If Render updates their API, update `.github/workflows/deploy_render.yml` accordingly.
- This workflow will fail early if the required secrets are not set.
- For a stable public URL, use the URL Render provides for the Web Service (example: `https://<your-service>.onrender.com`).

If you'd like, I can also add an action to automatically update a README badge with the Render URL once the service exists (requires the Render URL to be known). Ask me to add that and I'll implement it.
