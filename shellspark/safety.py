"""
safety.py — Command safety classification engine for ShellSpark.

Classifies any shell command as SAFE, WARNING, or BLOCKED before execution.
Uses structured pattern matching — not just substring search.
"""

import re
from enum import Enum


class Risk(Enum):
    SAFE = "safe"
    WARNING = "warning"
    BLOCKED = "blocked"


class SafetyResult:
    def __init__(self, risk: Risk, reason: str = ""):
        self.risk = risk
        self.reason = reason

    @property
    def is_blocked(self) -> bool:
        return self.risk == Risk.BLOCKED

    @property
    def is_warning(self) -> bool:
        return self.risk == Risk.WARNING

    @property
    def is_safe(self) -> bool:
        return self.risk == Risk.SAFE

    def __repr__(self) -> str:
        return f"SafetyResult({self.risk.value}, {self.reason!r})"


# ── Blocked patterns ──────────────────────────────────────────────────────────
# Each entry is (compiled_regex, human_readable_reason).
# Regexes match against the full command string (case-insensitive).

_BLOCKED: list[tuple[re.Pattern, str]] = [
    # Recursive forced removal of root or critical dirs
    (
        re.compile(r"rm\s+.*-[a-zA-Z]*r[a-zA-Z]*f.*[\s/]*/\s*$"),
        "Recursive forced deletion of root filesystem (rm -rf /)",
    ),
    (
        re.compile(
            r"rm\s+.*-[a-zA-Z]*r[a-zA-Z]*f.*(/boot|/etc|/usr|/bin|/sbin|/lib)\b"
        ),
        "Recursive forced deletion of a critical system directory",
    ),
    # Disk/device-level operations
    (
        re.compile(r"\bdd\b.+of=/dev/(sd[a-z]|nvme|hd[a-z]|vd[a-z])\b"),
        "Raw disk write with dd — can wipe an entire drive",
    ),
    (re.compile(r"\bmkfs\b"), "mkfs formats a filesystem — destructive disk operation"),
    (
        re.compile(r"\bfdisk\b|\bparted\b|\bgdisk\b|\bcfdisk\b"),
        "Partition table modification",
    ),
    (re.compile(r"\bshred\b.+/dev/"), "Shredding a raw device"),
    # Fork bombs
    (re.compile(r":\s*\(\s*\)\s*\{.*:\|:"), "Fork bomb pattern detected"),
    (
        re.compile(r"while\s+true.*fork|while\s+1.*fork"),
        "Potential resource exhaustion loop",
    ),
    # Wiping commands
    (re.compile(r"\b(wipefs|blkdiscard)\b"), "Disk wipe command"),
    # Overwrite /dev/sda or similar directly
    (
        re.compile(r">\s*/dev/(sd[a-z]|nvme|hd[a-z]|vd[a-z])\b"),
        "Redirect output directly to a raw block device",
    ),
    # Chmod 777 on root or system dirs
    (re.compile(r"chmod\s+.*777\s+/\s*$"), "Making root filesystem world-writable"),
    # History wipe (anti-forensics)
    (
        re.compile(
            r"(rm|cat /dev/null\s*>)\s+~/?\.(bash_history|zsh_history|sh_history)"
        ),
        "Wiping shell history",
    ),
    # Kernel module tampering
    (
        re.compile(r"\brmmod\b.+(ext4|btrfs|xfs|overlay|nfs)\b"),
        "Removing a critical kernel filesystem module",
    ),
    # Windows-specific dangerous commands
    (
        re.compile(r"\bformat\b.*[a-zA-Z]:", re.IGNORECASE),
        "Windows format command — destructive disk operation",
    ),
    (
        re.compile(r"\bdiskpart\b.*\bclean\b", re.IGNORECASE),
        "Diskpart clean — erases all data on disk",
    ),
    (
        re.compile(r"\bdiskpart\b.*\bremove\s+disk\b", re.IGNORECASE),
        "Diskpart remove disk — removes dynamic disk",
    ),
    (
        re.compile(r"\breg\s+delete\b.*\b/s\b.*\b/f\b", re.IGNORECASE),
        "Registry forced deletion — can break system",
    ),
    (
        re.compile(
            r"\bRemove-Item\b.*-Recurse.*[A-Z]:\\(Windows|Program Files)", re.IGNORECASE
        ),
        "PowerShell recursive deletion of system directories",
    ),
    (
        re.compile(r"\brm\s+-rf\s+/", re.IGNORECASE),
        "Recursive forced deletion of root filesystem",
    ),
]

# ── Warning patterns ──────────────────────────────────────────────────────────

_WARNING: list[tuple[re.Pattern, str]] = [
    # rm with -rf on non-root paths (still risky)
    (
        re.compile(r"\brm\s+.*-[a-zA-Z]*r[a-zA-Z]*f\b"),
        "Recursive forced deletion — double-check the target path",
    ),
    # System shutdown/reboot
    (
        re.compile(r"\b(shutdown|reboot|poweroff|halt|init\s+0|init\s+6)\b"),
        "System shutdown or reboot",
    ),
    # Package removal
    (
        re.compile(
            r"\b(apt|dnf|yum|pacman|zypper|apk)\b.+\b(remove|purge|autoremove|erase|uninstall)\b"
        ),
        "Package removal — verify what will be uninstalled",
    ),
    # Package installation (Windows winget)
    (
        re.compile(r"\bwinget\b.+\b(install|upgrade)\b", re.IGNORECASE),
        "Windows package installation — verify the package name",
    ),
    # Package removal (Windows)
    (
        re.compile(r"\bwinget\b.+\b(uninstall|remove)\b", re.IGNORECASE),
        "Windows package removal — verify what will be uninstalled",
    ),
    # Killing all processes
    (
        re.compile(r"\bkillall\b|\bkill\s+-9\s+-1\b|\bpkill\s+-9\b"),
        "Terminating multiple processes",
    ),
    # Disabling firewall
    (
        re.compile(r"\b(ufw|firewalld|iptables)\b.+\b(disable|stop|flush|reset)\b"),
        "Disabling or resetting firewall rules",
    ),
    # Windows firewall
    (
        re.compile(r"\bSet-NetFirewallProfile\b.*-Enabled\s+False", re.IGNORECASE),
        "Disabling Windows firewall",
    ),
    # chmod/chown on system dirs
    (
        re.compile(r"(chmod|chown)\s+.+\s+/(etc|usr|bin|sbin|lib|boot)\b"),
        "Changing permissions/ownership on system directories",
    ),
    # Writing to /etc
    (re.compile(r"(>|tee)\s+/etc/"), "Writing to /etc — modifies system configuration"),
    # curl/wget piped to shell (supply chain risk)
    (
        re.compile(r"(curl|wget).+\|\s*(bash|sh|zsh|python|ruby|perl)"),
        "Piping remote content directly into a shell interpreter",
    ),
    # sudo su / sudo -s (privilege escalation to root shell)
    (re.compile(r"sudo\s+(su|bash|sh|zsh|-s)\b"), "Opening a root shell session"),
    # Crontab modification
    (
        re.compile(r"\bcrontab\b.+-[er]\b"),
        "Modifying crontab — affects scheduled tasks",
    ),
    # systemctl disable on critical services
    (
        re.compile(
            r"systemctl\s+(disable|mask|stop)\s+(ssh|sshd|networking|network|systemd-resolved)\b"
        ),
        "Stopping or disabling a critical system service",
    ),
    # Windows registry modification
    (
        re.compile(r"\breg\s+add\b|\breg\s+import\b", re.IGNORECASE),
        "Windows registry modification — can affect system behavior",
    ),
    # Windows Stop-Process
    (
        re.compile(r"\bStop-Process\b.*-Force\b", re.IGNORECASE),
        "Forcefully terminating Windows processes",
    ),
    # PowerShell execution policy bypass
    (
        re.compile(r"-ExecutionPolicy\b.*Bypass", re.IGNORECASE),
        "Bypassing PowerShell execution policy",
    ),
]


def classify(command: str) -> SafetyResult:
    """
    Analyse a shell command and return a SafetyResult.

    Order of precedence: BLOCKED > WARNING > SAFE
    """
    # Strip leading/trailing whitespace for cleaner matching
    cmd = command.strip()

    for pattern, reason in _BLOCKED:
        if pattern.search(cmd):
            return SafetyResult(Risk.BLOCKED, reason)

    for pattern, reason in _WARNING:
        if pattern.search(cmd):
            return SafetyResult(Risk.WARNING, reason)

    return SafetyResult(Risk.SAFE)


def display_safety(result: SafetyResult) -> None:
    """Print a user-facing safety notice for WARNING or BLOCKED results."""
    if result.is_blocked:
        print(f"\n🚫 BLOCKED: {result.reason}")
        print("   ShellSpark will not execute this command.")
        print("   If you need to run this, do it manually with full awareness.\n")

    elif result.is_warning:
        print(f"\n⚠️  WARNING: {result.reason}")
        print("   This command may have irreversible effects.\n")
