"""
intent.py — Intent classification and deterministic command resolution for ShellSpark.

Provides:
- Intent type detection (INSTALL, NAVIGATE, DELETE, GENERIC)
- Deterministic resolution for known package names
- Fallback to AI when deterministic resolution is not possible
"""

import re
from enum import Enum
from typing import Optional


class IntentType(Enum):
    INSTALL = "install"
    NAVIGATE = "navigate"
    DELETE = "delete"
    EXPLAIN = "explain"     
    GENERIC = "generic"


KNOWN_PACKAGES = {
    "docker": {
        "apt": "sudo apt install docker.io",
        "dnf": "sudo dnf install docker",
        "pacman": "sudo pacman -S docker",
        "apk": "sudo apk add docker",
        "zypper": "sudo zypper install docker",
        "brew": "brew install docker",
        "winget": "winget install Docker.DockerDesktop",
    },
    "nginx": {
        "apt": "sudo apt install nginx",
        "dnf": "sudo dnf install nginx",
        "pacman": "sudo pacman -S nginx",
        "apk": "sudo apk add nginx",
        "zypper": "sudo zypper install nginx",
        "brew": "brew install nginx",
        "winget": "winget install Nginx.Nginx",
    },
    "node": {
        "apt": "sudo apt install nodejs npm",
        "dnf": "sudo dnf install nodejs npm",
        "pacman": "sudo pacman -S nodejs npm",
        "apk": "sudo apk add nodejs npm",
        "zypper": "sudo zypper install nodejs npm",
        "brew": "brew install node",
        "winget": "winget install OpenJS.NodeJS",
    },
    "python": {
        "apt": "sudo apt install python3 python3-pip",
        "dnf": "sudo dnf install python3 python3-pip",
        "pacman": "sudo pacman -S python python-pip",
        "apk": "sudo apk add python3 py3-pip",
        "zypper": "sudo zypper install python3 python3-pip",
        "brew": "brew install python",
        "winget": "winget install Python.Python.3.11",
    },
    "git": {
        "apt": "sudo apt install git",
        "dnf": "sudo dnf install git",
        "pacman": "sudo pacman -S git",
        "apk": "sudo apk add git",
        "zypper": "sudo zypper install git",
        "brew": "brew install git",
        "winget": "winget install Git.Git",
    },
    "vim": {
        "apt": "sudo apt install vim",
        "dnf": "sudo dnf install vim",
        "pacman": "sudo pacman -S vim",
        "apk": "sudo apk add vim",
        "zypper": "sudo zypper install vim",
        "brew": "brew install vim",
        "winget": "winget install Vim.Vim",
    },
    "curl": {
        "apt": "sudo apt install curl",
        "dnf": "sudo dnf install curl",
        "pacman": "sudo pacman -S curl",
        "apk": "sudo apk add curl",
        "zypper": "sudo zypper install curl",
        "brew": "brew install curl",
        "winget": "winget install curl.curl",
    },
    "wget": {
        "apt": "sudo apt install wget",
        "dnf": "sudo dnf install wget",
        "pacman": "sudo pacman -S wget",
        "apk": "sudo apk add wget",
        "zypper": "sudo zypper install wget",
        "brew": "brew install wget",
        "winget": "winget install wget",
    },
    "tmux": {
        "apt": "sudo apt install tmux",
        "dnf": "sudo dnf install tmux",
        "pacman": "sudo pacman -S tmux",
        "apk": "sudo apk add tmux",
        "zypper": "sudo zypper install tmux",
        "brew": "brew install tmux",
        "winget": "winget install tmux.tmp",
    },
    "htop": {
        "apt": "sudo apt install htop",
        "dnf": "sudo dnf install htop",
        "pacman": "sudo pacman -S htop",
        "apk": "sudo apk add htop",
        "zypper": "sudo zypper install htop",
        "brew": "brew install htop",
        "winget": "winget install htop.htop",
    },
    "jq": {
        "apt": "sudo apt install jq",
        "dnf": "sudo dnf install jq",
        "pacman": "sudo pacman -S jq",
        "apk": "sudo apk add jq",
        "zypper": "sudo zypper install jq",
        "brew": "brew install jq",
        "winget": "winget install jq.jq",
    },
    "yarn": {
        "apt": "sudo apt install yarn",
        "dnf": "sudo dnf install yarn",
        "pacman": "sudo pacman -S yarn",
        "apk": "sudo apk add yarn",
        "zypper": "sudo zypper install yarn",
        "brew": "brew install yarn",
        "winget": "winget install Yarn.Yarn",
    },
    "postgres": {
        "apt": "sudo apt install postgresql postgresql-contrib",
        "dnf": "sudo dnf install postgresql-server",
        "pacman": "sudo pacman -S postgresql",
        "apk": "sudo apk add postgresql postgresql-client",
        "zypper": "sudo zypper install postgresql-server",
        "brew": "brew install postgresql",
        "winget": "winget install PostgreSQL.PostgreSQL",
    },
    "mysql": {
        "apt": "sudo apt install mysql-server",
        "dnf": "sudo dnf install mysql-server",
        "pacman": "sudo pacman -S mariadb",
        "apk": "sudo apk add mysql mysql-client",
        "zypper": "sudo zypper install mariadb mariadb-client",
        "brew": "brew install mysql",
        "winget": "winget install Oracle.MySQL",
    },
    "redis": {
        "apt": "sudo apt install redis-server",
        "dnf": "sudo dnf install redis",
        "pacman": "sudo pacman -S redis",
        "apk": "sudo apk add redis",
        "zypper": "sudo zypper install redis",
        "brew": "brew install redis",
        "winget": "winget install Redis.Redis",
    },
    "mongodb": {
        "apt": "sudo apt install mongodb",
        "dnf": "sudo dnf install mongodb",
        "pacman": "sudo pacman -S mongodb",
        "apk": "sudo apk add mongodb",
        "zypper": "sudo zypper install mongodb",
        "brew": "brew tap mongodb/brew && brew install mongodb-community",
        "winget": "winget install MongoDB.Server",
    },
    "golang": {
        "apt": "sudo apt install golang-go",
        "dnf": "sudo dnf install golang",
        "pacman": "sudo pacman -S go",
        "apk": "sudo apk add go",
        "zypper": "sudo zypper install go",
        "brew": "brew install go",
        "winget": "winget install GoLang.Go",
    },
    "rust": {
        "apt": "sudo apt install rustc cargo",
        "dnf": "sudo dnf install rust cargo",
        "pacman": "sudo pacman -S rust",
        "apk": "sudo apk add rust cargo",
        "zypper": "sudo zypper install rust cargo",
        "brew": "brew install rust",
        "winget": "winget install Rustlang.Rust.MSVC",
    },
    "java": {
        "apt": "sudo apt install default-jdk",
        "dnf": "sudo dnf install java-11-openjdk-devel",
        "pacman": "sudo pacman -S jdk",
        "apk": "sudo apk add openjdk17",
        "zypper": "sudo zypper install java-17-openjdk-devel",
        "brew": "brew install openjdk",
        "winget": "winget install Oracle.JavaSDK",
    },
    "gcc": {
        "apt": "sudo apt install build-essential",
        "dnf": "sudo dnf install gcc gcc-c++ make",
        "pacman": "sudo pacman -S base-devel",
        "apk": "sudo apk add gcc g++ make musl-dev",
        "zypper": "sudo zypper install -t pattern devel_basis",
        "brew": "brew install gcc",
        "winget": "winget install mingw-w64.gcc",
    },
    "make": {
        "apt": "sudo apt install make",
        "dnf": "sudo dnf install make",
        "pacman": "sudo pacman -S make",
        "apk": "sudo apk add make",
        "zypper": "sudo zypper install make",
        "brew": "brew install make",
        "winget": "winget install Gnu.Make",
    },
    "zip": {
        "apt": "sudo apt install zip unzip",
        "dnf": "sudo dnf install zip unzip",
        "pacman": "sudo pacman -S zip unzip",
        "apk": "sudo apk add zip unzip",
        "zypper": "sudo zypper install zip unzip",
        "brew": "brew install zip unzip",
        "winget": "winget install zip",
    },
    "tar": {
        "apt": "sudo apt install tar",
        "dnf": "sudo dnf install tar",
        "pacman": "sudo pacman -S tar",
        "apk": "sudo apk add tar",
        "zypper": "sudo zypper install tar",
        "brew": "brew install gnu-tar",
        "winget": "winget install gnu.tar",
    },
    "openssh": {
        "apt": "sudo apt install openssh-client openssh-server",
        "dnf": "sudo dnf install openssh-clients openssh-server",
        "pacman": "sudo pacman -S openssh",
        "apk": "sudo apk add openssh-client openssh-server",
        "zypper": "sudo zypper install openssh",
        "brew": "brew install openssh",
        "winget": "winget install OpenSSH.OpenSSH",
    },
    "ufw": {
        "apt": "sudo apt install ufw",
        "dnf": "sudo dnf install ufw",
        "pacman": "sudo pacman -S ufw",
        "apk": "sudo apk add ufw",
        "zypper": "sudo zypper install ufw",
        "brew": "brew install ufw",
        "winget": "winget install ufw",
    },
    "firewalld": {
        "apt": "sudo apt install firewalld",
        "dnf": "sudo dnf install firewalld",
        "pacman": "sudo pacman -S firewalld",
        "apk": "sudo apk add firewalld",
        "zypper": "sudo zypper install firewalld",
        "brew": "brew install firewalld",
        "winget": "winget install firewalld",
    },
    "zsh": {
        "apt": "sudo apt install zsh",
        "dnf": "sudo dnf install zsh",
        "pacman": "sudo pacman -S zsh",
        "apk": "sudo apk add zsh",
        "zypper": "sudo zypper install zsh",
        "brew": "brew install zsh",
        "winget": "winget install zsh.zsh",
    },
    "fish": {
        "apt": "sudo apt install fish",
        "dnf": "sudo dnf install fish",
        "pacman": "sudo pacman -S fish",
        "apk": "sudo apk add fish",
        "zypper": "sudo zypper install fish",
        "brew": "brew install fish",
        "winget": "winget install fish.fish",
    },
    "powershell": {
        "apt": "sudo apt install powershell",
        "dnf": "sudo dnf install powershell",
        "pacman": "sudo pacman -S powershell",
        "apk": "sudo apk add powershell",
        "zypper": "sudo zypper install powershell",
        "brew": "brew install powershell",
        "winget": "winget install Microsoft.PowerShell",
    },
    "awscli": {
        "apt": "sudo apt install awscli",
        "dnf": "sudo dnf install awscli",
        "pacman": "sudo pacman -S aws-cli",
        "apk": "sudo apk add aws-cli",
        "zypper": "sudo zypper install aws-cli",
        "brew": "brew install awscli",
        "winget": "winget install Amazon.AWSCLI",
    },
    "terraform": {
        "apt": "sudo apt install terraform",
        "dnf": "sudo dnf install terraform",
        "pacman": "sudo pacman -S terraform",
        "apk": "sudo apk add terraform",
        "zypper": "sudo zypper install terraform",
        "brew": "brew install terraform",
        "winget": "winget install HashiCorp.Terraform",
    },
    "kubectl": {
        "apt": "sudo apt install kubectl",
        "dnf": "sudo dnf install kubectl",
        "pacman": "sudo pacman -S kubectl",
        "apk": "sudo apk add kubectl",
        "zypper": "sudo zypper install kubectl",
        "brew": "brew install kubectl",
        "winget": "winget install Kubernetes.kubectl",
    },
    "helm": {
        "apt": "sudo apt install helm",
        "dnf": "sudo dnf install helm",
        "pacman": "sudo pacman -S helm",
        "apk": "sudo apk add helm",
        "zypper": "sudo zypper install helm",
        "brew": "brew install helm",
        "winget": "winget install Helm.Helm",
    },
    "docker-compose": {
        "apt": "sudo apt install docker-compose",
        "dnf": "sudo dnf install docker-compose",
        "pacman": "sudo pacman -S docker-compose",
        "apk": "sudo apk add docker-compose",
        "zypper": "sudo zypper install docker-compose",
        "brew": "brew install docker-compose",
        "winget": "winget install Docker.DockerCompose",
    },
    "pip": {
        "apt": "sudo apt install python3-pip",
        "dnf": "sudo dnf install python3-pip",
        "pacman": "sudo pacman -S python-pip",
        "apk": "sudo apk add py3-pip",
        "zypper": "sudo zypper install python3-pip",
        "brew": "brew install pip",
        "winget": "winget install Python.Pip",
    },
    "npm": {
        "apt": "sudo apt install npm",
        "dnf": "sudo dnf install npm",
        "pacman": "sudo pacman -S npm",
        "apk": "sudo apk add npm",
        "zypper": "sudo zypper install npm",
        "brew": "brew install npm",
        "winget": "winget install OpenJS.NodeJS",
    },
    "yarn": {
        "apt": "sudo apt install yarn",
        "dnf": "sudo dnf install yarn",
        "pacman": "sudo pacman -S yarn",
        "apk": "sudo apk add yarn",
        "zypper": "sudo zypper install yarn",
        "brew": "brew install yarn",
        "winget": "winget install Yarn.Yarn",
    },
}


INSTALL_PATTERNS = [
    r"\binstall\b",
    r"\bsetup\b",
    r"\bget\b",
    r"\bdownload and install\b",
    r"\bset up\b",
    r"\badd\b",
    r"\benable\b",
]


DELETE_PATTERNS = [
    r"\bremove\b",
    r"\bdelete\b",
    r"\buninstall\b",
    r"\bpurge\b",
    r"\berase\b",
    r"\bclean\b",
    r"\bdrop\b",
    r"\btruncate\b",
    r"\bformat\b",
    r"\bwipe\b",
    r"\bremove\s+(all|old|unused|unused)\b",
]
EXPLAIN_PATTERNS = [
    r"\bexplain\b",
    r"\bwhat is\b",
    r"\bhow does\b",
    r"\bhow do\b",
    r"\bmeaning of\b",
    r"\bdefine\b",
]

def classify_intent(query: str) -> IntentType:
    query_lower = query.lower().strip()

    for pattern in DELETE_PATTERNS:
        if re.search(pattern, query_lower):
            return IntentType.DELETE

    for pattern in INSTALL_PATTERNS:
        if re.search(pattern, query_lower):
            return IntentType.INSTALL

    for pattern in EXPLAIN_PATTERNS:
        if re.search(pattern, query_lower):
            return IntentType.EXPLAIN

    return IntentType.GENERIC

def extract_install_target(query: str) -> Optional[str]:
    """
    Extract the package/software name from an install query.
    Returns None if no clear target can be extracted.
    """
    query_lower = query.lower().strip()

    remove_patterns = [
        r"\bhow (do I|to|can I)\b",
        r"\bplease\b",
        r"\bcan you\b",
        r"\bi want to\b",
        r"\bi need to\b",
        r"\b(to|for|on|with)\b",
        r"\b(the|this|that|my)\b",
    ]

    cleaned = query_lower
    for pattern in remove_patterns:
        cleaned = re.sub(pattern, " ", cleaned, flags=re.IGNORECASE)

    install_triggers = [
        r"\binstall\b",
        r"\bsetup\b",
        r"\bget\b",
        r"\bdownload and install\b",
        r"\bset up\b",
        r"\badd\b",
    ]

    for trigger in install_triggers:
        match = re.search(trigger + r"\s+(.+)", cleaned, re.IGNORECASE)
        if match:
            target = match.group(1).strip()
            target = re.sub(r"\s+", "", target)
            target = target.strip(".,;!?")
            if target and len(target) > 1:
                return target

    return None


def resolve_install_command(query: str, package_manager: str) -> Optional[str]:
    """
    Attempt deterministic resolution of an install query.
    Returns the command string if resolvable, or None if fallback to AI is needed.
    """
    if package_manager == "unknown":
        return None

    target = extract_install_target(query)
    if not target:
        return None

    target_lower = target.lower()

    if target_lower in KNOWN_PACKAGES:
        package_mapping = KNOWN_PACKAGES[target_lower]
        if package_manager in package_mapping:
            return package_mapping[package_manager]
        else:
            return None

    return None
