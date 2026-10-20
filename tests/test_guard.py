import os, subprocess, sys, unittest
HERE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

class T(unittest.TestCase):
    def run_ms(self, *a, **env):
        e = {k: v for k, v in os.environ.items() if k not in ("TERM_PROGRAM", "KITTY_WINDOW_ID", "MATHSHOW_FORCE")}
        e.update(TERM="xterm-256color", **env)
        return subprocess.run([sys.executable, os.path.join(HERE, "mathshow.py"), *a], env=e, capture_output=True, text=True)

    def test_hooks_silent_when_unsupported(self):
        for cmd in ("clear", "flush"):
            r = self.run_ms(cmd); self.assertEqual((r.returncode, r.stdout, r.stderr), (0, "", ""))

    def test_render_refuses_when_unsupported(self):
        r = self.run_ms("x^2"); self.assertNotEqual(r.returncode, 0); self.assertIn("Kitty graphics", r.stderr)

if __name__ == "__main__": unittest.main()
