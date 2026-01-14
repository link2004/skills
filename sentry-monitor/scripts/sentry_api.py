#!/usr/bin/env python3
"""
Sentry API Client for CLI-based monitoring and debugging.

Usage:
    python3 sentry_api.py issues [--all] [--query QUERY] [--limit N]
    python3 sentry_api.py events [--period PERIOD] [--limit N]
    python3 sentry_api.py issue ISSUE_ID
    python3 sentry_api.py breadcrumbs ISSUE_ID
    python3 sentry_api.py user USER_EMAIL

Environment:
    SENTRY_AUTH_TOKEN: Required. API token from sentry.io/settings/auth-tokens/
"""

import argparse
import json
import os
import sys
import urllib.request
import urllib.error
from datetime import datetime, timezone
from typing import Any

# Configuration (set via environment variables)
ORG_SLUG = os.environ.get("SENTRY_ORG")
PROJECT_SLUG = os.environ.get("SENTRY_PROJECT")
BASE_URL = "https://sentry.io/api/0"


def check_config():
    """Validate required environment variables."""
    missing = []
    if not ORG_SLUG:
        missing.append("SENTRY_ORG")
    if not PROJECT_SLUG:
        missing.append("SENTRY_PROJECT")
    if missing:
        print(f"Error: Missing required environment variables: {', '.join(missing)}", file=sys.stderr)
        print("Set them in your shell config or environment", file=sys.stderr)
        sys.exit(1)


def get_auth_token() -> str:
    token = os.environ.get("SENTRY_AUTH_TOKEN")
    if not token:
        # Try to read from shell config files
        for config_file in ["~/.zshenv", "~/.bashrc", "~/.bash_profile"]:
            config_path = os.path.expanduser(config_file)
            if os.path.exists(config_path):
                with open(config_path, "r") as f:
                    for line in f:
                        if line.startswith("export SENTRY_AUTH_TOKEN="):
                            value = line.split("=", 1)[1].strip()
                            token = value.strip('"').strip("'")
                            break
                if token:
                    break
    if not token:
        print("Error: SENTRY_AUTH_TOKEN not found", file=sys.stderr)
        print("Set in shell config or environment variable", file=sys.stderr)
        sys.exit(1)
    return token


def api_request(endpoint: str, params: dict = None) -> Any:
    """Make authenticated request to Sentry API."""
    token = get_auth_token()
    url = f"{BASE_URL}{endpoint}"

    if params:
        query = "&".join(f"{k}={v}" for k, v in params.items() if v is not None)
        if query:
            url = f"{url}?{query}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {token}")
    req.add_header("Content-Type", "application/json")

    try:
        with urllib.request.urlopen(req, timeout=30) as response:
            return json.loads(response.read().decode())
    except urllib.error.HTTPError as e:
        error_body = e.read().decode() if e.fp else ""
        print(f"API Error {e.code}: {e.reason}", file=sys.stderr)
        if error_body:
            print(f"Details: {error_body}", file=sys.stderr)
        sys.exit(1)
    except urllib.error.URLError as e:
        print(f"Network Error: {e.reason}", file=sys.stderr)
        sys.exit(1)


def format_timestamp(ts: str) -> str:
    """Format ISO timestamp to readable format."""
    try:
        dt = datetime.fromisoformat(ts.replace("Z", "+00:00"))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except (ValueError, AttributeError):
        return ts or "N/A"


def cmd_issues(args):
    """List project issues."""
    params = {
        "statsPeriod": args.period or "24h",
        "cursor": args.cursor,
    }

    if args.all:
        params["query"] = ""
    elif args.query:
        params["query"] = args.query
    # Default: is:unresolved (API default)

    endpoint = f"/projects/{ORG_SLUG}/{PROJECT_SLUG}/issues/"
    issues = api_request(endpoint, params)

    if not issues:
        print("No issues found")
        return

    limit = args.limit or 20
    for i, issue in enumerate(issues[:limit]):
        status = issue.get("status", "unknown")
        level = issue.get("level", "error")
        count = issue.get("count", 0)
        users = issue.get("userCount", 0)
        title = issue.get("title", "No title")
        last_seen = format_timestamp(issue.get("lastSeen"))
        issue_id = issue.get("id")
        short_id = issue.get("shortId", issue_id)

        # Color coding for level
        level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵"}.get(level, "⚪")
        status_icon = {"resolved": "✅", "ignored": "🔕"}.get(status, "")

        print(f"\n{level_icon} [{short_id}] {title} {status_icon}")
        print(f"   Events: {count} | Users: {users} | Last seen: {last_seen}")
        print(f"   ID: {issue_id}")


def cmd_events(args):
    """List project events."""
    params = {
        "statsPeriod": args.period or "24h",
    }

    endpoint = f"/projects/{ORG_SLUG}/{PROJECT_SLUG}/events/"
    events = api_request(endpoint, params)

    if not events:
        print("No events found")
        return

    limit = args.limit or 20
    for event in events[:limit]:
        event_id = event.get("eventID", "N/A")
        title = event.get("title", "No title")
        timestamp = format_timestamp(event.get("dateCreated"))
        user = event.get("user", {})
        user_str = user.get("email") or user.get("username") or user.get("id") or "anonymous"

        print(f"\n📍 {title}")
        print(f"   Time: {timestamp} | User: {user_str}")
        print(f"   Event ID: {event_id}")


def cmd_issue_detail(args):
    """Get detailed information about a specific issue."""
    endpoint = f"/issues/{args.issue_id}/"
    issue = api_request(endpoint)

    print(f"\n{'='*60}")
    print(f"Issue: {issue.get('shortId')} - {issue.get('title')}")
    print(f"{'='*60}")
    print(f"Status: {issue.get('status')}")
    print(f"Level: {issue.get('level')}")
    print(f"Events: {issue.get('count')}")
    print(f"Users affected: {issue.get('userCount')}")
    print(f"First seen: {format_timestamp(issue.get('firstSeen'))}")
    print(f"Last seen: {format_timestamp(issue.get('lastSeen'))}")

    # Get latest event for more context
    events_endpoint = f"/issues/{args.issue_id}/events/"
    events = api_request(events_endpoint, {"limit": "1"})

    if events:
        event = events[0]
        print(f"\n--- Latest Event ---")
        print(f"Time: {format_timestamp(event.get('dateCreated'))}")

        # User info
        user = event.get("user", {})
        if user:
            print(f"User: {user.get('email') or user.get('username') or user.get('id', 'N/A')}")

        # Context
        contexts = event.get("contexts", {})
        if "device" in contexts:
            device = contexts["device"]
            print(f"Device: {device.get('model', 'N/A')} ({device.get('family', 'N/A')})")
        if "os" in contexts:
            os_info = contexts["os"]
            print(f"OS: {os_info.get('name', 'N/A')} {os_info.get('version', '')}")
        if "app" in contexts:
            app = contexts["app"]
            print(f"App: {app.get('app_version', 'N/A')} (build {app.get('app_build', 'N/A')})")


def cmd_breadcrumbs(args):
    """Get breadcrumbs (user actions) for an issue's latest event."""
    events_endpoint = f"/issues/{args.issue_id}/events/"
    events = api_request(events_endpoint, {"limit": "1"})

    if not events:
        print("No events found for this issue")
        return

    event = events[0]
    breadcrumbs = event.get("entries", [])

    print(f"\n{'='*60}")
    print(f"Breadcrumbs for Issue {args.issue_id}")
    print(f"Event time: {format_timestamp(event.get('dateCreated'))}")
    print(f"{'='*60}")

    crumb_entry = None
    for entry in breadcrumbs:
        if entry.get("type") == "breadcrumbs":
            crumb_entry = entry
            break

    if not crumb_entry:
        print("No breadcrumbs found")
        return

    crumbs = crumb_entry.get("data", {}).get("values", [])

    for crumb in crumbs:
        ts = format_timestamp(crumb.get("timestamp"))
        category = crumb.get("category", "unknown")
        level = crumb.get("level", "info")
        message = crumb.get("message", "")
        crumb_type = crumb.get("type", "")
        data = crumb.get("data", {})

        level_icon = {"error": "🔴", "warning": "🟡", "info": "🔵", "debug": "⚪"}.get(level, "⚪")

        print(f"\n{level_icon} [{category}] {message}")
        print(f"   {ts}")
        if data:
            for k, v in data.items():
                print(f"   {k}: {v}")


def cmd_user(args):
    """Search for issues/events by user email."""
    query = f'user.email:"{args.email}"'

    params = {
        "query": query,
        "statsPeriod": args.period or "14d",
    }

    endpoint = f"/projects/{ORG_SLUG}/{PROJECT_SLUG}/issues/"
    issues = api_request(endpoint, params)

    print(f"\n{'='*60}")
    print(f"Issues for user: {args.email}")
    print(f"{'='*60}")

    if not issues:
        print("No issues found for this user")
        return

    for issue in issues[:args.limit or 10]:
        title = issue.get("title", "No title")
        count = issue.get("count", 0)
        last_seen = format_timestamp(issue.get("lastSeen"))
        issue_id = issue.get("id")

        print(f"\n🔴 {title}")
        print(f"   Events: {count} | Last seen: {last_seen}")
        print(f"   ID: {issue_id}")


def main():
    check_config()
    parser = argparse.ArgumentParser(
        description="Sentry API client for CLI-based monitoring",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 sentry_api.py issues                    # Unresolved issues (24h)
  python3 sentry_api.py issues --all              # All issues
  python3 sentry_api.py issues --query "is:unresolved level:error"
  python3 sentry_api.py events --period 7d        # Events from last 7 days
  python3 sentry_api.py issue 12345               # Issue details
  python3 sentry_api.py breadcrumbs 12345         # User actions before error
  python3 sentry_api.py user test@example.com     # Issues for specific user
        """
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # issues command
    issues_parser = subparsers.add_parser("issues", help="List project issues")
    issues_parser.add_argument("--all", action="store_true", help="Include resolved issues")
    issues_parser.add_argument("--query", "-q", help="Sentry search query")
    issues_parser.add_argument("--period", "-p", default="24h", help="Time period (24h, 7d, 14d)")
    issues_parser.add_argument("--limit", "-n", type=int, default=20, help="Max results")
    issues_parser.add_argument("--cursor", help="Pagination cursor")

    # events command
    events_parser = subparsers.add_parser("events", help="List project events")
    events_parser.add_argument("--period", "-p", default="24h", help="Time period")
    events_parser.add_argument("--limit", "-n", type=int, default=20, help="Max results")

    # issue detail command
    issue_parser = subparsers.add_parser("issue", help="Get issue details")
    issue_parser.add_argument("issue_id", help="Issue ID")

    # breadcrumbs command
    breadcrumbs_parser = subparsers.add_parser("breadcrumbs", help="Get breadcrumbs for issue")
    breadcrumbs_parser.add_argument("issue_id", help="Issue ID")

    # user command
    user_parser = subparsers.add_parser("user", help="Search by user email")
    user_parser.add_argument("email", help="User email")
    user_parser.add_argument("--period", "-p", default="14d", help="Time period")
    user_parser.add_argument("--limit", "-n", type=int, default=10, help="Max results")

    args = parser.parse_args()

    commands = {
        "issues": cmd_issues,
        "events": cmd_events,
        "issue": cmd_issue_detail,
        "breadcrumbs": cmd_breadcrumbs,
        "user": cmd_user,
    }

    commands[args.command](args)


if __name__ == "__main__":
    main()
