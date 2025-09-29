# 🚀 FastAPI GitHub Issues Gateway

A FastAPI service that integrates with ****GitHub Issues**** and consumes ****GitHub Webhooks****.
You can run it locally using ****Python**** or inside ****Docker****.
For webhook testing, use ****ngrok**** to expose your local server.

---

## 1. 📂 Clone the Repository

```bash
git clone https://github.com/<your-org>/<your-repo>.git
cd <your-repo>
```

---

## 2. 📦 Prerequisites

Make sure the following are installed:

### Python
- Version ****3.9+****
```bash
python --version
```

### Docker
- [Install Docker Desktop](https://www.docker.com/products/docker-desktop) (Windows/macOS)
- Linux (Debian/Ubuntu):
  ```bash
  sudo apt-get update
  sudo apt-get install docker.io docker-compose-plugin
  ```
- Verify:
  ```bash
  docker --version
  docker compose version
  ```

### ngrok
Used to expose your local app to GitHub webhooks.
- [Download ngrok](https://ngrok.com/download) or install via package manager:
  ```bash
  # macOS
  brew install ngrok/ngrok/ngrok

  # Linux (snap)
  sudo snap install ngrok
  ```
- Verify:
  ```bash
  ngrok version
  ```

---

## 3. 📁 Project Structure

```
.
├── app/
│   ├── main.py # FastAPI entrypoint
│   ├── config.py # Settings
│   ├── github.py # GitHub API integration
│   ├── webhook.py # Webhook handler
│   ├── rate_limit.py # Rate limiting
│   ├── pagination.py # Pagination
│   ├── logging.py # Logging setup
│   └── models.py # Data models
│
├── scripts/
│   └── dev.sh # Docker startup script
│
├── tests/               # Pytest tests
├── compose.yaml          # Docker Compose definition
├── Dockerfile            # Image build
├── requirements.txt      # Python dependencies
├── .env                  # Environment variables (ignored in git)
└── README.md             # This documentation
```

---

## 4. ⚙️ Environment Variables

Create a `.env` file in the project root:

```dotenv
# GitHub Personal Access Token (must have repo + webhook scopes)
GITHUB_TOKEN=

# GitHub repository info
GITHUB_OWNER=REST-Assured-CMPE-272
GITHUB_REPO=GitHub-Service-Issues

# Webhook secret (must match GitHub webhook settings)
WEBHOOK_SECRET=webhooktestak

# Application port
PORT=8080
```

### Required GitHub Token Scopes

Generate Personal Access Token at: [https://github.com/settings/tokens](https://github.com/settings/tokens)

---

## 5. 🖥️ Run Locally without Docker

1. Create & activate virtual environment:
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Start the app:
   ```bash
   uvicorn app.main:app --reload --host 0.0.0.0 --port ${PORT:-8080}
   ```

4. Start ngrok in another terminal:
   ```bash
   ngrok http 8080
   ```
   Example output:
   ```
   Forwarding https://a1b2c3d4.ngrok.io -> http://localhost:8080
   ```

5. [Configure GitHub webhook](#github-webhook-setup-redelivery):
   - Payload URL → `https://a1b2c3d4.ngrok.io/webhook`
   - Secret → must match `WEBHOOK_SECRET`

---

## 6. 🐳 Run Locally with Docker

1. Ensure `.env` is configured.
2. Start with helper script:
   ```bash
   ./scripts/dev.sh
   ```
   - Builds the Docker image
   - Starts containers in the background

3. Access the app:
   - API root → [http://127.0.0.1:8080/](http://127.0.0.1:8080/)
   - Swagger Docs → [http://127.0.0.1:8080/docs](http://127.0.0.1:8080/docs)

4. Start ngrok in another terminal:
   ```bash
   ngrok http 8080
   ```
   Example output:
   ```
   Forwarding https://a1b2c3d4.ngrok.io -> http://localhost:8080
   ```

5. [Configure GitHub webhook](#github-webhook-setup-redelivery):
   - Payload URL → `https://a1b2c3d4.ngrok.io/webhook`
   - Secret → must match `WEBHOOK_SECRET`

6. Stop containers:
   ```bash
   docker compose down
   ```

---

✅ You now have the app running locally and connected to GitHub via ngrok!


---

# 📖 API Usage Examples

This service exposes a simple API for managing GitHub issues and comments, as well as receiving webhook events.

Load env file into your shell:

```bash
export $(cat .env | xargs)
export BASE_URL="http://localhost:$PORT"
```

Now you can use `$BASE_URL` in all curl commands.
_*(You only need to be in the folder with `.env` when running the `export` — after that, you can curl from anywhere.)*_

---

## Endpoints

### Health Check — `GET /healthz`
```bash
curl "$BASE_URL/healthz"
```

---

### Create an Issue — `POST /issues`
```bash
curl -i "$BASE_URL/issues"   -H "Content-Type: application/json" -d '{
        "title": "Bug: API returns 500 on PATCH",
        "body": "Steps to reproduce...\nExpected...\nActual...",
        "labels": ["bug","api"]
      }'
```

---

### List Issues — `GET /issues`
```bash
# Default (open issues)
curl -i "$BASE_URL/issues"

# With filters
curl -i "$BASE_URL/issues?state=all&labels=bug,api&page=2&per_page=50"
```

---

### Get a Single Issue — `GET /issues/{number}`
```bash
ISSUE=42
curl "$BASE_URL/issues/$ISSUE"
```

---

### Update an Issue — `PATCH /issues/{number}`
```bash
ISSUE=42
curl -X PATCH "$BASE_URL/issues/$ISSUE"   -H "Content-Type: application/json" -d '{ "state": "closed" }'
```

---

### Create a Comment — `POST /issues/{number}/comments`
```bash
ISSUE=42
curl -X POST "$BASE_URL/issues/$ISSUE/comments"   -H "Content-Type: application/json" -d '{ "body": "Thanks for the report! We'\''re investigating. 🙏" }'
```

---

### GitHub Webhook Receiver — `POST /webhook`
```bash
curl -i -X POST "$BASE_URL/webhook"   -H "Content-Type: application/json" -d '{
        "action": "opened",
        "issue": { "number": 123, "title": "Sample issue", "state": "open" },
        "repository": { "full_name": "acme/repo" }
      }'
```

---

### Debug: Recent Webhook Events — `GET /events`
```bash
curl "$BASE_URL/events?limit=10"
```

---

## Notes

- Add `-i` to curl to see response headers (e.g., `Location`, `Link`).
- Change `ISSUE=42` to the issue number you want to fetch/update/comment on.
- The server reads the `GITHUB_TOKEN` directly from `.env`, so no need to pass `Authorization` headers in curl.


---

# 🔔 GitHub Webhook Setup & Redelivery

Once your app is running locally ****and exposed via ngrok****, complete these steps to connect GitHub:

## 1. Create webhook in GitHub

1. Go to your repository → ****Settings → Webhooks → Add webhook****
2. ****Payload URL:**** `https://<ngrok-id>.ngrok-free.app/webhook`
3. ****Content type:**** `application/json`
4. ****Secret:**** use the value of `WEBHOOK_SECRET` from `.env`
5. ****Events:**** Select
   - ✅ Issues
   - ✅ Issue comments
6. Save. GitHub will immediately send a ****ping**** event.

## 2. Trigger events from GitHub UI

- Create a new issue → triggers an ****`issues`**** event (`opened`)
- Add a comment → triggers an ****`issue_comment`**** event (`created`)
- Edit/close/reopen → additional ****`issues`**** events

## 3. Check event logs

Webhook payloads are logged into `events.jsonl`.
Each event is stored as ****one JSON object per line****. Example:

```json
{"id": "b3dc85fe-9c2a-11f0-982e-8a365c3ac1c1", "event": "issue_comment", "action": "deleted", "issue_number": 15, "timestamp": "2025-09-28T05:19:27Z"}
```

To view logs in real time:

```bash
tail -f events.jsonl
```

## 4. Redeliver failed events

- ****GitHub UI:****
  Repo → ****Settings → Webhooks**** → select webhook → ****Recent Deliveries**** → ****Redeliver****

- ****GitHub API:****
  Use [`/repos/{owner}/{repo}/hooks/{hook_id}/deliveries`](https://docs.github.com/en/rest/webhooks/repo-deliveries) to list and retry deliveries.