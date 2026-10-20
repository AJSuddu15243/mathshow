# mathshow

Proper math notation inside your terminal chat. Integrals, derivatives, sums, Greek letters, physics formulas and chemical equations are rendered as a boxed image inline, using the **Kitty graphics protocol**, instead of being squeezed into plain text.

Built for [Claude Code](https://claude.com/claude-code): the agent writes an explanation, calls `mathshow`, and the equation appears in the chat. No changes to Claude Code itself.

## Supported terminals

mathshow draws with the [Kitty graphics protocol](https://sw.kovidgoyal.net/kitty/graphics-protocol/).

| Terminal | Status |
|---|---|
| Ghostty | Tested |
| Kitty, WezTerm | Speak the same protocol; untested |
| iTerm2, Terminal.app, Windows Terminal, VS Code | Not supported (different or no image protocol) |
| tmux / screen | Not supported by default; try `MATHSHOW_FORCE=1` with passthrough enabled |

In unsupported terminals the hooks do nothing and `mathshow` exits with an error, so the agent falls back to plain text.

## Requirements

`node`, `npm`, `python3`, and ImageMagick (`magick`). On macOS: `brew install node imagemagick`. No TeX install needed; math is rendered with [MathJax](https://www.mathjax.org/).

## Install

```sh
git clone https://github.com/AJSuddu15243/mathshow.git
cd mathshow
./install.sh
```

This installs dependencies, links `mathshow` into `~/.local/bin`, links the skill into `~/.claude/skills/`, and adds two hooks to `~/.claude/settings.json` (a backup is saved as `settings.json.bak-mathshow`). Restart Claude Code afterwards. Remove everything with `./install.sh --uninstall`.

**As a plugin (experimental, untested):** the repo also ships a Claude Code plugin manifest and marketplace file: `/plugin marketplace add AJSuddu15243/mathshow`, then `/plugin install mathshow@mathshow`. You still need the requirements above, and `npm install` run once inside the plugin folder.

## Use

Ask Claude for anything with real notation ("derive the Gaussian integral", "balance this reaction", "show the epsilon-delta definition of a limit"). Or call it yourself:

```sh
mathshow '\int_0^\infty e^{-x^2}\,dx=\frac{\sqrt\pi}{2}'
mathshow '\ce{2H2 + O2 -> 2H2O}'
mathshow '\begin{aligned} f(x) &= x^2 \\ f'"'"'(x) &= 2x \end{aligned}'
```

Input is LaTeX math syntax, plus `\ce{}` for chemistry and the `physics` package macros.

## How it works

1. `mathshow '<tex>'` renders the math to SVG (MathJax), then to a PNG in a rounded dark box sized exactly to a whole number of terminal cells, using your terminal's real cell pixel size.
2. It prints a block of N placeholder rows. The agent ends its reply with that block, which reserves N rows of space in the chat.
3. When the reply finishes, a `Stop` hook writes the image to the terminal's tty over those rows (Claude Code's own output capture is bypassed, which is why no harness change is needed).
4. When you send the next prompt, a `UserPromptSubmit` hook deletes the image.

## Limits

- One image per reply (put several equations in one call).
- The image is drawn at a fixed row offset above the cursor (`GAP` in `mathshow.py`, measured for a one-line prompt plus the status line). A multi-line prompt or a resize can misalign it until the next prompt. Adjust `GAP` if your layout differs.
- Images are removed on the next prompt, not kept in scrollback history.
- No plots or graphs yet.

## Troubleshooting

- **Nothing appears:** hooks load at session start; restart Claude Code after installing. Check `mathshow/.log` for the result of the last draw.
- **Image stuck on screen:** run `mathshow clear`, or press Ctrl+L.
- **Image covers text:** the reply didn't end with the exact block `mathshow` printed, or `GAP` doesn't match your layout.

## Tests

```sh
python3 -m unittest discover -s tests
```

## License

MIT, see [LICENSE](LICENSE).
