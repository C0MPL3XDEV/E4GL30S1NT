<h1 align="center">E4GL30S1NT</h1>

<p align="center">
  <img src="https://github.com/C0MPL3XDEV/E4GL30S1NT/blob/main/image/imageonline-co-roundcorner.png" alt="E4GL30S1NT logo">
</p>

<p align="center">
  <a href="https://discord.gg/Vy8C724XWV">
    <img src="https://discordapp.com/api/guilds/437716353584070677/widget.png?style=shield" alt="Discord">
  </a>
  &nbsp;
  <img src="https://img.shields.io/badge/version-2.0.0-green?style=for-the-badge" alt="Version">
  &nbsp;
  <img src="https://img.shields.io/badge/python-3.11+-blue?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  &nbsp;
  <img src="https://img.shields.io/badge/license-GPL--3.0-red?style=for-the-badge" alt="License">
</p>

<p align="center">
  <img src="https://img.shields.io/github/stars/C0MPL3XDEV/E4GL30S1NT?style=social" alt="Stars">
  &nbsp;
  <img src="https://img.shields.io/github/forks/C0MPL3XDEV/E4GL30S1NT?style=social" alt="Forks">
  &nbsp;
  <img src="https://img.shields.io/github/issues/C0MPL3XDEV/E4GL30S1NT?color=yellow" alt="Issues">
  &nbsp;
  <img src="https://img.shields.io/github/last-commit/C0MPL3XDEV/E4GL30S1NT?color=blue" alt="Last Commit">
  &nbsp;
  <img src="https://img.shields.io/github/languages/code-size/C0MPL3XDEV/E4GL30S1NT" alt="Code size">
  &nbsp;
  <a href="https://github.com/C0MPL3XDEV/E4GL30S1NT/actions/workflows/ci.yml">
    <img src="https://github.com/C0MPL3XDEV/E4GL30S1NT/actions/workflows/ci.yml/badge.svg" alt="CI">
  </a>
</p>

<p align="center">
  <strong>Simple Information Gathering Toolkit</strong><br>
  A modular OSINT CLI — username recon, Facebook dumping, email discovery, phone lookup, network analysis, and more.
</p>

---

## Features

| Command | Description |
|---|---|
| `userrecon` | Username reconnaissance across 71 social platforms |
| `facedumper` | Dump Facebook friend list (IDs, emails, phones, birthdays, locations) |
| `mailfinder` | Discover email addresses from a person's name |
| `godorker` | Google dorking with automatic result scraping |
| `phoneinfo` | Phone number validation and carrier info |
| `dns` | DNS lookup for a domain or IP |
| `whois` | WHOIS lookup for a domain |
| `subnet` | Subnet / network calculator |
| `hostfinder` | Find hosts for a domain |
| `dnsfinder` | DNS finder via MTR |
| `riplookup` | Reverse IP lookup |
| `iplocation` | IP address geolocation |
| `bitly` | Resolve and bypass Bitly short URLs |
| `github` | Dump GitHub user profile information |
| `tempmail` | Generate a temporary email address and monitor inbox |
| `settings` | Manage API keys and configuration |
| `update` | Update E4GL30S1NT to the latest version |

---

## Requirements

- Python **3.11+**
- `curl` (used by `iplocation` to detect local IP)
- `wget` (used by `update` command — Linux only)
- API keys for two optional features (see [API Keys](#api-keys))

---

### Linux

Supports **Debian / Ubuntu / Kali** (`apt`), **Arch-based** (`pacman`), and **Fedora-based** (`dnf`) systems. The script auto-detects your package manager.

```bash
wget https://raw.githubusercontent.com/C0MPL3XDEV/E4GL30S1NT/main/linuxinstall.sh
bash linuxinstall.sh
```

The script will:
1. Detect your package manager (apt / pacman / dnf)
2. Install system packages (`python3`, `python3-venv`, `libxml2`, `libxslt1.1`, `curl`, `git`)
3. Clone the repository to `~/.local/share/eagleosint`
4. Create a virtual environment and install the package
5. Add `eagleosint` and `e4gl` launchers to `/usr/local/bin`

### Manual (all platforms)

### Manual (all platforms)

```bash
git clone https://github.com/C0MPL3XDEV/E4GL30S1NT.git
cd E4GL30S1NT
curl -LsSf https://astral.sh/uv/install.sh | sh   # skip if uv already installed
uv tool install .
```

### Verify installation

```bash
eagleosint --help
```

---

## Usage

### Interactive menu

```bash
eagleosint
# or
e4gl
```

### Direct subcommands

```bash
eagleosint userrecon          # username recon
eagleosint facedumper         # Facebook dump
eagleosint mailfinder         # email finder
eagleosint godorker           # Google dork
eagleosint phoneinfo          # phone lookup
eagleosint dns                # DNS lookup
eagleosint whois              # WHOIS lookup
eagleosint subnet             # subnet calculator
eagleosint hostfinder         # host finder
eagleosint dnsfinder          # DNS finder
eagleosint riplookup          # reverse IP
eagleosint iplocation         # IP geolocation
eagleosint bitly              # Bitly bypass
eagleosint github             # GitHub lookup
eagleosint tempmail           # temporary email
eagleosint settings           # edit config
eagleosint update             # self-update
```

Each subcommand can also be invoked as `python -m eagleosint <command>`.

---

## API Keys

Two tools require free API keys. You will be prompted on first use; keys are stored in `~/.config/E4GL30S1NT/config.json`.

| Tool | Provider | Free tier |
|---|---|---|
| `mailfinder` | [isitarealemail.com](https://isitarealemail.com/) | Yes |
| `phoneinfo` | [veriphone.io](https://veriphone.io/) | Yes |

You can also set them via environment variables (no config file write needed):

```bash
export E4GL30S1NT_REALEMAIL_KEY="your-key-here"
export E4GL30S1NT_VERIPHONE_KEY="your-key-here"
```

Or edit them interactively:

```bash
eagleosint settings
```

---

## Configuration

The config file is created automatically at first run:

```
~/.config/E4GL30S1NT/config.json
```

The log file is written to:

```
~/.config/E4GL30S1NT/eagleosint.log
```

Log rotation is automatic (max 500 KB, 2 backups kept).

---

## Uninstall

**If installed via `linuxinstall.sh`:**

```bash
sudo rm /usr/local/bin/eagleosint /usr/local/bin/e4gl
rm -rf ~/.local/share/eagleosint
rm -rf ~/.config/E4GL30S1NT
```

**If installed manually via pip:**

```bash
pip uninstall eagleosint
rm -rf ~/.config/E4GL30S1NT
```

---

## Developer Setup

```bash
git clone https://github.com/C0MPL3XDEV/E4GL30S1NT.git
cd E4GL30S1NT
bash install_deps.sh
```

This will create a `.venv`, install in editable mode with test dependencies, and run the test suite.

### Running tests manually

```bash
source .venv/bin/activate
pytest -v
```

### Project structure

```
eagleosint/
  cli.py             ← click group, menus, settings, update
  config.py          ← paths, CONFIGS dict, logger, save_config()
  display.py         ← ANSI colors, LOGO, display_progress()
  session.py         ← shared requests.Session
  providers/
    bitly.py         ← bypass_bitly()
    facebook.py      ← Facebook class (facedumper)
    github.py        ← github_lookup()
    godorker.py      ← godorker()
    mailfinder.py    ← mailfinder(), check_email()
    network.py       ← iplocation(), infoga()
    phoneinfo.py     ← phoneinfo()
    tempmail.py      ← temp_mail_gen()
    userrecon.py     ← userrecon(), send_req()
tests/               ← offline unit tests (pytest + pytest-mock)
E4GL30S1NT.py        ← backward-compat shim
pyproject.toml       ← package metadata and entry points
```

---

## Disclaimer

This tool is intended for **educational and authorized security research purposes only**. Always obtain explicit permission before gathering information about individuals or systems. The authors are not responsible for any misuse.

---

## Contributing

1. Fork the repo and create a branch: `git checkout -b feat/your-feature`
2. Install dev dependencies: `bash install_deps.sh` (requires [uv](https://docs.astral.sh/uv/))
3. Make changes — one logical concern per commit
4. Ensure tests pass: `pytest -v`
5. Open a pull request against `main`

**Guidelines**
- Follow the existing module layout — new tools go in `eagleosint/providers/`
- Every new provider must have a matching `tests/test_<name>.py`
- No real network calls in tests — mock with `monkeypatch` or `unittest.mock`
- Keep `E4GL30S1NT.py` as a shim only — no logic there

---

## CI/CD

Every push and pull request runs the full test suite automatically via GitHub Actions.

[![CI](https://github.com/C0MPL3XDEV/E4GL30S1NT/actions/workflows/ci.yml/badge.svg)](https://github.com/C0MPL3XDEV/E4GL30S1NT/actions/workflows/ci.yml)

---

## Contributors

<a href="https://github.com/C0MPL3XDEV/E4GL30S1NT/graphs/contributors">
  <img src="https://contrib.rocks/image?repo=C0MPL3XDEV/E4GL30S1NT" alt="Contributors"/>
</a>

Want your name here? See [Contributing](#contributing).

---

## Credits

Copyright © 2024 — [**@C0MPL3XDEV**](https://github.com/C0MPL3XDEV) & [**@PoulDev**](https://github.com/PoulDev)