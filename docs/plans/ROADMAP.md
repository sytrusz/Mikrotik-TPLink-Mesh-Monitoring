# Project Roadmap

## Planned Features

- [ ] **Interactive Telegram Bot (Push Notifications & Chat-Ops)**
  - Integrate `python-telegram-bot` to send real-time alerts when an ISP officially drops or recovers.
  - **Two-Way Interaction:** Allow the user to query the bot (e.g., `/status`) to get live router metrics (CPU, Temp, ISP speeds) directly on their phone.
  - **Secure Access:** Restrict bot commands to the user's specific Telegram ID for security.

- [ ] **Automated Failover Trigger with Manual Recovery Button**
  - **Problem:** Native MikroTik load-balancing sometimes fails to drop a connection experiencing heavy-load failures.
  - **Automated Action:** When the backend debouncer officially registers 'NO INTERNET' or 'OFFLINE' for an ISP, trigger a POST request to the MikroTik REST API to actively `disable` that specific interface.
  - **Interactive Recovery:** The Telegram alert will include an **Inline Button** (e.g., "[ ✅ Re-enable Converge ]"). Tapping this button will send a command back to the server to re-enable the port after the user has finished their physical verification.

