#!/bin/bash
echo "[+] Starting JAMES mutation cycle..."
end=$((SECONDS+39600))
while [ $SECONDS -lt $end ]; do
  python3 feedback_rewriter.py
  python3 prompt_mutate.py
  python3 phantom_fork.py
  python3 omega_simulator.py
  python3 injection_proxy.py
  sleep 300
done
echo "[+] JAMES LOOP COMPLETE."
