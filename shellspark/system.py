"""
system.py — OS and package manager detection for ShellSpark.
"""

import platform
import subprocess

PACKAGE_MANAGERS: dict[str, str] = {
    # Debian/Ubuntu family
    "ubuntu": "apt",       "debian": "apt",      "linuxmint": "apt",
    "pop": "apt",          "elementary": "apt",  "kali": "apt",
    "raspbian": "apt",     "zorin": "apt",
    # Red Hat family
    "fedora": "dnf",       "centos": "yum",      "rhel": "yum",
    "rocky": "dnf",        "almalinux": "dnf",   "ol": "yum",
    # Arch family
    "arch": "pacman",      "manjaro": "pacman",
    "endeavouros": "pacman", "garuda": "pacman",
    # SUSE
    "opensuse": "zypper",  "opensuse-leap": "zypper",
    "opensuse-tumbleweed": "zypper",
    # Others
    "alpine": "apk",       "void": "xbps",       "gentoo": "emerge",
    "nixos": "nix",        "solus": "eopkg",
    # macOS / Windows
    "macos": "brew",       "windows": "winget",
}


def get_distro_info() -> tuple[str, str]:
    """Return (distro_name, distro_id) for the current OS."""
    system = platform.system()

    if system == "Darwin":
        return "macOS", "macos"

    if system == "Windows":
        return "Windows", "windows"

    if system == "Linux":
        # Primary source: /etc/os-release
        try:
            info: dict[str, str] = {}
            with open("/etc/os-release") as f:
                for line in f:
                    line = line.strip()
                    if "=" in line:
                        k, _, v = line.partition("=")
                        info[k] = v.strip('"')
            return info.get("NAME", "Linux"), info.get("ID", "linux").lower()
        except OSError:
            pass

        # Fallback: lsb_release
        try:
            out = subprocess.check_output(
                ["lsb_release", "-si"], text=True, stderr=subprocess.DEVNULL
            ).strip().lower()
            return out.capitalize(), out
        except (FileNotFoundError, subprocess.CalledProcessError):
            pass

    return system or "Linux", (system or "linux").lower()


def get_package_manager(distro_id: str) -> str:
    """Map a distro ID to its package manager. Returns 'unknown' if not found."""
    return PACKAGE_MANAGERS.get(distro_id.lower(), "unknown")