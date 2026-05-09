# Claude Code Skills

A collection of custom skills for [Claude Code](https://docs.claude.com/en/docs/claude-code).

## Available Skills

| Skill | Description |
|-------|-------------|
| [html-output](./html-output) | Render the conversation as a visually scannable HTML page, publish to your S3, return a short URL |
| [nanobanana](./nanobanana) | Generate / edit images via Google Gemini (Nano Banana) or OpenAI GPT Image, including sticker-sheet split |
| [sentry-monitor](./sentry-monitor) | Sentry error monitoring & user behavior tracking via CLI |
| [video-frame-reader](./video-frame-reader) | Extract keyframes from video files and analyze with AI |

## Installation

### Recommended: via [`skills`](https://github.com/vercel-labs/skills) CLI

```bash
# Install one skill globally
npx skills add link2004/skills --skill html-output --global

# Or pick interactively from the list
npx skills add link2004/skills --global
```

### Manual

```bash
git clone --depth 1 https://github.com/link2004/skills.git /tmp/link2004-skills
cp -r /tmp/link2004-skills/html-output ~/.claude/skills/
rm -rf /tmp/link2004-skills
```

Replace `html-output` with any skill name from the table above.

## Contributing

PRs welcome — add a new directory at the repo root with `SKILL.md` plus any supporting files, and add a row to the table above.

## License

MIT
