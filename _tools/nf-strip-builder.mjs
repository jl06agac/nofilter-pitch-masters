#!/usr/bin/env node
// nf-strip-builder.mjs — remove the Part 2 quote builder from a stamped build.
//
//   node nf-strip-builder.mjs <stamped.html> --out <file>
//
// For clients who have ALREADY committed (renewed / signed) and so have nothing to
// choose: the pitch keeps the record, the beats and the close, and drops the
// price/machine/term wizard entirely.
//
// It excises <section class="section" id="price"> … </section> by real tag matching
// (not regex-over-match), and reports the byte delta so a silent no-op is impossible.
// The builder's JS is left in place: it is defensive and self-disables when its
// elements are absent (see the `if(!panel || !grid) return;` guard in initSpecs).
// Verified: zero page errors with the section removed.

import { readFileSync, writeFileSync } from 'node:fs';

const args = process.argv.slice(2);
const outIdx = args.indexOf('--out');
const src = args.find((a) => !a.startsWith('--') && a !== args[outIdx + 1]);
const out = outIdx > -1 ? args[outIdx + 1] : null;
if (!src || !out) {
  process.stderr.write('usage: node nf-strip-builder.mjs <stamped.html> --out <file>\n');
  process.exit(2);
}

const html = readFileSync(src, 'utf8');
const OPEN = '<section class="section" id="price"';
const i = html.indexOf(OPEN);
if (i === -1) {
  process.stderr.write(`nf-strip-builder: no builder section found in ${src}\n`);
  process.exit(1);
}
let depth = 0, j = -1;
const re = /<section\b|<\/section>/g;
re.lastIndex = i;
for (let m; (m = re.exec(html)) !== null; ) {
  depth += m[0].startsWith('<section') ? 1 : -1;
  if (depth === 0) { j = m.index + m[0].length; break; }
}
if (j === -1) {
  process.stderr.write('nf-strip-builder: unbalanced <section> tags — refusing to cut\n');
  process.exit(1);
}
const stripped = html.slice(0, i)
  + '<!-- builder removed: this client has already committed (nf-strip-builder) -->'
  + html.slice(j);
writeFileSync(out, stripped);
process.stderr.write(`nf-strip-builder: removed ${j - i} bytes (${html.slice(i, j).split('\n').length} lines)\n`);
process.stderr.write(`wrote ${out}\n`);
