---
name: sentry-monitor
description: |
  Sentry error monitoring and user behavior tracking via CLI.
  Use when: (1) debugging user-reported issues, (2) checking recent errors/crashes,
  (3) tracing user actions before an error occurred, (4) searching issues by user email,
  (5) user asks "Sentryのログを確認して" or similar.
---

# Sentry Monitor

CLI-based Sentry monitoring for debugging user issues.

## 使用方法

**重要**: Sentryログの確認にはTaskエージェント（haiku）を使用して高速に検索する。

```
Task tool:
  subagent_type: "general-purpose"
  model: "haiku"
  prompt: "Sentryのログを確認して、VLM関連のイベントを探してください。以下のコマンドを実行して結果を報告: python3 ~/.claude/skills/sentry-monitor/scripts/sentry_api.py issues --all --limit 20"
```

## Setup

Required environment variables:

```bash
# Required: Sentry API token
# Get from: https://sentry.io/settings/auth-tokens/
export SENTRY_AUTH_TOKEN="your-token"

# Required: Your Sentry organization slug
export SENTRY_ORG="your-org"

# Required: Your Sentry project slug
export SENTRY_PROJECT="your-project"
```

Add these to your `~/.zshenv` or `~/.bashrc`.

## Commands

```bash
SCRIPT="~/.claude/skills/sentry-monitor/scripts/sentry_api.py"

# List unresolved issues (last 24h)
python3 $SCRIPT issues

# List all issues (including resolved)
python3 $SCRIPT issues --all

# Search with query
python3 $SCRIPT issues --query "level:error"
python3 $SCRIPT issues --query "is:unresolved has:user"

# Events from last 7 days
python3 $SCRIPT events --period 7d

# Issue details
python3 $SCRIPT issue <ISSUE_ID>

# User actions (breadcrumbs) before error
python3 $SCRIPT breadcrumbs <ISSUE_ID>

# Search by user email
python3 $SCRIPT user test@example.com
```

## Query Syntax

| Query | Description |
|-------|-------------|
| `is:unresolved` | Unresolved issues (default) |
| `is:resolved` | Resolved issues |
| `level:error` | Error level only |
| `level:warning` | Warning level only |
| `user.email:X` | Filter by user email |
| `has:user` | Issues with user info |

## Debugging Workflow

1. **Check recent issues**: `python3 $SCRIPT issues`
2. **Get issue details**: `python3 $SCRIPT issue <ID>`
3. **View user actions**: `python3 $SCRIPT breadcrumbs <ID>`
4. **Search by user**: `python3 $SCRIPT user <EMAIL>` (when user reports problem)

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SENTRY_AUTH_TOKEN` | Yes | API token from Sentry |
| `SENTRY_ORG` | Yes | Your Sentry organization slug |
| `SENTRY_PROJECT` | Yes | Your Sentry project slug |
