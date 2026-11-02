# Winter Arc

93 days, 30 Oct 2026 to 30 Jan 2027 (Casablanca time).

- Countdown page: https://claude.ai/artifact/SFb7AenMS47rDyjGLBjjH6 (source in `page/index.html`)
- Push reminders at 08:30, 18:00 and 22:30 Casablanca time, sent to ntfy.sh by GitHub Actions
  (`.github/workflows/reminders.yml`, messages in `send_reminder.py`).

## Setup

1. Add a repository secret `NTFY_TOPIC` (Settings > Secrets and variables > Actions) with your topic name.
2. Install the ntfy app (Android / iOS) and subscribe to the same topic on ntfy.sh.
3. Actions tab > "Winter Arc reminders" > Run workflow to send a test.

GitHub may deliver scheduled runs a few minutes late.
