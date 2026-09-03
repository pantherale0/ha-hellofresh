# HelloFresh

[![GitHub Release][releases-shield]][releases]
[![GitHub Activity][commits-shield]][commits]
[![License][license-shield]](LICENSE)

[![hacs][hacsbadge]][hacs]
![Project Maintenance][maintenance-shield]

<!--
Uncomment and customize these badges if you want to use them:

[![BuyMeCoffee][buymecoffeebadge]][buymecoffee]
[![Discord][discord-shield]][discord]
-->

**✨ Develop in the cloud:** Want to contribute or customize this integration? Open it directly in GitHub Codespaces - no local setup required!

[![Open in GitHub Codespaces](https://github.com/codespaces/badge.svg)](https://codespaces.new/pantherale0/ha-hellofresh?quickstart=1)

## ✨ Features

- **Magic-link setup**: Connect with HelloFresh passwordless login (or paste tokens)
- **Account sensors**: Credit balance, household size, dietary exclusions, subscription info
- **Menu & deliveries**: Next delivery week, selected/available meals, cart total
- **Delivery calendar**: Week-based events from past and upcoming deliveries
- **Recipe services**: `hellofresh.get_recipe` and `hellofresh.search_recipes` with response data for scripts, automations, and AI tools
- **LLM API**: Registers a HelloFresh LLM API (recipe search/get + delivery summary) for Assist/conversation agents and [MCP](https://www.home-assistant.io/integrations/mcp_server/)
- **Multi-region**: Country/locale selection for common HelloFresh markets
- **Token refresh**: Persists refreshed access tokens automatically
- **Options flow**: Adjust the polling interval after setup

**This integration will set up the following platforms.**

| Platform        | Description                                                        |
| --------------- | ------------------------------------------------------------------ |
| `sensor`        | Account credit, household, meals, cart total, subscription details |
| `binary_sensor` | API connectivity and meals-ready status                            |
| `calendar`      | Delivery weeks from HelloFresh schedule history                    |
| `button`        | Force a data refresh                                               |

Powered by [`pyhellofresh`](https://github.com/pantherale0/pyhellofresh).

## 🚀 Quick Start

### Step 1: Install the Integration

**Prerequisites:** This integration requires [HACS](https://hacs.xyz/) (Home Assistant Community Store) to be installed.

Click the button below to open the integration directly in HACS:

[![Open your Home Assistant instance and open a repository inside the Home Assistant Community Store.](https://my.home-assistant.io/badges/hacs_repository.svg)](https://my.home-assistant.io/redirect/hacs_repository/?owner=pantherale0&repository=ha-hellofresh&category=integration)

Then:

1. Click "Download" to install the integration
2. **Restart Home Assistant** (required after installation)

> [!NOTE]
> The My Home Assistant redirect will first take you to a landing page. Click the button there to open your Home Assistant instance.

<details>
<summary><strong>Manual Installation (Advanced)</strong></summary>

If you prefer not to use HACS:

1. Download the `custom_components/hellofresh/` folder from this repository
2. Copy it to your Home Assistant's `custom_components/` directory
3. Restart Home Assistant

</details>

### Step 2: Add and Configure the Integration

**Important:** You must have installed the integration first (see Step 1) and restarted Home Assistant!

#### Option 1: One-Click Setup (Quick)

Click the button below to open the configuration dialog:

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=hellofresh)

Follow the setup wizard:

1. Choose **Magic link (recommended)** (or **Access token** for advanced use)
2. Enter your HelloFresh email and country
3. Open the email HelloFresh sends and paste the magic link URL (or code)
4. Submit — the integration stores tokens and starts polling

#### Option 2: Manual Configuration

1. Go to **Settings** → **Devices & Services**
2. Click **"+ Add Integration"**
3. Search for "HelloFresh"
4. Follow the same setup steps as Option 1

### Step 3: Adjust Settings (Optional)

After setup, you can adjust options:

1. Go to **Settings** → **Devices & Services**
2. Find **HelloFresh**
3. Click **Configure** to adjust the update interval

You can also **Reconfigure** to change email/country and complete a new magic-link login.

### Step 4: Start Using!

The integration creates entities for your HelloFresh account:

- **Sensors**: credit, household, dietary exclusions, meals, cart total, subscription
- **Binary sensors**: API connection, meals ready
- **Calendar**: delivery weeks
- **Button**: refresh

Find all entities in **Settings** → **Devices & Services** → **HelloFresh**.

## Available Entities

### Sensors

- **Account credit**: Credit balance (monetary)
- **Adults / Children / Total people**: Household size from your profile
- **Dietary exclusions**: Count of exclusions (list in attributes)
- **Next delivery week**: Upcoming ISO week (e.g. `2026-W32`)
- **Selected meals / Available meals**: Counts with meal details in attributes
- **Cart total**: Calculated box price for the next week
- **Subscription status / plan**: Active subscription summary
- **Active subscription ID** (diagnostic)

### Binary Sensors

- **API connection**: Whether the last coordinator update succeeded
- **Meals ready**: Whether the weekly menu reports meals as ready

### Calendar

- **Deliveries**: Events for past and upcoming HelloFresh delivery weeks

### Button

- **Refresh**: Force an immediate data refresh

## Custom Services

Response-capable services for scripts, automations, and AI tools:

### `hellofresh.get_recipe`

```yaml
action: hellofresh.get_recipe
data:
  recipe_id: "64f1a2b3c4d5e6f7a8b9c0d1"
response_variable: recipe
```

### `hellofresh.search_recipes`

```yaml
action: hellofresh.search_recipes
data:
  query: "pasta"
  take: 10
response_variable: recipes
```

When multiple HelloFresh accounts are configured, pass `config_entry_id`.

## LLM / AI tools

This integration registers a Home Assistant [LLM API](https://developers.home-assistant.io/docs/core/llm/) per config entry (`hellofresh-<entry_id>`).

Tools exposed to conversation agents (and automatically over MCP when the MCP Server integration is set up):

| Tool                           | Purpose                                         |
| ------------------------------ | ----------------------------------------------- |
| `GetHelloFreshDeliverySummary` | Next week, selected meals, credit, subscription |
| `SearchHelloFreshRecipes`      | Keyword recipe search                           |
| `GetHelloFreshRecipe`          | Full recipe details by `recipe_id`              |

In a conversation agent that supports selecting LLM APIs, enable the **HelloFresh** API for that agent. With [MCP Server](https://www.home-assistant.io/integrations/mcp_server/), the API is available at `/api/mcp/hellofresh-<entry_id>`.

## Configuration Options

### During Setup

| Name          | Required | Description                                  |
| ------------- | -------- | -------------------------------------------- |
| Email         | Yes\*    | HelloFresh account email (\*magic-link flow) |
| Country       | Yes      | Regional HelloFresh market                   |
| Magic link    | Yes\*    | URL from the email (\*or code)               |
| Access token  | Yes\*    | Bearer token (\*token flow only)             |
| Refresh token | No       | Long-lived refresh token (recommended)       |

### After Setup (Options)

| Name            | Default | Description               |
| --------------- | ------- | ------------------------- |
| Update Interval | 1 hour  | How often to refresh data |

## Troubleshooting

### Authentication Issues

#### Reauthentication

If your credentials expire or change, Home Assistant will automatically prompt you to reauthenticate:

1. Go to **Settings** → **Devices & Services**
2. Look for **"Action Required"** or **"Configuration Required"** message on the integration
3. Click **"Reconfigure"** or follow the prompt
4. Complete a new magic-link login (or paste fresh tokens)
5. Click Submit

The integration will automatically resume normal operation with the new tokens.

#### Manual Credential Update

You can also reconfigure at any time without waiting for an error:

1. Go to **Settings** → **Devices & Services**
2. Find **HelloFresh**
3. Click the **3 dots menu** → **Reconfigure**
4. Update email/country and complete magic-link confirmation
5. Click Submit

#### Connection Status

Monitor your connection status with the **API Connection** binary sensor:

- **On** (Connected): Integration is receiving data normally
- **Off** (Disconnected): Connection lost or authentication failed
  - Check the binary sensor attributes for diagnostic information
  - Verify credentials if authentication failed
  - Check network connectivity

### Enable Debug Logging

To enable debug logging for this integration, add the following to your `configuration.yaml`:

```yaml
logger:
  default: info
  logs:
    custom_components.hellofresh: debug
```

### Common Issues

#### Authentication Errors

If you receive authentication errors:

1. Verify your username and password are correct
2. Check that your account has the necessary permissions
3. Wait for the automatic reauthentication prompt, or manually reconfigure
4. Check the API Connection binary sensor for status

#### Device Not Responding

If your device is not responding:

1. Check the **API Connection** binary sensor - it should be "On"
2. Check your network connection
3. Verify the device is powered on
4. Check the integration diagnostics (Settings → Devices & Services → HelloFresh → 3 dots → Download diagnostics)

## 🤝 Contributing

Contributions are welcome! Please open an issue or pull request if you have suggestions or improvements.

You have two options to set up a development environment — expand below for full details.

<details>
<summary><strong>Development Setup</strong></summary>

Both options provide the same fully-configured environment with Home Assistant, Python 3.14, Node.js LTS, and all necessary tools.

### Option 1: GitHub Codespaces (Recommended) ☁️

Develop directly in your browser without installing anything locally!

1. Click the green **"Code"** button in this repository
2. Switch to the **"Codespaces"** tab
3. Click **"Create codespace on main"**
4. **Wait for setup** (2-3 minutes first time) — everything installs automatically
5. **Review and commit** your changes in the Source Control panel (`Ctrl+Shift+G`)

> [!TIP]
> Codespaces gives you **60 hours/month free** for personal accounts. When you start Home Assistant (`script/develop`), port 8123 forwards automatically.

### Option 2: Local Development with VS Code 💻

#### Prerequisites

You'll need these installed locally:

- **A Docker-compatible container engine** — see options by platform:

  | Option                                                                                                                   | 🍎 macOS | 🐧 Linux | 🪟 Windows | Notes                                                                                                                                                                                                                                     |
  | ------------------------------------------------------------------------------------------------------------------------ | :------: | :------: | :--------: | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
  | [Docker Desktop](https://www.docker.com/products/docker-desktop/)                                                        |    ✅    |    ✅    |     ✅     | **Easiest starting point for all platforms.** GUI-based, well-documented, one installer. Uses WSL2 as default backend on Windows (Hyper-V also available). Installation requires admin rights; daily use does not. Free for personal use. |
  | [OrbStack](https://orbstack.dev/) ⭐                                                                                     |    ✅    |    —     |     —      | **Recommended for macOS** once Docker Desktop feels slow. Starts in ~2s, much lighter on RAM/CPU, full Docker API compatibility. Free for personal use.                                                                                   |
  | [Docker CE](https://docs.docker.com/engine/install/) (native) ⭐                                                         |    —     |    ✅    |     —      | **Recommended for Linux.** Install directly via your package manager — no VM, no GUI, no overhead. Free.                                                                                                                                  |
  | [WSL2](https://learn.microsoft.com/windows/wsl/install) + [Docker CE](https://docs.docker.com/engine/install/ubuntu/) ⭐ |    —     |    —     |     ✅     | **Recommended for Windows** once you're comfortable with WSL2. Docker runs natively inside WSL2 — no GUI overhead. Requires one-time WSL2 setup. Free.                                                                                    |
  | [Rancher Desktop](https://rancherdesktop.io/)                                                                            |    ✅    |    ✅    |     ✅     | Open source by SUSE. GUI-based, uses WSL2 on Windows. Good alternative to Docker Desktop. Free.                                                                                                                                           |
  | [Colima](https://github.com/abiosoft/colima)                                                                             |    ✅    |    ✅    |     —      | CLI-only, very lightweight. Good for terminal-focused workflows. Free.                                                                                                                                                                    |

- **VS Code** with the [Dev Containers extension](https://marketplace.visualstudio.com/items?itemName=ms-vscode-remote.remote-containers)
- **Git** — macOS and Linux usually have it already; see below if not, or to get a newer version:
  - **🍎 macOS:** The system Git (`xcode-select --install`) works fine. Recommended: `brew install git` ([Homebrew](https://brew.sh/)) for a current version.
  - **🐧 Linux:** Usually pre-installed. If not: `sudo apt install git` (or your distro's equivalent).
  - **🪟 Windows + WSL2 ⭐:** Install Git _inside WSL2_ with `sudo apt install git`. Git on Windows itself is not needed — VS Code clones and operates entirely within WSL2.
  - **🪟 Windows + Docker Desktop:** Install via `winget install Git.Git` or download [Git for Windows](https://git-scm.com/download/win).
- **Hardware** — the devcontainer runs a full Home Assistant instance including Python tooling:

  |          | Minimum    | Recommended                           |
  | -------- | ---------- | ------------------------------------- |
  | **RAM**  | 8 GB       | 16 GB or more                         |
  | **CPU**  | 4 cores    | 8 cores or more                       |
  | **Disk** | 10 GB free | 20 GB free (SSD strongly recommended) |

> [!TIP]
> **Not sure which Docker option to pick?** Start with [Docker Desktop](https://www.docker.com/products/docker-desktop/) — it works on all platforms, has a GUI, and needs no extra setup. The ⭐ options are faster alternatives once you're comfortable. macOS and Linux offer the best devcontainer experience — containers run with no extra VM layer and file I/O is fast. Windows works well too; this integration uses named container volumes (files live inside WSL2, not on the Windows drive) to keep performance acceptable.

> [!NOTE]
> **New to Dev Containers?** See the [VS Code Dev Containers documentation](https://code.visualstudio.com/docs/devcontainers/containers#_system-requirements) for system requirements and how to install the extension. **Once the extension is installed, you're done** — this repository already ships a complete devcontainer configuration. You don't need to follow the rest of the VS Code guide; the setup steps below are all that's needed.

#### Setup Steps

1. **Clone in a Dev Container:**

   **🍎 macOS / 🐧 Linux:** Clone the repository and open the folder in VS Code → click **"Reopen in Container"** when prompted (or `F1` → **"Dev Containers: Reopen in Container"**).

   **🪟 Windows:** In VS Code, press `F1` → **"Dev Containers: Clone Repository in Named Container Volume..."** and enter the repository URL. This keeps files inside WSL2 for best I/O performance.

2. Wait for the container to build (2-3 minutes first time)

3. **Review and commit** changes in Source Control (`Ctrl+Shift+G`)

4. **Start developing**:

   ```bash
   script/develop  # Home Assistant runs at http://localhost:8123
   ```

> [!NOTE]
> Both Codespaces and local DevContainer provide the exact same experience. The only difference is where the container runs (GitHub's cloud vs. your machine).

</details>

---

## 🤖 AI-Assisted Development

> [!NOTE]
> **Transparency Notice:** This integration was developed with assistance from AI coding agents (GitHub Copilot, Claude, and others). While the codebase follows Home Assistant Core standards, AI-generated code may not be reviewed or tested to the same extent as manually written code. AI tools were used to generate boilerplate code, implement standard integration features (config flow, coordinator, entities), ensure code quality and type safety, and write documentation. If you encounter unexpected behavior, please [open an issue](../../issues) on GitHub.
>
> _This section can be removed or modified if AI assistance was not used in your integration's development._

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

**Made with ❤️ by [@pantherale0][user_profile]**

---

[commits-shield]: https://img.shields.io/github/commit-activity/y/pantherale0/ha-hellofresh.svg?style=for-the-badge
[commits]: https://github.com/pantherale0/ha-hellofresh/commits/main
[hacs]: https://github.com/hacs/integration
[hacsbadge]: https://img.shields.io/badge/HACS-Default-orange.svg?style=for-the-badge
[license-shield]: https://img.shields.io/github/license/pantherale0/ha-hellofresh.svg?style=for-the-badge
[maintenance-shield]: https://img.shields.io/badge/maintainer-%40pantherale0-blue.svg?style=for-the-badge
[releases-shield]: https://img.shields.io/github/release/pantherale0/ha-hellofresh.svg?style=for-the-badge
[releases]: https://github.com/pantherale0/ha-hellofresh/releases
[user_profile]: https://github.com/pantherale0
