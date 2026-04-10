# 🤖 AutoBard Automation Setup Guide

Follow these steps to migrate your local AutoBard to a **24/7 Autonomous Content Factory** on GitHub.

## 1. Prepare Your GitHub Repository
1. Create a **Private** repository on GitHub.
2. Push all files (except those in `.gitignore`) to the repository:
   ```bash
   git init
   git remote add origin https://github.com/your-username/AutoBard.git
   git add .
   git commit -m "Initial commit: Series Factory"
   git push -u origin main
   ```

## 2. Set Up GitHub Secrets
Go to your repo on GitHub: **Settings > Secrets and variables > Actions > New repository secret**.
Add the following secrets:

| Secret Name | Value Description |
| :--- | :--- |
| `ENV_BASE64` | Base64 encoded content of your local `.env` file |
| `CLIENT_SECRET_BASE64` | Base64 encoded content of your `client_secret.json` |
| `YOUTUBE_TOKEN_BASE64` | Base64 encoded content of your `youtube_token.pickle` |

### How to get Base64 strings (in PowerShell):
Run these commands and copy the output:
```powershell
# For .env
[Convert]::ToBase64String([IO.File]::ReadAllBytes(".env"))

# For client_secret.json
[Convert]::ToBase64String([IO.File]::ReadAllBytes("client_secret.json"))

# For youtube_token.pickle
[Convert]::ToBase64String([IO.File]::ReadAllBytes("youtube_token.pickle"))
```

## 3. How the Automation Works
- **Schedule**: The `.github/workflows/daily_autobard.yml` is set to run at **00:00 UTC (9:00 AM KST)** daily.
- **Auto-Scheduler**:
  - Every morning, it calls AI to invent a new "Modern Urban Legend" or "Traditional Ghost Story."
  - It generates the video, including a **Teaser (Coming Soon)** for tomorrow's topic.
  - It uploads the result to YouTube automatically.
  - It updates `temp/scheduler_state.json` and commits it back to GitHub to remember what it planned for tomorrow.

## 4. Manual Trigger
You can also run it manually at any time:
1. Go to the **Actions** tab in your GitHub repo.
2. Select **Daily AutoBard Production**.
3. Click **Run workflow**.

---
**Happy Automating!** 👹📺
