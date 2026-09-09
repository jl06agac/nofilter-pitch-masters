#!/usr/bin/env node
// nf-ship-stamp.mjs — make a built bundle able to say which build it is.
//
//   node _tools/nf-ship-stamp.mjs Marketing/NoFilter-Website/SHIP-2026-08-30f
//
// WHY
//   On 30 Aug 2026 the question "which version is live?" could not be answered without a
//   Netlify login. Every SHIP bundle from the 29th and 30th carried data-nf-build="nf-2026-08-28"
//   — that is the stamp of the SOURCE file, so it cannot tell two bundles apart. The pages had
//   no visible text differences either; 30d, 30e and 30f differ only in CSS and JS. So the live
//   site could not be identified from outside at all.
//
//   This writes the bundle's own folder name into every page and into llms.txt. After that,
//   anyone can ask the live site what it is, from any machine, with no login:
//       curl -s https://nofilter.sg | grep nf-ship
//
// Idempotent: re-running replaces the stamp rather than adding a second one.

import { readFileSync, writeFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, basename, resolve } from 'node:path';

const dir = process.argv[2];
if (!dir) { console.error('usage: nf-ship-stamp.mjs <SHIP-folder>'); process.exit(2); }
const ship = basename(resolve(dir));
if (!/^SHIP-\d{4}-\d{2}-\d{2}/.test(ship)) { console.error(`not a SHIP folder: ${ship}`); process.exit(2); }

const html = [];
(function walk(d) {
  for (const e of readdirSync(d)) {
    const p = join(d, e);
    if (statSync(p).isDirectory()) { if (e !== 'netlify' && e !== 'assets') walk(p); }
    else if (e.endsWith('.html')) html.push(p);
  }
})(resolve(dir));

const TAG = `<meta name="nf-ship" content="${ship}">`;
let stamped = 0, replaced = 0;
for (const f of html) {
  let s = readFileSync(f, 'utf8');
  const existing = /<meta name="nf-ship"[^>]*>/;
  if (existing.test(s)) { s = s.replace(existing, TAG); replaced++; }
  else if (/<head[^>]*>/i.test(s)) { s = s.replace(/<head[^>]*>/i, (m) => m + '\n' + TAG); stamped++; }
  else if (/<meta charset[^>]*>/i.test(s)) { s = s.replace(/<meta charset[^>]*>/i, (m) => m + '\n' + TAG); stamped++; }
  else { s = TAG + '\n' + s; stamped++; }
  writeFileSync(f, s);
}

const llms = join(resolve(dir), 'llms.txt');
if (existsSync(llms)) {
  let t = readFileSync(llms, 'utf8').replace(/^# build: SHIP-.*\n/m, '');
  writeFileSync(llms, `# build: ${ship}\n` + t);
  console.log('llms.txt: build line written');
}
console.log(`${ship}: ${html.length} html files — ${stamped} stamped, ${replaced} re-stamped`);
console.log(`check the live site with:  curl -s https://nofilter.sg | grep nf-ship`);
