// LaTeX-syntax math (incl. \ce{} chemistry) -> standalone SVG on stdout. Usage: node render.mjs '<tex>'
import {mathjax} from 'mathjax-full/js/mathjax.js';
import {TeX} from 'mathjax-full/js/input/tex.js';
import {SVG} from 'mathjax-full/js/output/svg.js';
import {liteAdaptor} from 'mathjax-full/js/adaptors/liteAdaptor.js';
import {RegisterHTMLHandler} from 'mathjax-full/js/handlers/html.js';
import 'mathjax-full/js/input/tex/AllPackages.js';
import 'mathjax-full/js/input/tex/mhchem/MhchemConfiguration.js';

const tex = process.argv[2];
if (!tex) { console.error('usage: render.mjs <tex>'); process.exit(2); }
const adaptor = liteAdaptor();
RegisterHTMLHandler(adaptor);
const doc = mathjax.document('', {
  InputJax: new TeX({packages: ['base', 'ams', 'mhchem', 'physics', 'boldsymbol', 'newcommand', 'noundefined']}),
  OutputJax: new SVG({fontCache: 'none'}),
});
const node = doc.convert(tex, {display: true});
const svg = adaptor.innerHTML(node).match(/<svg[\s\S]*<\/svg>/)[0];
process.stdout.write(svg.replace(/currentColor/g, '#e6edf3'));
