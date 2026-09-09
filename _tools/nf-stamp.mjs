#!/usr/bin/env node
// nf-stamp.mjs — NoFilter pitch stamp engine (dependency-free, Node built-ins only)
//
// Usage:
//   node nf-stamp.mjs <master.html> <values1.json> [<values2.json> ...] [--out <file>] [--strict]
//
// Merges the value files in order (later overrides earlier) into one map, replaces every
// [[KEY]] occurrence in the master with its value, then runs the TOKEN GATE: any surviving
// [[A-Z0-9_]+]] token is reported to stderr, grouped DEPLOY-TIME (an allowlist filled at
// deploy) vs MISSING (a real problem). With --strict, exit non-zero if any MISSING remain.
//
// See _STAMP-A-PITCH.md and _TOKEN-DICTIONARY.md.

import { readFileSync, writeFileSync } from 'node:fs';
import { dirname, join } from 'node:path';
import { fileURLToPath } from 'node:url';

const PARTIALS_DIR = join(dirname(fileURLToPath(import.meta.url)), '..', '_partials');

// ── Expand [[INCLUDE:name]] with _partials/name.html BEFORE token substitution,
//    so tokens inside partials are filled too. Single source of truth for shared blocks.
function expandIncludes(html) {
  const re = /\[\[INCLUDE:([a-zA-Z0-9_-]+)\]\]/g;
  let out = html;
  for (let guard = 0; out.includes('[[INCLUDE:') && guard < 20; guard++) {
    out = out.replace(/\[\[INCLUDE:([a-zA-Z0-9_-]+)\]\]/g, (whole, name) => {
      try { return readFileSync(join(PARTIALS_DIR, `${name}.html`), 'utf8'); }
      catch (e) { throw new Error(`cannot read partial "${name}": ${e.message}`); }
    });
  }
  return out;
}

// ── Deploy-time allowlist: tokens legitimately left unfilled at stamp time and
//    supplied later at deploy (machine rate card, contract/part URLs, shared-asset base…).
const DEPLOY_TIME_PATTERNS = [
  /^RATE_CM.*$/,
  /^PURCHASE_CM.*$/,
  /^CONTRACT_URL$/,
  /^PART2_URL$/,
  /^MACHINE_COBRAND_LOGO$/,
  /^DEFAULT_MACHINE$/,
  /^DEFAULT_ORIGIN$/,
  /^DEFAULT_PATH$/,
  /^COST_PER_KG$/,
  /^SHARED_BASE$/,
];

const isDeployTime = (key) => DEPLOY_TIME_PATTERNS.some((re) => re.test(key));

// ── Parse argv ────────────────────────────────────────────────────────────────
function parseArgs(argv) {
  const positionals = [];
  let out = null;
  let strict = false;
  for (let i = 0; i < argv.length; i++) {
    const a = argv[i];
    if (a === '--out') {
      out = argv[++i];
      if (out == null) { throw new Error('--out requires a file path'); }
    } else if (a === '--strict') {
      strict = true;
    } else if (a.startsWith('--')) {
      throw new Error(`unknown flag: ${a}`);
    } else {
      positionals.push(a);
    }
  }
  if (positionals.length < 2) {
    throw new Error('need <master.html> and at least one <values.json>');
  }
  const [master, ...valueFiles] = positionals;
  return { master, valueFiles, out, strict };
}

// ── Merge value files (later overrides earlier). Keys starting with "_" are meta
//    (notes/readme) and are ignored for substitution. ───────────────────────────
function mergeValues(valueFiles) {
  const map = {};
  for (const f of valueFiles) {
    let raw;
    try {
      raw = readFileSync(f, 'utf8');
    } catch (e) {
      throw new Error(`cannot read values file ${f}: ${e.message}`);
    }
    let obj;
    try {
      obj = JSON.parse(raw);
    } catch (e) {
      throw new Error(`invalid JSON in ${f}: ${e.message}`);
    }
    for (const [k, v] of Object.entries(obj)) {
      if (k.startsWith('_')) continue; // meta key, skip
      map[k] = String(v);
    }
  }
  return map;
}

// ── Substitute every [[KEY]] present in the map. ───────────────────────────────
function stamp(html, map) {
  return html.replace(/\[\[([A-Z0-9_]+)\]\]/g, (whole, key) =>
    Object.prototype.hasOwnProperty.call(map, key) ? map[key] : whole
  );
}

// ── Token gate: find surviving [[TOKEN]]s, split deploy-time vs missing. ────────
function tokenGate(html) {
  const deploy = new Set();
  const missing = new Set();
  const re = /\[\[([A-Z0-9_]+)\]\]/g;
  let m;
  while ((m = re.exec(html)) !== null) {
    const key = m[1];
    if (isDeployTime(key)) deploy.add(key);
    else missing.add(key);
  }
  return { deploy: [...deploy].sort(), missing: [...missing].sort() };
}

// ── Main ───────────────────────────────────────────────────────────────────────
function main() {
  let args;
  try {
    args = parseArgs(process.argv.slice(2));
  } catch (e) {
    process.stderr.write(`nf-stamp: ${e.message}\n\n` +
      'Usage: node nf-stamp.mjs <master.html> <values1.json> [<values2.json> ...] [--out <file>] [--strict]\n');
    process.exit(2);
  }

  let html;
  try {
    html = readFileSync(args.master, 'utf8');
  } catch (e) {
    process.stderr.write(`nf-stamp: cannot read master ${args.master}: ${e.message}\n`);
    process.exit(2);
  }

  let map;
  try {
    map = mergeValues(args.valueFiles);
  } catch (e) {
    process.stderr.write(`nf-stamp: ${e.message}\n`);
    process.exit(2);
  }

  let withIncludes;
  try { withIncludes = expandIncludes(html); }
  catch (e) { process.stderr.write(`nf-stamp: ${e.message}\n`); process.exit(2); }
  const filled = stamp(withIncludes, map);
  const { deploy, missing } = tokenGate(filled);

  // ── TOKEN GATE report (stderr) ──
  process.stderr.write('── TOKEN GATE ──\n');
  process.stderr.write(`DEPLOY-TIME (${deploy.length}, filled at deploy — OK):\n`);
  if (deploy.length) {
    for (const k of deploy) process.stderr.write(`  [[${k}]]\n`);
  } else {
    process.stderr.write('  (none)\n');
  }
  process.stderr.write(`MISSING (${missing.length}, real problem):\n`);
  if (missing.length) {
    for (const k of missing) process.stderr.write(`  [[${k}]]\n`);
  } else {
    process.stderr.write('  (none)\n');
  }

  // ── Write output ──
  if (args.out) {
    try {
      writeFileSync(args.out, filled);
    } catch (e) {
      process.stderr.write(`nf-stamp: cannot write ${args.out}: ${e.message}\n`);
      process.exit(2);
    }
    process.stderr.write(`\nwrote ${args.out}\n`);
  } else {
    process.stdout.write(filled);
  }

  if (args.strict && missing.length) {
    process.stderr.write(`\nnf-stamp: --strict: ${missing.length} MISSING token(s) remain\n`);
    process.exit(1);
  }
}

main();
