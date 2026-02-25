# ShellSpark

Your intelligent terminal companion that translates natural English commands into distribution-specific bash commands.

![ShellSpark](https://img.shields.io/badge/version-1.0.0-blue) ![Python](https://img.shields.io/badge/python-3.8+-green) ![License](https://img.shields.io/badge/license-MIT-orange)

## Features

- **Natural Language Processing** - Type what you want in plain English
- **Distro-Aware Commands** - Automatically detects your Linux distribution
- **Groq API Integration** - Powered by lightning-fast LLM technology
- **Safety First** - Shows commands for confirmation before execution
- **Cross-Platform** - Works on Linux and macOS

## Installation

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

## Setup

1. Get a free Groq API key at [https://console.groq.com](https://console.groq.com)
2. Run `shellspark --config` to save your API key
3. Or set the `GROQ_API_KEY` environment variable

## Usage

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

### Options

| Option | Description |
|--------|-------------|
| `--help, -h` | Show help message |
| `--version, -v` | Show version |
| `--config` | Update API key |

## Configuration

- Config file: `~/.shellspark/config.json`
- Logs: `~/.shellspark/logs/`

## How It Works

1. ShellSpark detects your OS and package manager
2. Sends your natural language query + system info to Groq API
3. Returns the generated bash command for your confirmation
4. Executes only after you approve

## Requirements

- Python 3.8+
- Internet connection (for Groq API)
- Groq API key (free at console.groq.com)

## License

MIT License - see LICENSE for details.

---

Built with \u2764\ufe0f using Groq API
