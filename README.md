# 🧠 job-alerter

A lightweight Python service that checks **top companies in your area** (from [Levels.fyi](https://www.levels.fyi/)) for new job postings and emails you when matches appear.

Development is done **entirely inside a Docker dev container**, ensuring every contributor shares the same Python, dependencies, and tools—no more “works on my machine.”

---

## 🚀 Quick Start (Development)

### 1️⃣ Build the dev container
```bash
docker compose -f docker-compose.dev.yml build
```
Builds the isolated Python environment with all required tools (linters, test runners, etc.).

### 2️⃣ Start the container
```bash
docker compose -f docker-compose.dev.yml up -d
```
Starts the container in the background and mounts your source code.

### 3️⃣ Enter the container
```bash
docker compose -f docker-compose.dev.yml exec dev bash
```
Your prompt should now look like:
```
dev@container:/work$
```

### 4️⃣ Set up dependencies (first time only)
Inside the container:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip3 install -r requirements.txt
pip3 install pre-commit ruff black pytest
pre-commit install
```
This creates a project-local Python environment (`.venv`) stored on your host for persistence.

---

## 💻 Daily Developer Flow

After the first setup, your `.venv` and dependencies persist across sessions.

Each day:
```bash
# 1. Start the container again
docker compose -f docker-compose.dev.yml up -d

# 2. Enter it
docker compose -f docker-compose.dev.yml exec dev bash

# 3. Activate your venv
source .venv/bin/activate

# 4. Run tests or start coding
pytest -q
python3 src/main.py

# 5. Commit your work (pre-commit hooks will auto-run)
git add .
git commit -m "Your message"

# 6. Exit when done
exit

# 7. Stop the container (optional)
docker compose -f docker-compose.dev.yml down
```
You do **not** need to reinstall dependencies every day—your `.venv` folder persists between runs.

---

## 🧪 Optional: Auto-run tests before every commit

Add this snippet to `.pre-commit-config.yaml` to automatically run tests on commit:

```yaml
- repo: local
  hooks:
    - id: run-tests
      name: Run pytest
      entry: pytest -q
      language: system
      pass_filenames: false
```

---

## 🧹 Clean up / Rebuild Environment

If you ever want to fully reset your dev environment:
```bash
docker compose -f docker-compose.dev.yml down
docker system prune -f
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
docker compose -f docker-compose.dev.yml exec dev bash
```
Then recreate your `.venv` and reinstall dependencies as shown above.

