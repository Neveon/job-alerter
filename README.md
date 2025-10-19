# 🧠 job-alerter

A lightweight Python service that checks **top companies in your area** (from [Levels.fyi](https://www.levels.fyi/)) for new job postings and emails you when matches appear.

Development is done **entirely inside a Docker dev container**, ensuring every contributor shares the same Python, dependencies, and tools—no more “works on my machine.”

---

## 💻 Development Workflow

All development is done **inside a Docker container** with **LunarVim (lvim)** preinstalled.

### 1. Build and start the container
```bash
docker compose -f docker-compose.dev.yml build
docker compose -f docker-compose.dev.yml up -d
```

This will:
- Build the Python 3.12 image from `.devcontainer/Dockerfile`
- Install project dependencies from `requirements.txt` and `requirements-dev.txt`
- Install Neovim (v0.10+) and LunarVim with all dependencies
- Keep the container running in the background

### 2. Exec into the container
```bash
docker exec -it job-alerter-dev bash
```

You’ll land in `/work`, the project root inside the container.

Your prompt should now look like:
```
dev@container:/work$
```

### 3. Start coding with LunarVim or execute tests or main

You now have a full IDE-like setup in the terminal.  
LunarVim already includes Treesitter, Mason, and LSP tooling support.

```bash
lvim .

pytest -q

python3 src/main.py
```

### 4. Stop or clean up
```bash
# Exit when done working in container
exit

# Stop container
docker compose down

# Rebuild from scratch (optional)
docker compose build --no-cache
```

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

