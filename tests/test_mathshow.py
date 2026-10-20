import os, subprocess, sys, tempfile, unittest
HERE = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))
sys.path.insert(0, HERE)
import mathshow

class T(unittest.TestCase):
    def test_chunks_rejoin_and_fit(self):
        with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f: f.write(os.urandom(10000))
        import base64
        ch = mathshow.chunks(f.name)
        self.assertEqual("".join(ch), base64.standard_b64encode(open(f.name, "rb").read()).decode())
        self.assertTrue(all(len(c) <= 4096 for c in ch))

    def test_render_outputs_svg_with_ex_size(self):
        for tex in (r"\frac{a}{b}", r"\ce{2H2 + O2 -> 2H2O}"):
            out = subprocess.run(["node", os.path.join(HERE, "render.mjs"), tex], capture_output=True, text=True)
            self.assertEqual(out.returncode, 0, out.stderr)
            self.assertRegex(out.stdout, r'width="[\d.]+ex" height="[\d.]+ex"')

    def test_bad_math_fails_instead_of_drawing_an_error(self):
        for tex in (r"\frac{", r"\undefinedmacro{x}"):
            out = subprocess.run(["node", os.path.join(HERE, "render.mjs"), tex], capture_output=True, text=True)
            self.assertEqual(out.returncode, 1, tex)

if __name__ == "__main__": unittest.main()
