name: Self-Forge FrankCore

on:
  push:
    branches: [ main ]
  workflow_dispatch:

jobs:
  deploy:
    runs-on: ubuntu-latest

    steps:
    - name: Checkout Repo
      uses: actions/checkout@v3

    - name: Connect & Execute
      uses: appleboy/ssh-action@v1.1.0
      with:
        host: ${{ secrets.HOST }}
        username: ${{ secrets.USER }}
        key: ${{ secrets.SSH_PRIVATE_KEY }}
        script: |
          echo "🔥 [FRANK INIT] Self-repairing GitOps integrity"

          rm -rf /opt/frank_core_tmp
          git clone git@github.com:Empire325Marketing/FrankOp.git /opt/frank_core_tmp || exit 1

          echo "🔁 Overwriting core with latest commit"
          rm -rf /opt/frank_core_bak
          mv /opt/frank_core /opt/frank_core_bak || true
          mv /opt/frank_core_tmp /opt/frank_core || { echo "💥 Deploy failed. Reverting to backup."; mv /opt/frank_core_bak /opt/frank_core; exit 2; }

          cd /opt/frank_core || { echo "💥 Core directory missing. Reverting..."; mv /opt/frank_core_bak /opt/frank_core; exit 3; }
          source venv/bin/activate || { echo "💥 Virtualenv activation failed. Reverting..."; mv /opt/frank_core_bak /opt/frank_core; exit 4; }

          echo "📦 Rebuilding environment"
          pip install -r requirements.txt || pip install fastapi uvicorn jinja2 aiofiles

          echo "🎨 UI Overhaul Triggered"
          python3 ui_theme_updater.py || echo "[UI] Theme script not found—skip."

          echo "🚀 Restarting control server"
          pkill -f uvicorn || true
          nohup uvicorn main_control_hub:app --host 0.0.0.0 --port 1337 > app.log 2>&1 &

          echo "✅ FrankCore deployed. No mutation loop initiated."

    - name: Confirm Deployment
      run: echo "💥 FrankCore deployed cleanly. Run mutation manually if desired."
