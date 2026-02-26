# ShellSpark

<p align="center">
  <img src="shellSparkLogo.png" alt="ShellSpark" width="200"/>
</p>

<p align="center">
  Your intelligent terminal companion that translates natural language into safe, distribution-specific shell commands.
</p>

<p align="center">
  <a href="https://pypi.org/project/shellspark/"><img src="https://img.shields.io/pypi/v/shellspark?color=blue" alt="PyPI"></a>
  <a href="https://python.org/downloads/"><img src="https://img.shields.io/pypi/pyversions/shellspark?color=green" alt="Python"></a>
  <a href="https://github.com/shellspark/shellspark/blob/main/LICENSE"><img src="https://img.shields.io/pypi/l/shellspark?color=orange" alt="License"></a>
  <a href="https://github.com/shellspark/shellspark/stargazers"><img src="https://img.shields.io/github/stars/shellspark?color=yellow" alt="Stars"></a>
</p>

---

## ✨ Features

### 🤖 Intelligent Command Generation
- **Natural Language Processing** — Type what you want in plain English
- **Groq API Powered** — Lightning-fast LLM technology for accurate command generation
- **Context-Aware** — Remembers conversation history for follow-up commands

### 🛡️ Safety First
- **Three-Tier Classification** — SAFE, WARNING, and BLOCKED command detection
- **"See Before You Run"** — Always shows commands for confirmation before execution
- **Destructive Command Blocking** — Prevents accidental system damage

### 🌐 Cross-Platform Support
- **Linux** — Full support for all major distributions (Ubuntu, Debian, Fedora, Arch, etc.)
- **macOS** — Native support with Homebrew integration
- **Windows** — PowerShell-first approach with winget package manager
- **WSL** — Automatically detected and handled as Linux

### 🧭 Smart Navigation
- **Shell Function Integration** — Directory changes persist in your shell session
- **Natural Navigation Commands** — "go to desktop", "go back", "open downloads folder"
- **Smart Path Resolution** — Only returns existing directories

### 🎨 Beautiful Terminal UI
- **Rich Library** — Colorful, structured output
- **Syntax Highlighting** — Generated commands beautifully formatted
- **Clear Status Indicators** — Safety classification at a glance

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         ShellSpark                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│   │   __main__   │───▶│   navigator  │───▶│     ai       │   │
│   │   (CLI)      │    │   (nav detection)   │   (Groq API) │   │
│   └──────────────┘    └──────────────┘    └──────────────┘   │
│          │                    │                    │            │
│          ▼                    ▼                    ▼            │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐   │
│   │     ui       │    │   safety    │    │   executor   │   │
│   │  (Rich)      │    │ (classifier)│    │  (run cmd)   │   │
│   └──────────────┘    └──────────────┘    └──────────────┘   │
│                              │                    │            │
│                              ▼                    ▼            │
│                     ┌──────────────┐    ┌──────────────┐       │
│                     │   system    │    │   history    │       │
│                     │ (OS detect) │    │  (context)   │       │
│                     └──────────────┘    └──────────────┘       │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Module Overview

| Module | Responsibility |
|--------|---------------|
| `__main__.py` | CLI entry point, command routing |
| `navigator.py` | Navigation intent detection & path resolution |
| `ai.py` | Groq API integration, command generation |
| `safety.py` | Command classification (SAFE/WARNING/BLOCKED) |
| `executor.py` | Command execution with confirmation |
| `system.py` | OS/distribution detection |
| `ui.py` | Rich-based terminal output |
| `history.py` | Conversation context storage |
| `chat.py` | Conversational queries handling |

---

## 📦 Installation

### Quick Install (Linux & macOS)

```bash
curl -sSL https://shellspark.dev/install | bash
```

### Manual Installation

```bash
git clone https://github.com/shellspark/shellspark.git
cd shellspark
pip install -e .
```

### Windows Installation

```powershell
# PowerShell
pip install shellspark
```

---

## ⚡ Quick Start

### Setup

1. Get a free Groq API key at [https://console.groq.com](https://console.groq.com)
2. Run `shellspark --config` to save your API key
3. Or set the `GROQ_API_KEY` environment variable

### Basic Usage

```bash
# Update your system
shellspark update my system

# Install software
shellspark install docker

# Find files
shellspark find files larger than 100MB

# Show disk usage
shellspark show disk usage by directory

# Compress folders
shellspark compress my-folder to tar.gz

# Kill processes
shellspark kill process using port 3000
```

### Navigation (Shell Integration)

For directory navigation to persist in your shell, add to your `.bashrc` or `.zshrc`:

```bash
# For Bash/Zsh
source /path/to/shellspark/shellspark/shellspark.sh
```

Then use natural navigation commands:

```bash
shellspark go to desktop
shellspark go back
shellspark open downloads folder
shellspark enter projects
```

---

## 🔧 Configuration Options

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help message |
| `--version, -v` | Show version |
| `--config` | Configure API key |
| `--model` | Show current AI model |
| `--history` | View command history |
| `--clear-history` | Clear command history |
| `--run <query>` | Generate and execute |
| `--dry-run <query>` | Generate only (default) |
| `--explain <query>` | Explain generated command |
| `--no-history <query>` | Run without context |

---

## 🔐 Safety Classification

ShellSpark classifies every command before execution:

| Level | Color | Behavior |
|-------|-------|----------|
| **SAFE** | 🟢 Green | Executable after confirmation |
| **WARNING** | 🟡 Yellow | Requires explicit "yes" confirmation |
| **BLOCKED** | 🔴 Red | Never executed automatically |

### Blocked Commands Include
- Recursive deletion of system directories (`rm -rf /`)
- Disk formatting operations
- Fork bombs and resource exhaustion
- Firewall disabling (in some contexts)

---

## 🖥️ Platform Support

### Linux Distributions
- **Debian/Ubuntu** — apt
- **Fedora/RHEL** — dnf/yum
- **Arch Linux** — pacman
- **openSUSE** — zypper
- **Alpine** — apk

### macOS
- **Homebrew** — brew

### Windows
- **PowerShell** — Default shell
- **winget** — Package manager

### WSL
- Automatically detected and treated as Linux

---

## 📁 Project Structure

```
shellspark/
├── shellspark/
│   ├── __main__.py      # CLI entry point
│   ├── ai.py            # Groq API integration
│   ├── chat.py          # Conversational queries
│   ├── config.py        # Configuration management
│   ├── executor.py      # Command execution
│   ├── explainer.py     # Command explanation
│   ├── history.py       # Conversation history
│   ├── logger.py        # Event logging
│   ├── navigator.py     # Navigation detection
│   ├── safety.py        # Safety classification
│   ├── system.py        # OS detection
│   ├── ui.py            # Terminal UI
│   └── shellspark.sh    # Shell integration
├── setup.py
├── requirements.txt
└── README.md
```

---

## 📋 Requirements

- **Python** 3.8+
- **Internet** connection (for Groq API)
- **Groq API key** (free at [console.groq.com](https://console.groq.com))

### Python Dependencies

- `requests` — HTTP client
- `rich` — Terminal styling

---

## 📜 License

MIT License — See [LICENSE](LICENSE) for details.

---

<div align="center">

Built with ❤️ using Groq API

</div>
