#!/usr/bin/env python3
"""Render math as a boxed image in a Kitty-graphics terminal (Ghostty).
  mathshow '<tex>'   render + queue; prints the spacer block to end your message with
  mathshow flush     (Stop hook) draw the queued image over the spacer rows
  mathshow clear     (UserPromptSubmit hook) delete our images
"""
import os, sys, re, json, math, base64, fcntl, termios, struct, subprocess, tempfile
HERE = os.path.dirname(os.path.realpath(__file__))
STATE = os.path.join(HERE, ".pending.json")
BASE = 4200   # our image ids live in BASE..BASE+99, so clear never touches other programs' images
GAP = 5       # rows between a message's last line and the cursor, measured with the calibration spike
FG, BORDER, FILL = "#e6edf3", "#6b8299", "#0f1620"

def supported():
    # Kitty graphics terminals; MATHSHOW_FORCE=1 overrides detection (e.g. inside tmux with passthrough)
    e = os.environ
    return bool(e.get("MATHSHOW_FORCE") or e.get("KITTY_WINDOW_ID") or e.get("TERM_PROGRAM") in ("ghostty", "WezTerm")
                or "kitty" in e.get("TERM", "") or "ghostty" in e.get("TERM", ""))

def log(msg):
    open(os.path.join(HERE, ".log"), "a").write(msg + "\n")

def tty():
    if os.environ.get("MATH_TTY"): return os.environ["MATH_TTY"]
    p = os.getpid()
    while p > 1:
        t = subprocess.run(["ps","-o","tty=","-p",str(p)],capture_output=True,text=True).stdout.strip()
        if t and t != "??": return "/dev/"+t
        pp = subprocess.run(["ps","-o","ppid=","-p",str(p)],capture_output=True,text=True).stdout.strip()
        if not pp: break
        p = int(pp)
    sys.exit("mathshow: no terminal found (not running under a terminal?)")

def cell_px(dev):
    # ioctl gives rows, cols, xpixel, ypixel; fall back to a typical cell if the terminal reports 0
    with open(dev) as f:
        r, c, xp, yp = struct.unpack("HHHH", fcntl.ioctl(f, termios.TIOCGWINSZ, b"\0"*8))
    return (xp/c if xp and c else 10.0), (yp/r if yp and r else 20.0), c

def build(tex, dev):
    cw, ch, term_cols = cell_px(dev)
    svg = subprocess.run(["node", os.path.join(HERE,"render.mjs"), tex], capture_output=True, text=True)
    if svg.returncode: sys.exit("mathshow: bad math: " + (svg.stderr.strip() or svg.stdout.strip()))
    svg = svg.stdout
    w_ex, h_ex = (float(x) for x in re.search(r'width="([\d.]+)ex" height="([\d.]+)ex"', svg).groups())
    ex = 0.65 * ch                                   # math ~1.5x the text height
    maxw = (term_cols - 6) * cw
    pad = 0.9 * ch
    W, H = w_ex*ex + 2*pad*1.4, h_ex*ex + 2*pad
    if W > maxw: ex *= (maxw - 2*pad*1.4) / (w_ex*ex); W, H = w_ex*ex + 2*pad*1.4, h_ex*ex + 2*pad
    cols, rows = math.ceil(W/cw), math.ceil(H/ch)
    CW, CH = round(cols*cw), round(rows*ch)          # canvas is exactly cols x rows cells: no stretching
    svg = re.sub(r'width="[\d.]+ex" height="[\d.]+ex"', f'width="{round(w_ex*ex)}" height="{round(h_ex*ex)}"', svg, count=1)
    d = tempfile.mkdtemp(prefix="mathshow-")
    open(f"{d}/m.svg","w").write(svg)
    out = os.path.join(HERE, ".last.png")
    r = round(0.8*ch)
    subprocess.run(["magick","-background","none","-density","72",f"{d}/m.svg",f"{d}/m.png"], check=True)
    subprocess.run(["magick","-size",f"{CW}x{CH}","xc:none","-fill",FILL,"-stroke",BORDER,"-strokewidth","3",
        "-draw",f"roundrectangle 2,2 {CW-3},{CH-3} {r},{r}", f"{d}/m.png","-gravity","center","-composite",
        "-depth","8","-type","TrueColorAlpha", out], check=True)
    return out, cols, rows

def chunks(png):
    d = base64.standard_b64encode(open(png,"rb").read()).decode()
    return [d[i:i+4096] for i in range(0,len(d),4096)]

def draw(png, cols, rows, slot=0, col=2):
    ch = chunks(png)
    with open(tty(),"w") as f:
        f.write(f"\x1b7\x1b[{GAP+rows}A\x1b[{col+1}G")   # save cursor, up to the top spacer row
        for n,c in enumerate(ch):
            ctrl = f"a=T,f=100,C=1,q=2,i={BASE+slot},c={cols},r={rows}," if n == 0 else ""
            f.write(f"\x1b_G{ctrl}m={int(n < len(ch)-1)};{c}\x1b\\")
        f.write("\x1b8")

def clear():
    with open(tty(),"w") as f:
        for i in range(100): f.write(f"\x1b_Ga=d,d=I,i={BASE+i},q=2\x1b\\")

def main(argv):
    if not argv: sys.exit(__doc__)
    if not supported():
        if argv[0] in ("clear", "flush"): return   # hooks stay silent outside Kitty-graphics terminals
        sys.exit("mathshow: this terminal doesn't look like it supports Kitty graphics (set MATHSHOW_FORCE=1 to try anyway)")
    if argv[0] == "clear": return clear()
    if argv[0] == "flush":
        if not os.path.exists(STATE): return
        p = json.load(open(STATE)); os.remove(STATE)
        try:
            draw(p["png"], p["cols"], p["rows"])
            log(f"flush ok tty={tty()} {p['cols']}x{p['rows']}")
        except BaseException as e:
            log(f"flush FAILED: {e!r}")
        return
    png, cols, rows = build(argv[0], tty())
    kept = os.path.join(HERE, ".pending.png"); os.replace(png, kept)
    json.dump({"png": kept, "cols": cols, "rows": rows}, open(STATE,"w"))
    print(f"Queued {cols}x{rows} cells. The image appears when your reply ends.\n"
          f"End your reply with exactly this block (a code block with {rows} rows), and put nothing after it:\n")
    print("```\n" + "\n".join("·"*1 for _ in range(rows)) + "\n```")

if __name__ == "__main__":
    main(sys.argv[1:])
