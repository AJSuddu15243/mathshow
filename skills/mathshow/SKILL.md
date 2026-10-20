---
name: mathshow
description: Render math as a boxed image inline in the Ghostty terminal. Use whenever a reply needs real notation that plain text shows badly: integrals, derivatives, sums, limits, fractions, matrices, Greek-heavy formulas, worked derivations, physics formulas, chemical equations. Also when the user pastes LaTeX and wants it shown.
---

# mathshow

Draws an equation as a boxed image over reserved rows in the terminal chat. Works only in Kitty-graphics terminals (tested: Ghostty). Images are cleared automatically when the user sends their next prompt.

## How to use

1. Write your explanation in normal text first.
2. Run, with LaTeX-syntax math (single quotes; `\ce{...}` for chemistry; `aligned` for multi-line derivations):

   ```
   mathshow '\int_0^\infty e^{-x^2}\,dx=\frac{\sqrt\pi}{2}'
   ```

3. The command prints a code block of `·` rows sized to the image. **End your reply with that block exactly as printed, and write nothing after it.** The image is drawn over those rows when your reply finishes. Text after the block, or a different number of rows, makes the image cover your text.

## Rules

- One image per reply. Put several equations in one call (`\quad` between them, or `\begin{aligned} a &= b \\ c &= d \end{aligned}` for steps).
- A very long single-line equation is shrunk to fit the terminal width and becomes unreadable: split it with `aligned` instead.
- Keep the explanation above the block, and make the math the last thing in the reply.
- Quote the tex in single quotes; escape a literal `'` as `'\''`.
- If the command errors ("bad math", "no terminal found", "command not found"), say so and fall back to plain text or Unicode (ε, δ, π, μ, ∫, ∂, √).
- Do not describe the image as if you can see it. You cannot; the user sees it.

## Limits (v1)

- No plots or graphs yet.
- If the terminal is resized or the user's prompt grows several lines, the offset shifts and the box may misalign until the next prompt.
