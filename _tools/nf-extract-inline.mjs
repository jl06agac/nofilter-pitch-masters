#!/usr/bin/env node
// nf-extract-inline.mjs — pull big base64 images out of a stamped build into real files.
//
//   node nf-extract-inline.mjs <stamped.html> --out <file> [--assets <dir>] [--min <bytes>]
//
// WHY
//   The masters carry their hero photography inline as base64 so a master is a single
//   self-contained file that cannot lose its images. That is right for a master and wrong
//   for a deployed page: base64 is ~33% bigger than the bytes it encodes, it cannot be
//   cached separately, it cannot be fetched in parallel, and the browser must parse the
//   whole lot before it can render anything. On the Sprinklr build that was 1,066 KB of a
//   1,745 KB file — 61% of the HTML was three photographs.
//
//   This runs AFTER the stamp (and after nf-strip-builder), writes each large image to
//   assets/ under a content-hashed name, and rewrites the reference. Same pixels, same
//   page, a third of the parse. Small inlines are left alone: below the threshold an extra
//   HTTP request costs more than it saves.
//
// Content-hashed names mean re-running it is idempotent and two clients sharing an image
// share a filename.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname } from 'node:path';
import { createHash } from 'node:crypto';

const args = process.argv.slice(2);
const get = (flag, dflt) => { const i = args.indexOf(flag); return i > -1 ? args[i + 1] : dflt; };
const src = args.find((a) => !a.startsWith('--') && a !== get('--out') && a !== get('--assets') && a !== get('--min'));
const out = get('--out');
const MIN = parseInt(get('--min', '20000'), 10);   // bytes of base64 text, not decoded size

if (!src || !out) {
  process.stderr.write('usage: node nf-extract-inline.mjs <stamped.html> --out <file> [--assets <dir>] [--min <bytes>]\n');
  process.exit(2);
}

const assetsDir = get('--assets', join(dirname(out), 'assets'));
if (!existsSync(assetsDir)) mkdirSync(assetsDir, { recursive: true });

const EXT = {
  'image/jpeg': 'jpg', 'image/jpg': 'jpg', 'image/png': 'png',
  'image/webp': 'webp', 'image/gif': 'gif', 'image/svg+xml': 'svg',
};

const html = readFileSync(src, 'utf8');
const before = Buffer.byteLength(html);
const written = [];

const outHtml = html.replace(/data:([a-z/+]+);base64,([A-Za-z0-9+/=]+)/g, (whole, mime, b64) => {
  const ext = EXT[mime];
  if (!ext || b64.length < MIN) return whole;          // unknown type, or too small to be worth a request
  const raw = Buffer.from(b64, 'base64');
  const name = `inline-${createHash('md5').update(raw).digest('hex').slice(0, 10)}.${ext}`;
  const dest = join(assetsDir, name);
  if (!existsSync(dest)) writeFileSync(dest, raw);
  written.push([name, raw.length]);
  return `assets/${name}`;
});

writeFileSync(out, outHtml);
const after = Buffer.byteLength(outHtml);

process.stderr.write(`nf-extract-inline: ${(before / 1024).toFixed(0)} KB -> ${(after / 1024).toFixed(0)} KB `
  + `(${((before - after) / 1024).toFixed(0)} KB moved into ${written.length} file(s))\n`);
for (const [n, b] of written) process.stderr.write(`  ${n}  ${(b / 1024).toFixed(1)} KB\n`);
if (!written.length) process.stderr.write('  (nothing above the threshold — file unchanged in substance)\n');
process.stderr.write(`wrote ${out}\n`);
