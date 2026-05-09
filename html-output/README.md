# html-output

A [Claude Code](https://docs.claude.com/en/docs/claude-code) skill that writes a visually scannable HTML page from your conversation, publishes it to a public S3 bucket, and returns a short shareable URL.

> Replace Markdown walls of text with at-a-glance HTML — metrics cards, side-by-side comparisons, inline SVG diagrams, timelines, color-coded callouts. **Visible in 5 seconds, shareable in 1 link.**

## Why

When Claude Code outputs long reports, comparisons, or how-to guides directly in chat, important details get buried in walls of text. This skill turns that output into a single self-contained HTML file with strong visual hierarchy, hosts it on your own S3 bucket, and hands you a short URL like:

```
https://<your-bucket>.s3.<region>.amazonaws.com/setup-guide-4f0e78eb.html
```

URLs use a 32-bit random suffix, which combined with S3's rate limits is **practically unguessable** for casual attackers (~14 days of sustained brute force at the S3 limit, just to enumerate one timestamp window). The bucket grants public-read on objects only — no listing — so distribution is controlled by who you share the URL with.

> Want stronger guarantees? Bump the suffix to 16 hex (64-bit) by changing one line in `scripts/publish.sh`: `secrets.token_hex(4)` → `secrets.token_hex(8)`. URL grows by 8 chars, brute force becomes physically infeasible.

## Three URL modes

| Mode | Trigger | Result | Use |
|---|---|---|---|
| **timestamp** | no argument | `<YYYY-MM-DDTHHMM>-<8hex>.html` | one-shot ephemeral output |
| **named** | a name string | `<slug>-<8hex>.html` | persistent doc you'll link to later |
| **overwrite** | full key ending in `.html` | the same key, new content | update existing doc, URL stays the same |

Names auto-slug (lowercase, alphanumeric+hyphens) so you can pass `"Setup Guide"` and get `setup-guide-<8hex>.html`.

## Install

### Recommended: via [`skills`](https://github.com/vercel-labs/skills) CLI

```bash
# From the link2004/skills monorepo
npx skills add link2004/skills --skill html-output --global

# Or from the standalone repo
npx skills add link2004/html-output --global
```

For other agents (Cursor, Cline, etc.), pass `--agent <name>` — see the upstream docs.

### Manual

```bash
git clone --depth 1 https://github.com/link2004/skills.git /tmp/link2004-skills
cp -r /tmp/link2004-skills/html-output ~/.claude/skills/
rm -rf /tmp/link2004-skills
```

### Then, one-time AWS setup

```bash
# 1. Fill in your bucket / region / profile / IAM user
cp ~/.claude/skills/html-output/config.example.json ~/.claude/skills/html-output/config.json
$EDITOR ~/.claude/skills/html-output/config.json

# 2. Bootstrap S3 + IAM (creates a bucket, an IAM user scoped to that bucket only,
#    and an access key). See:
open ~/.claude/skills/html-output/references/setup.md
```

### Trigger from Claude Code

Type `/html-output` directly, or just say "HTML化して" / "publish this as HTML" / "make it browseable" — the skill description catches those phrases automatically.

## What it does (concretely)

1. Claude writes a single self-contained HTML page with inline CSS, inline SVG, no CDN.
2. Pipes the HTML to `scripts/publish.sh` over stdin.
3. `publish.sh` reads `config.json`, picks a key based on the argument, uploads via `aws s3 cp` with `Content-Type: text/html`, and prints the public URL.
4. You paste that URL anywhere — Slack, email, a tweet, another HTML doc.

## Wiki-style cross-linking

Use `scripts/list.sh <name-prefix>` to find existing docs and embed their URLs in new ones:

```bash
URL=$(bash scripts/list.sh setup-guide | head -1)
# Then in your HTML: <a href="$URL">setup guide</a>
```

This turns the bucket into a tiny wiki where docs reference each other by name, AI included can read them back.

## Cost

Practically free for personal use. With Tokyo region pricing (`ap-northeast-1`):

- ~$0.001/month at light usage (100 files, 1k views)
- ~$0.01/month at heavy usage (1k files, 10k views)
- 100 GB/month transfer is free
- AWS free tier covers your first year entirely

See [`references/setup.md`](references/setup.md) and the spec doc for details.

## Security

- 32-bit random suffix per file → brute-force enumeration takes ~14 days at S3's rate limit, even when an attacker knows the timestamp prefix
- `s3:ListBucket` is **not** public — unknown filenames cannot be discovered
- Bucket policy only grants `s3:GetObject` (no PUT/DELETE/LIST to the public)
- The IAM user used to upload has no permissions outside this one bucket

The realistic risk is URL leakage (sharing in public channels, browser history, search-engine crawl of public pages). Don't put genuine secrets in HTML you share via this.

## Files

```
html-output/
├── SKILL.md                    # the prompt Claude Code reads
├── config.json                 # YOUR personal values (gitignored)
├── config.example.json         # placeholder template
├── scripts/
│   ├── publish.sh              # stdin/file → S3 → URL
│   └── list.sh                 # find existing docs by prefix
└── references/
    └── setup.md                # one-time AWS bootstrap
```

## License

MIT — see [LICENSE](LICENSE).

## Author

Built by [@link2004](https://github.com/link2004) while iterating with Claude Code. PRs welcome.
