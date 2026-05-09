---
name: html-output
description: Turn the current conversation content into a visually scannable HTML page, publish it to a personal S3 bucket, and return a short shareable URL. Use when (1) the user asks to "make this an HTML / link / browser-viewable page" (in any language, e.g. "HTML化して", "リンクで渡して", "ブラウザで見れる形に"), (2) "upload to s3" / "s3に上げて" is requested, (3) the content has tables, code, comparisons, charts, timelines, or diagrams that Markdown chat can't convey well, (4) the output is something the user wants to come back to later.
---

# html-output

Take the content from `$ARGUMENTS` or the immediate conversation context, render it as a **visually-priority HTML page**, publish it via `publish.sh` to S3, and return the URL.

## Design principles

Never produce "Markdown translated into `<p>` tags." **Use what HTML is good at**:

- **5-second rule**: in 5 seconds the reader should grasp "what topic, what conclusion."
- **Visual hierarchy (size + color + weight)**: more important info → larger, bolder, with color. Don't bury it in body text.
- **Headline numbers as huge cards**: primary metrics in 30–50px digits.
- **Comparisons → side-by-side cards**: prefer grids of cards (with hairline color accents) over tables.
- **Flow / relationships → inline SVG**: hand-draw diagrams. Avoid CDN libraries (Chart.js, Mermaid) — heavy and slow to load.
- **Numeric comparisons → bar chart**: simple CSS horizontal bars with a green→red gradient.
- **Structures → tree view**: monospace, indented, color-keyed.
- **Conclusions → callouts**: tinted box with a colored left border.
- **Anti-patterns**: walls of `<p>` / uniformly-sized text / decorative-only SVGs / emoji spam / "just-in-case" CDN includes.

The actual CSS / HTML is **left to the AI's creativity** — don't templatize components, every output should fit its content.

## Color palette

**Always light (white background)**. Do not auto-switch to dark mode (no `prefers-color-scheme: dark` block).

- background: `#ffffff`
- body text: `#111827` (near-black slate)
- secondary: `#6b7280` (muted gray)
- borders: `#e5e7eb` (very light gray)
- card / code background: `#fafafa` to `#f3f4f6`
- primary accent: **orange `#d97706`** / soft accent bg: `#fef3c7`
- semantic: green `#16a34a` / yellow `#f59e0b` / red `#dc2626`

## Language

Match the input language exactly — if the brief / conversation is in Japanese, write the HTML in Japanese; if English, English. **Do not translate.**

## Publish step

```bash
bash ~/.claude/skills/html-output/scripts/publish.sh <<'HTML'
<!DOCTYPE html>
<html lang="ja">
<head>...</head>
<body>...</body>
</html>
HTML
```

Argument matrix:

| Argument | Behavior | Use |
|---|---|---|
| (none) | new `<timestamp>-<8hex>.html` | one-shot, ephemeral |
| `<name>` | new `<slug>-<8hex>.html` | persistent doc (wiki-style) |
| `<key>.html` | overwrite existing key | update existing doc, URL stays the same |

Return the URL inside a code fence (Markdown's `&` interpretation can otherwise truncate it).

## Wiki cross-link

To reference an existing document from a new one:

```bash
bash ~/.claude/skills/html-output/scripts/list.sh <name-prefix>
# → list of matching URLs
```

Embed those URLs in the new page with `<a href="...">`.

## File layout

| Path | Role |
|---|---|
| `scripts/publish.sh` | upload + return public URL (stdin pipe) |
| `scripts/list.sh` | search existing docs (for wiki cross-linking) |
| `config.json` / `config.example.json` | bucket / profile config |
| `references/setup.md` | one-time AWS bootstrap |
