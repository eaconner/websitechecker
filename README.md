# Website Checker for Home Assistant

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/hacs/default)

A custom Home Assistant integration that monitors the HTTP status of specified websites and exposes them as `binary_sensor` entities. Perfect for keeping tabs on self-hosted services, personal blogs, or external sites directly from your dashboard.

Based on the original work by [@mvdwetering](https://github.com/mvdwetering/websitechecker), this version includes direct **UI Configuration (Config Flow)** support and allows setting a custom **User-Agent** header per site.

> **NOTE:** Generative AI was used to aid in the creation, refactoring, and implementation of the UI Config Flow architecture for this repository.

---

## Features

- **UI Config Flow**: Add, edit, and remove monitored sites directly from **Settings > Devices & Services**.
- **Custom User-Agent**: Set custom HTTP `User-Agent` strings globally or per individual URL to bypass aggressive bot protection filters.
- **Configurable Update Intervals**: Define how frequently each site is checked (in minutes).
- **SSL Certificate Toggle**: Option to ignore SSL validation for internal or self-signed services.
- **Detailed Attributes**: Entities track response state, last status code, and error details.

---

## Installation

### Method 1: HACS (Recommended)

1. Open **HACS** in your Home Assistant UI.
2. Click the three dots in the top right corner and select **Custom repositories**.
3. Add `https://github.com/eaconner/websitechecker` with the category **Integration**.
4. Click **Download** on the Website Checker integration card.
5. Restart Home Assistant.

### Method 2: Manual Installation

1. Download the latest release source zip from [GitHub Releases](https://github.com/eaconner/websitechecker/releases).
2. Extract the archive and copy the `custom_components/websitechecker` directory to your Home Assistant's `config/custom_components/` folder.
3. Restart Home Assistant.

---

## Configuration

### Setting Up via UI (Recommended)

1. In Home Assistant, navigate to **Settings** > **Devices & Services**.
2. Click **Add Integration** in the bottom right corner.
3. Search for **Website Checker**.
4. Fill in the form fields:

| Field | Description | Default |
| :--- | :--- | :--- |
| **Website URL** | The full HTTP or HTTPS URL to monitor. | *Required* |
| **Friendly Name** | Custom display name for the binary sensor entity. | URL string |
| **User-Agent Header** | Custom HTTP `User-Agent` string sent with request. | `HomeAssistant-WebsiteChecker/2.0.0` |
| **Update Interval** | Polling frequency in minutes. | `10` |
| **Verify SSL Certificate** | Whether to enforce valid SSL/TLS certificates. | `true` |

5. Click **Submit**. You can repeat this process for each website you wish to monitor.

---

## Binary Sensor Behavior

The integration creates entities under the `binary_sensor` domain using the `problem` device class:

- **`Off` (Clear/Normal)**: The site returned an HTTP status code lower than 500 (e.g., `200 OK`, `301 Redirect`, `404 Not Found`).
- **`On` (Problem Detected)**: The site returned an HTTP status code $\ge 500$, or the connection timed out/failed.

### Entity Attributes

Each sensor exposes the following attributes for automations or custom dashboard cards:

- `url`: Monitored target URL
- `user_agent`: Configured User-Agent header
- `last_status`: Detailed HTTP status string (e.g., `200 - OK`, `500 - HTTP Error`, `Connection Error`)
- `last_error_status`: Last recorded error message

---

## Example Automations

Send a notification via persistent notification when a site goes down:

```yaml
alias: "Notify when site is unreachable"
trigger:
  - platform: state
    entity_id: binary_sensor.example_main_site
    from: "off"
    to: "on"
action:
  - service: notify.persistent_notification
    data:
      title: "Website Down Alert"
      message: "Monitored website {{ state_attr(trigger.entity_id, 'url') }} is down. Status: {{ state_attr(trigger.entity_id, 'last_status') }}"