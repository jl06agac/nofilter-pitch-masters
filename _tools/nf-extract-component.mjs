#!/usr/bin/env node
// nf-extract-component.mjs — copy a component OUT of the website master into its own file.
//
//   node DO-NOT-TOUCH-Claude-files/_tools/nf-extract-component.mjs [slider|quote-console|all]
//
// WHY
//   The impact slider existed in three generations at once (30 Aug 2026): 6 Jul in
//   nf-impact-standalone.html, 17 Aug in the Part 2 master, 28 Aug in the website master.
//   The 6 Jul file still called itself "the single source of truth". Nothing was wrong with
//   any of them; they were simply snapshots taken at different times and then hand-maintained,
//   and hand-maintained siblings always drift.
//
//   So: the website master is the ONLY place the component is edited. Everything else takes a
//   GENERATED copy. A generated copy carries the master's data-nf-build stamp, so nf-doctor can
//   say out loud when it has fallen behind instead of it going unnoticed for seven weeks.
//
// WHAT IT DOES NOT DO
//   It does not minimise. It errs towards taking too much rather than too little: whole <script>
//   blocks, not sliced functions, because slicing a closure in half produces a file that parses
//   and misbehaves. Per CLAUDE.md: reproduce in full, or not at all.
//
// IT CANNOT PROVE THE RESULT RENDERS. It reports what it gathered. Alex is the eyes.

import { readFileSync, writeFileSync, mkdirSync, existsSync } from 'node:fs';
import { join, dirname, resolve } from 'node:path';

const ROOT = resolve(process.argv[2]?.startsWith('/') ? process.argv[2] : findRoot(process.cwd()));
function findRoot(from) {
  let d = resolve(from);
  for (let i = 0; i < 8; i++) {
    if (existsSync(join(d, 'DO-NOT-TOUCH-Claude-files'))) return d;
    d = dirname(d);
  }
  throw new Error('could not find the NoFilter workspace root');
}
const fromIdx = process.argv.indexOf('--from');
const MASTER = fromIdx > -1 ? resolve(process.argv[fromIdx + 1])
                            : join(ROOT, 'Marketing/NoFilter-Website/NoFilter-Website-Master.html');
const SUFFIX = process.argv.indexOf('--suffix') > -1 ? process.argv[process.argv.indexOf('--suffix') + 1] : '';
const OUTDIR = join(ROOT, 'Marketing/NoFilter-Website/_components');

const COMPONENTS = {
  slider: {
    file: 'nf-impact-slider' + SUFFIX + '.generated.html',
    title: 'Impact slider',
    note: 'Three inputs (wholePrice, topUp, volCups), the morph stage, the .mgut gutter boxes and compute(). They are one component: compute() reads all three, so none can be lifted alone.',
    rootIds: ['morphStage'],
    css: ['morph', 'mgut', 'thumb-pulse', 'scale-range', 'topup-range', 'vol-range', 'lockbtn', 'mprice', 'mrow', 'uni-pin', 'mcur', 'mu'],
    js: ['morphStage', 'ensureMorph', 'wholePrice', 'volCups', 'topUp'],
  },
  'quote-console': {
    file: 'nf-quote-console' + SUFFIX + '.generated.html',
    title: 'Quote console',
    note: 'The slider plus the surrounding console: coffee grid, machine picker, form and submit.',
    rootIds: ['quote', 'morphStage'],
    css: ['morph', 'mgut', 'thumb-pulse', 'scale-range', 'topup-range', 'vol-range', 'lockbtn', 'mprice', 'mrow', 'uni-pin', 'mcur', 'q-', 'quote'],
    js: ['morphStage', 'ensureMorph', 'nfQuoteSubmit', 'quoteForm', 'quoteLines', 'wholePrice', 'volCups', 'topUp'],
  },
};

const src = readFileSync(MASTER, 'utf8');
const build = (src.match(/data-nf-build="([^"]+)"/) || [, 'UNKNOWN'])[1];

// ── blocks ───────────────────────────────────────────────────────────────────
function blocks(tag) {
  const out = [];
  const re = new RegExp(`<${tag}\\b([^>]*)>([\\s\\S]*?)</${tag}>`, 'gi');
  let m;
  while ((m = re.exec(src))) out.push({ attrs: m[1], body: m[2], index: m.index });
  return out;
}
const STYLES = blocks('style');
const SCRIPTS = blocks('script').filter((s) => !/\bsrc\s*=/.test(s.attrs));

// ── css: keep rules whose selector mentions a needle; always keep token + font blocks ────
function pickCss(css, needles) {
  // NOTE: lastEnd is LOCAL. It was module-level in the first version, which the
  // recursion below corrupted the moment an @media block appeared — selectors
  // after the first at-rule were sliced from the wrong offset and whole token
  // blocks silently vanished. Found 30 Aug 2026 by checking for undefined vars.
  const kept = [];
  let i = 0, depth = 0, start = 0, lastEnd = 0;
  while (i < css.length) {
    const c = css[i];
    if (c === '{') { if (depth === 0) start = i; depth++; }
    else if (c === '}') {
      depth--;
      if (depth === 0) {
        // strip leading comments: a /* ... */ banner above a rule was being treated
        // as part of its selector, so `:root` blocks under a section banner failed
        // the alwaysKeep test and their tokens were dropped. Found 30 Aug 2026.
        const rawSel = css.slice(lastEnd, start);
        const sel = rawSel.replace(/\/\*[\s\S]*?\*\//g, '').trim();
        const body = css.slice(start, i + 1);
        const isAt = sel.startsWith('@');
        const alwaysKeep = /^:root/.test(sel) || /@font-face/.test(sel) || /^html\b/.test(sel) || /^body\b/.test(sel);
        const hit = needles.some((n) => sel.toLowerCase().includes(n.toLowerCase()));
        if (isAt && !/@font-face/.test(sel)) {
          const inner = pickCss(body.slice(1, -1), needles);
          if (inner.trim()) kept.push(`${sel}{\n${inner}\n}`);
        } else if (hit || alwaysKeep) kept.push(sel + body);
        lastEnd = i + 1;
      }
    }
    i++;
  }
  return kept.join('\n');
}
function pick(css, needles) { return pickCss(css, needles); }

// ── markup: balanced subtree from an element id ──────────────────────────────
function subtree(id) {
  const at = src.search(new RegExp(`<[a-zA-Z]+[^>]*\\bid="${id}"`));
  if (at < 0) return null;
  const tag = (src.slice(at).match(/^<([a-zA-Z]+)/) || [])[1];
  if (!tag) return null;
  const open = new RegExp(`<${tag}\\b`, 'gi'), close = new RegExp(`</${tag}>`, 'gi');
  open.lastIndex = at; close.lastIndex = at;
  let depth = 0, i = at;
  while (i < src.length) {
    open.lastIndex = i; close.lastIndex = i;
    const o = open.exec(src), c = close.exec(src);
    if (!c) break;
    if (o && o.index < c.index) { depth++; i = o.index + 1; }
    else { depth--; i = c.index + 1; if (depth === 0) return src.slice(at, c.index + c[0].length); }
  }
  return null;
}


// ── resolve custom properties the component uses but does not define ─────────
// Harvesting rule 4: bring the dependencies, or it silently renders as a fallback.
// Iterates because a token's value can itself reference another token.
const ALLCSS = STYLES.map((s) => s.body).join('\n');
function resolveVars(css) {
  const extra = [];
  for (let pass = 0; pass < 6; pass++) {
    const body = css + '\n' + extra.join('\n');
    const used = new Set([...body.matchAll(/var\((--[a-zA-Z0-9_-]+)/g)].map((m) => m[1]));
    const def = new Set([...body.matchAll(/(--[a-zA-Z0-9_-]+)\s*:/g)].map((m) => m[1]));
    const missing = [...used].filter((v) => !def.has(v));
    if (!missing.length) break;
    let found = 0;
    for (const v of missing) {
      const re = new RegExp(`(${v}\\s*:[^;{}]+);`);
      const m = ALLCSS.match(re);
      if (m) { extra.push(`  ${m[1]};`); found++; }
    }
    if (!found) break;
  }
  return extra.length ? `/* tokens pulled in so nothing falls back — harvesting rule 4 */\n:root{\n${extra.join('\n')}\n}\n` : '';
}

mkdirSync(OUTDIR, { recursive: true });
const report = [];
const which = (process.argv.find((a) => COMPONENTS[a]) || 'all');
for (const [name, C] of Object.entries(COMPONENTS)) {
  if (which !== 'all' && which !== name) continue;
  let css = STYLES.map((s) => pick(s.body, C.css)).filter((x) => x.trim()).join('\n\n');
  css = resolveVars(css) + css;
  const marks = C.rootIds.map((id) => ({ id, html: subtree(id) }));
  const js = SCRIPTS.filter((s) => C.js.some((n) => s.body.includes(n)));
  const missing = marks.filter((m) => !m.html).map((m) => m.id);

  const out = `<!doctype html>
<meta charset="utf-8">
<title>NoFilter — ${C.title} (generated)</title>
<!--
  ════════════════════════════════════════════════════════════════════════
  GENERATED FILE — DO NOT EDIT THIS FILE.
  Source        : Marketing/NoFilter-Website/NoFilter-Website-Master.html
  Source build  : ${build}
  Generated     : ${new Date().toISOString().slice(0, 10)} by _tools/nf-extract-component.mjs
  ════════════════════════════════════════════════════════════════════════
  ${C.note}

  To change this component, change the website master and run the extractor again.
  Editing this file directly recreates the exact problem it exists to prevent.
  nf-doctor compares the source build above against the master's current
  data-nf-build and reports this file as stale when they differ.
-->
<style>
${css}
</style>

${marks.map((m) => `<!-- markup: #${m.id} -->\n${m.html || `<!-- NOT FOUND: #${m.id} -->`}`).join('\n\n')}

${js.map((s, i) => `<script${s.attrs}>\n${s.body}\n</script>`).join('\n\n')}
`;
  writeFileSync(join(OUTDIR, C.file), out);
  report.push({ name, file: C.file, bytes: out.length, cssBytes: css.length,
    markup: marks.map((m) => `${m.id}:${m.html ? m.html.length + 'b' : 'MISSING'}`).join(' '),
    scripts: js.length, scriptBytes: js.reduce((a, s) => a + s.body.length, 0), missing });
}
console.log(`master build: ${build}`);
console.log(`style blocks scanned: ${STYLES.length}   script blocks scanned: ${SCRIPTS.length}\n`);
for (const r of report) {
  console.log(`${r.file}`);
  console.log(`   total ${r.bytes} b   css ${r.cssBytes} b   scripts ${r.scripts} blocks / ${r.scriptBytes} b`);
  console.log(`   markup ${r.markup}`);
  if (r.missing.length) console.log(`   ⚠ MISSING ROOTS: ${r.missing.join(', ')}`);
}
