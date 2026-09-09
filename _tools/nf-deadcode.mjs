#!/usr/bin/env node
// nf-deadcode.mjs — find code in a built page that cannot possibly do anything.
//   node _tools/nf-deadcode.mjs <file.html> [--fix]
// Without --fix it only reports. With --fix it removes ONLY the SAFE categories and
// writes a dated .bak first.
//
// THE TEST FOR A DEAD SELECTOR (deliberately conservative)
//   A class/id is dead only if its name appears NOWHERE outside <style> blocks: not in the
//   markup and not in any line of JavaScript. So a class added at runtime by classList.add,
//   or built inside a template string, still counts as live. This misses some genuinely dead
//   rules. That bias is intended: under-removing costs bytes, over-removing costs a rendering
//   bug nobody notices until a client opens the page.
import { readFileSync, writeFileSync, copyFileSync } from 'node:fs';
const FILE = process.argv[2];
const FIX = process.argv.includes('--fix');
const WITH_DUPES = process.argv.includes('--with-dupes');
if (!FILE) { console.error('usage: nf-deadcode.mjs <file.html> [--fix]'); process.exit(2); }
let src = readFileSync(FILE, 'utf8');
const ORIG = src.length;
const styleRe = /<style\b[^>]*>([\s\S]*?)<\/style>/gi;
const styles = [...src.matchAll(styleRe)];
const outside = src.replace(styleRe, ' ');
function rules(css) {
  const out = []; let depth = 0, start = 0, i = 0, last = 0;
  while (i < css.length) {
    const c = css[i];
    if (c === '{') { if (depth === 0) start = i; depth++; }
    else if (c === '}') { depth--; if (depth === 0) { out.push({ head: css.slice(last, start), body: css.slice(start, i + 1), from: last, to: i + 1 }); last = i + 1; } }
    i++;
  }
  return out;
}
const clean = (h) => h.replace(/\/\*[\s\S]*?\*\//g, '').trim();
const esc = (s) => s.replace(/[-[\]{}()*+?.,\\^$|#]/g, '\\$&');


// ── class-name prefixes that JS assembles at runtime ────────────────────────
// className = 'mgut mgut--' + side  never puts the literal "mgut--l" in the file, so the
// plain absence test calls .mgut--l::before dead and deletes the slider's gutter boxes.
// Found 30 Aug 2026 while auditing the website master. Any selector whose class starts with
// one of these prefixes is treated as live.
const BUILT = [...src.matchAll(/(?:className\s*=|classList\.(?:add|remove|toggle)\()\s*['"`]([\w -]+)['"`]\s*\+/g)]
  .flatMap((m) => m[1].split(/\s+/).filter(Boolean));
const builtPrefix = (n) => BUILT.some((b) => n.startsWith(b));
if (BUILT.length) console.log('runtime-assembled class prefixes protected: ' + [...new Set(BUILT)].join(', '));

const dead = [], empty = [], dup = [], seen = new Set();
for (const s of styles) {
  for (const r of rules(s[1])) {
    const head = clean(r.head);
    if (!head || head.startsWith('@')) continue;
    if (/^\{\s*\}$/.test(r.body.trim())) { empty.push(head); continue; }
    const key = head + '|' + r.body.replace(/\s+/g, '');
    if (seen.has(key)) { dup.push(head); continue; }
    seen.add(key);
    const names = [...head.matchAll(/[.#]([A-Za-z_][\w-]*)/g)].map((m) => m[1]);
    if (!names.length) continue;
    if (names.some(builtPrefix)) continue;   // assembled at runtime — cannot prove it is dead
    if (names.every((n) => !new RegExp('(^|[^\\w-])' + esc(n) + '([^\\w-]|$)').test(outside))) {
      dead.push({ head, bytes: r.body.length + r.head.length, names: [...new Set(names)] });
    }
  }
}
const usedVar = new Set([...src.matchAll(/var\((--[\w-]+)\s*\)/g)].map((m) => m[1]));
const defVar = new Set([...src.matchAll(/(--[\w-]+)\s*:/g)].map((m) => m[1]));
const undef = [...usedVar].filter((v) => !defVar.has(v));
const domIds = new Set([...src.matchAll(/\bid="([\w-]+)"/g)].map((m) => m[1]));
const fetched = new Set([...src.matchAll(/getElementById\(\s*['"]([\w-]+)['"]/g)].map((m) => m[1]));
const ghost = [...fetched].filter((i) => !domIds.has(i));
const fns = [...new Set([...src.matchAll(/\bfunction\s+([A-Za-z_]\w*)\s*\(/g)].map((m) => m[1]))];
const uncalled = fns.filter((f) => (src.match(new RegExp('\\b' + esc(f) + '\\b', 'g')) || []).length < 2);
const say = (t, n, x = '') => console.log(String(n).padStart(6) + '  ' + t + x);
console.log('\n' + FILE + ' — ' + ORIG.toLocaleString() + ' bytes\n' + '-'.repeat(70));
say('SAFE  empty rules', empty.length);
say('SAFE  exact duplicate rules', dup.length);
say('SAFE  rules whose every class/id appears nowhere outside CSS', dead.length, '  (' + dead.reduce((a, d) => a + d.bytes, 0).toLocaleString() + ' bytes)');
say('CHECK custom props used with no fallback, never defined', undef.length, undef.length ? '  ' + undef.join(', ') : '');
say('CHECK getElementById targets with no matching element', ghost.length, ghost.length ? '  ' + ghost.slice(0, 12).join(', ') : '');
say('CHECK functions declared but never referenced again', uncalled.length, uncalled.length ? '  ' + uncalled.slice(0, 12).join(', ') : '');
console.log('\ndead-rule selectors (largest 25):');
dead.sort((a, b) => b.bytes - a.bytes).slice(0, 25).forEach((d) => console.log('  ' + String(d.bytes).padStart(6) + ' b  ' + d.head.slice(0, 92)));
if (dead.length > 25) console.log('  … and ' + (dead.length - 25) + ' more');
if (FIX) {
  const bak = FILE.replace(/\.html$/, '.PRE-DEADCODE-' + new Date().toISOString().slice(0, 10) + '.html.bak');
  copyFileSync(FILE, bak);
  const kill = new Set(dead.map((d) => d.head));
  const seenFix = new Set();          // for dropping exact duplicates, keeping the first
  let removed = 0, dropDup = 0, dropDead = 0;
  src = src.replace(styleRe, (whole, css) => {
    const open = whole.slice(0, whole.indexOf('>') + 1);
    let out = '', last = 0;
    for (const r of rules(css)) {
      const head = clean(r.head);
      const isEmpty = /^\{\s*\}$/.test(r.body.trim());
      const key = head + '|' + r.body.replace(/\s+/g, '');
      // Duplicate removal is OFF by default and needs --with-dupes.
      // Two byte-identical rules are NOT always redundant: if a conflicting rule with the
      // same selector sits between them, the later copy is what overrides it, and dropping
      // the later copy lets the middle rule win. On this file 13 of the 109 duplicate pairs
      // had exactly that shape. Found 30 Aug 2026, after removing them once and checking.
      const isDupe = WITH_DUPES && head && !head.startsWith('@') && seenFix.has(key);
      if (head && !head.startsWith('@')) seenFix.add(key);
      if (head && !head.startsWith('@') && (isEmpty || kill.has(head) || isDupe)) {
        removed += r.to - r.from; if (isDupe) dropDup++; else dropDead++;
      } else out += css.slice(r.from, r.to);
      last = r.to;
    }
    return open + out + css.slice(last) + '</style>';
  });
  writeFileSync(FILE, src);
  console.log('\nbackup: ' + bak);
  console.log('removed ' + dropDead + ' dead + ' + dropDup + ' duplicate rules = ' + removed.toLocaleString() + ' bytes');
  console.log(ORIG.toLocaleString() + ' -> ' + src.length.toLocaleString() + ' bytes');
}
