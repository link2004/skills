# Claude Code Skills

A collection of custom skills for [Claude Code](https://claude.ai/claude-code).

## Available Skills

| Skill | Description |
|-------|-------------|
| [video-frame-reader](./video-frame-reader) | Extract keyframes from video files and analyze with AI |

## Installation

Clone this repository and copy the desired skill to your Claude skills directory:

```bash
# Clone the repository
git clone https://github.com/link2004/claude-code-skills.git

# Copy a skill to your Claude skills directory
cp -r claude-code-skills/video-frame-reader ~/.claude/skills/
```

Or install a specific skill directly:

```bash
# Install video-frame-reader
git clone --depth 1 https://github.com/link2004/claude-code-skills.git /tmp/claude-code-skills
cp -r /tmp/claude-code-skills/video-frame-reader ~/.claude/skills/
rm -rf /tmp/claude-code-skills
```

## Contributing

Feel free to submit pull requests with new skills or improvements to existing ones.

## License

MIT License
