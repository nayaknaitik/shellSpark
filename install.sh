#!/bin/bash

set -e

INSTALL_DIR="${HOME}/.local/bin"
CONFIG_DIR="${HOME}/.shellspark"
REPO_URL="https://github.com/shellspark/shellspark.git"

BOLD='\033[1m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${BOLD}Installing ShellSpark...${NC}"

if command -v shellspark &> /dev/null; then
    echo -e "${YELLOW}ShellSpark is already installed!${NC}"
    read -p "Reinstall? [y/N]: " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 0
    fi
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    echo -e "${GREEN}Detected macOS${NC}"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    echo -e "${GREEN}Detected Linux${NC}"
else
    echo -e "${YELLOW}Unknown OS: $OSTYPE${NC}"
fi

if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Python 3 is required but not installed.${NC}"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo -e "Python version: ${PYTHON_VERSION}"

echo "Creating installation directory..."
mkdir -p "${INSTALL_DIR}"

echo "Installing ShellSpark..."
TEMP_DIR=$(mktemp -d)
cd "${TEMP_DIR}"

git clone --depth 1 "${REPO_URL}" shellspark_tmp 2>/dev/null || {
    echo -e "${YELLOW}Git clone failed. Creating package manually...${NC}"
    mkdir -p shellspark_tmp/shellspark
    cat > shellspark_tmp/shellspark/__init__.py << 'PKGINIT'
__version__ = "1.0.0"
PKGINIT
    cat > shellspark_tmp/shellspark/__main__.py << 'PKGMAIN'
#!/usr/bin/env python3

import sys
import os
import subprocess
import json
import platform
import requests
from pathlib import Path

VERSION = "1.0.0"
CONFIG_DIR = Path.home() / ".shellspark"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_DIR = CONFIG_DIR / "logs"

def ensure_config_dir():
    CONFIG_DIR.mkdir(exist_ok=True)
    LOG_DIR.mkdir(exist_ok=True)

def get_distro_info():
    system = platform.system()
    if system == "Darwin":
        return "macOS", "macOS"
    elif system == "Linux":
        try:
            with open("/etc/os-release", "r") as f:
                lines = f.readlines()
                distro_info = {}
                for line in lines:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        distro_info[key] = value.strip('"')
                distro_name = distro_info.get("NAME", "Linux")
                distro_id = distro_info.get("ID", "linux")
                return distro_name, distro_id
        except:
            return "Linux", "linux"
    else:
        return system, system.lower()

def get_package_manager(distro_id):
    package_managers = {
        "ubuntu": "apt", "debian": "apt", "fedora": "dnf",
        "centos": "yum", "rhel": "yum", "arch": "pacman",
        "manjaro": "pacman", "opensuse": "zypper", "alpine": "apk",
    }
    return package_managers.get(distro_id.lower(), "unknown")

def load_config():
    if CONFIG_FILE.exists():
        with open(CONFIG_FILE, "r") as f:
            return json.load(f)
    return {}

def save_config(config):
    ensure_config_dir()
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f, indent=2)

def setup_api_key():
    print("\n\U0001F511 Groq API Key Setup")
    print("=" * 50)
    print("\nTo use ShellSpark, you need a Groq API key.")
    print("Get one for free at: https://console.groq.com\n")
    api_key = input("Enter your Groq API key: ").strip()
    if api_key:
        config = load_config()
        config["api_key"] = api_key
        save_config(config)
        print("\n\U0001F514 API key saved successfully!")
        return api_key
    else:
        print("\n\U0001F6AB No API key provided.")
        sys.exit(1)

def get_api_key():
    config = load_config()
    api_key = config.get("api_key")
    if not api_key:
        api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        print("\n\U0001F6AB No API key found.")
        return setup_api_key()
    return api_key

def generate_command(query, distro_name, distro_id, package_manager, api_key):
    system_prompt = f"""You are a bash command generator. Given a natural language request, generate the appropriate bash command.

System Information:
- OS: {distro_name} ({distro_id})
- Package Manager: {package_manager}

Rules:
1. Return ONLY the bash command, no explanations
2. Use the appropriate package manager for the detected distribution
3. For system updates on apt-based systems, use: sudo apt update && sudo apt upgrade -y
4. For system updates on dnf-based systems, use: sudo dnf update -y
5. For system updates on pacman-based systems, use: sudo pacman -Syu
6. Make commands safe and include necessary flags
7. If the command requires sudo, include it
8. Return only executable bash commands, no markdown formatting
9. If multiple commands are needed, chain them with && or ;
10. Be concise and practical

Generate the bash command for the following request:"""

    try:
        response = requests.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
            },
            json={
                "model": "openai/gpt-oss-120b",
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": query}
                ],
                "temperature": 0.3,
                "max_tokens": 500,
            },
            timeout=30
        )
        if response.status_code == 200:
            data = response.json()
            command = data["choices"][0]["message"]["content"].strip()
            command = command.replace("```bash", "").replace("```", "").strip()
            return command
        elif response.status_code == 401:
            print("\n\U0001F6AB Invalid API key.")
            sys.exit(1)
        else:
            print(f"\n\U0001F6AB API Error: {response.status_code}")
            sys.exit(1)
    except requests.exceptions.Timeout:
        print("\n\U0001F6AB Request timed out.")
        sys.exit(1)
    except Exception as e:
        print(f"\n\U0001F6AB Error: {str(e)}")
        sys.exit(1)

def confirm_execution(command):
    print("\n" + "=" * 60)
    print("\U0001F50D Generated Command:")
    print("=" * 60)
    print(f"\n  {command}\n")
    print("=" * 60)
    response = input("\nExecute this command? [Y/n]: ").strip().lower()
    return response in ["", "y", "yes"]

def execute_command(command):
    try:
        result = subprocess.run(command, shell=True, check=False, text=True)
        return result.returncode
    except KeyboardInterrupt:
        print("\n\n\U0001F6AB Command cancelled.")
        return 130
    except Exception as e:
        print(f"\n\U0001F6AB Error: {str(e)}")
        return 1

def show_help():
    print(f"""
\U0001F4BB ShellSpark v{VERSION}
   Your Intelligent Terminal Companion

USAGE:
  shellspark [options] <natural language command>

OPTIONS:
  --help, -h        Show help
  --version, -v     Show version
  --config          Update API key

EXAMPLES:
  shellspark update my system
  shellspark install docker
  shellspark find files larger than 100MB
""")

def main():
    ensure_config_dir()
    if len(sys.argv) < 2:
        show_help()
        sys.exit(0)
    if sys.argv[1] in ["--help", "-h"]:
        show_help()
        sys.exit(0)
    if sys.argv[1] in ["--version", "-v"]:
        print(f"ShellSpark v{VERSION}")
        sys.exit(0)
    if sys.argv[1] == "--config":
        setup_api_key()
        sys.exit(0)

    query = " ".join(sys.argv[1:])
    distro_name, distro_id = get_distro_info()
    package_manager = get_package_manager(distro_id)

    print(f"\n\U0001F50D System: {distro_name}")
    print(f"\U0001F4E6 Package Manager: {package_manager}")
    print(f"\U0001F914 Query: \"{query}\"")
    print("\n\u23F3 Generating command...")

    api_key = get_api_key()
    command = generate_command(query, distro_name, distro_id, package_manager, api_key)

    if confirm_execution(command):
        print("\n\U0001F680 Executing...\n")
        return_code = execute_command(command)
        print(f"\n{'✅' if return_code == 0 else '⚠️'} Exit code: {return_code}")
        sys.exit(return_code)
    else:
        print("\n\U0001F6AB Cancelled.")
        sys.exit(0)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\U0001F44B Goodbye!")
        sys.exit(130)
PKGMAIN
}

cd shellspark_tmp
pip install --user -e . 2>/dev/null || pip install --user requests 2>/dev/null || pip install -e . --break-system-packages 2>/dev/null || pip install requests --break-system-packages

if [ -f "${TEMP_DIR}/shellspark_tmp/shellspark/__main__.py" ]; then
    cp "${TEMP_DIR}/shellspark_tmp/shellspark/__main__.py" "${INSTALL_DIR}/shellspark"
    chmod +x "${INSTALL_DIR}/shellspark"
fi

rm -rf "${TEMP_DIR}"

if [[ ":$PATH:" != *":${INSTALL_DIR}:"* ]]; then
    echo ""
    echo -e "${YELLOW}Add this to your ~/.bashrc or ~/.zshrc:${NC}"
    echo "  export PATH=\"\${HOME}/.local/bin:\$PATH\""
fi

echo ""
echo -e "${GREEN}✅ ShellSpark installed successfully!${NC}"
echo ""
echo "Run 'shellspark --help' to get started."
echo "You'll be prompted for a Groq API key on first run."
echo "Get your free key at: https://console.groq.com"
echo ""
