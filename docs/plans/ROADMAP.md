# Project Roadmap

## Planned Features

- [ ] **Push Notifications (Telegram / Discord)**
  - Integrate a Telegram or Discord bot API to send push notifications when an ISP officially drops (NO INTERNET or OFFLINE) or recovers (ONLINE).
  - Tie this directly into the existing debounced state machine to avoid spam during brief network noise.

- [ ] **Daily Automated Speed Tests**
  - Integrate a speed test tool (like `speedtest-cli`) to run automatically at off-peak hours (e.g., 3:00 AM) on both ISPs.
  - Display the last known true capability of the ISP on the dashboard, to compare against the live bandwidth usage.

- [ ] **Automated Failover Trigger (MikroTik Interface Disabler)**
  - **Problem:** Native MikroTik load-balancing sometimes fails to drop a connection experiencing heavy-load failures, causing traffic to still route to a dead ISP.
  - **Solution:** When the backend debouncer officially registers 'NO INTERNET' or 'OFFLINE' for an ISP (like Converge), trigger a POST request to the MikroTik REST API to actively `disable` the interface.
  - **Recovery:** Send a push notification that the interface was auto-disabled. Re-enabling the interface will be done **manually** by the user, as the failure requires a physical check of the hardware before it can be trusted again.
