"""
navigator.py — Navigation intent detection and path resolution for ShellSpark.

Handles directory navigation queries by detecting intent and resolving paths.
Outputs shell code (cd commands) for shell integration.
"""

import os
import platform
import re
from pathlib import Path
from typing import Optional


NAVIGATION_PATTERNS = [
    r"^go\s+back$",
    r"^go\s+up$",
    r"^go\s+up\s+one\s+directory$",
    r"^back$",
    r"^up$",
    r"^up\s+one\s+directory$",
    r"^previous\s+directory$",
    r"^go\s+(?:to|into)\s+",
    r"^cd\s+(?:into|to|in)\s+",
    r"^change\s+(?:directory|dir)\s+(?:to|into)?\s*",
    r"^switch\s+to\s+",
    r"^navigate\s+to\s+",
    r"^open\s+(?:the\s+)?(\w+)\s+(?:folder|directory)",
    r"^enter\s+",
    r"^jump\s+to\s+",
    r"^move\s+to\s+",
]


COMMON_DIRECTORIES = {
    "desktop": "~/Desktop",
    "downloads": "~/Downloads",
    "documents": "~/Documents",
    "home": "~",
    "root": "/",
    "tmp": "/tmp",
    "temp": "/tmp",
}

WINDOWS_COMMON_DIRECTORIES = {
    "desktop": "~/Desktop",
    "downloads": "~/Downloads",
    "documents": "~/Documents",
    "home": "~",
    "profile": "~",
    "temp": "~\\AppData\\Local\\Temp",
    "tmp": "~\\AppData\\Local\\Temp",
    "program files": "C:\\Program Files",
    "program files (x86)": "C:\\Program Files (x86)",
    "appdata": "~/AppData/Roaming",
    "localappdata": "~/AppData/Local",
}


def _is_windows() -> bool:
    """Check if running on Windows (native, not WSL)."""
    return platform.system() == "Windows"


def is_navigation_query(query: str) -> bool:
    """
    Determine if the query is primarily about directory navigation.
    Uses lightweight heuristic pattern matching.
    """
    query_lower = query.lower().strip()

    for pattern in NAVIGATION_PATTERNS:
        if re.search(pattern, query_lower):
            return True

    return False


def _is_back_up_query(query: str) -> bool:
    """
    Check if the query is asking to go back/up in directory hierarchy.
    """
    query_lower = query.lower().strip()
    back_up_patterns = [
        r"^go\s+back$",
        r"^go\s+up$",
        r"^go\s+up\s+one\s+directory$",
        r"^back$",
        r"^up$",
        r"^up\s+one\s+directory$",
        r"^previous\s+directory$",
    ]
    return any(re.search(p, query_lower) for p in back_up_patterns)


def _extract_location(query: str) -> str:
    """
    Extract the directory/folder name from the query after removing navigation phrases.
    """
    query_lower = query.lower().strip()

    open_match = re.match(
        r"^open\s+(?:the\s+)?(\w+)\s+(?:folder|directory)$", query_lower
    )
    if open_match:
        return open_match.group(1)

    patterns_to_remove = [
        r"^go\s+(?:to|into)\s+",
        r"^cd\s+(?:into|to|in)\s+",
        r"^change\s+(?:directory|dir)\s+(?:to|into)?\s*",
        r"^switch\s+to\s+",
        r"^navigate\s+to\s+",
        r"^enter\s+",
        r"^jump\s+to\s+",
        r"^move\s+to\s+",
    ]

    location = query_lower
    for pattern in patterns_to_remove:
        location = re.sub(pattern, "", location, flags=re.IGNORECASE)

    return location.strip().strip("\"'")


def _resolve_path(location: str) -> Optional[str]:
    """
    Resolve the extracted location to an absolute filesystem path.
    Returns None if the path cannot be determined confidently.
    """
    if not location:
        return None

    location_lower = location.lower()

    if _is_windows():
        if location_lower in WINDOWS_COMMON_DIRECTORIES:
            return os.path.expanduser(WINDOWS_COMMON_DIRECTORIES[location_lower])
    else:
        if location_lower in COMMON_DIRECTORIES:
            return os.path.expanduser(COMMON_DIRECTORIES[location_lower])

    home = Path.home()

    search_dirs = [
        home,
        home / "Desktop",
        home / "Downloads",
        home / "Documents",
        home / "Documents" / "Projects",
        home / "workspace",
        home / "code",
        home / "projects",
        Path.cwd(),
        Path.cwd().parent,
    ]

    for base in search_dirs:
        if base.is_dir():
            potential = base / location
            if potential.is_dir():
                return str(potential.resolve())
            try:
                for item in base.iterdir():
                    if item.is_dir() and item.name.lower() == location_lower:
                        return str(item.resolve())
            except PermissionError:
                continue

    return None


def resolve_navigation_command(query: str) -> str:
    """
    Resolve a navigation query to a shell command.
    Returns shell code: "cd <path>", "cd ..", or "UNKNOWN"
    """
    if _is_back_up_query(query):
        return "cd .."

    location = _extract_location(query)

    if not location:
        return "UNKNOWN"

    path = _resolve_path(location)

    if path is None:
        return "UNKNOWN"

    return f"cd {path}"
