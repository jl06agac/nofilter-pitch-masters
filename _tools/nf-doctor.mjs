#!/usr/bin/env node
// nf-doctor.mjs — NoFilter workspace integrity check (dependency-free, Node built-ins only)
//
//   node DO-NOT-TOUCH-Claude-files/_tools/nf-doctor.mjs [extraRoot ...] [--quiet] [--json]
//
// Every guardrail in this workspace is a RULE A HUMAN HAS TO FOLLOW. This is a CHECK THAT RUNS.
// It exists because on 7 Aug 2026 three things were true at once and nothing noticed:
//   * two different files both named NoFilter-Generic-Part2-SG.html, 30KB apart, both labelled v256
//   * an SOP note asserting which of them was canonical, which had been wrong for a month
//   * the Part 2 master shipping Accenture's logo geometry and brand purple to every new client
//
// Exit 1 if any ERROR. Exit 0 on WARN/INFO only.

import { readFileSync, readdirSync, statSync, existsSync } from 'node:fs';
import { join, resolve, basename, dirname, relative, extname } from 'node:path';
import { homedir } from 'node:os';

// ── locate the workspace root (the dir holding DO-NOT-TOUCH-Claude-files) ─────
function findRoot(from) {
  let d = resolve(from);
  for (let i = 0; i < 8; i++) {
    if (existsSync(join(d, 'DO-NOT-TOUCH-Claude-files'))) return d;
    const up = dirname(d);
    if (up === d) break;
    d = up;
  }
  throw new Error('cannot find the NoFilter workspace root from ' + from);
}
const ROOT = findRoot(process.argv[1] || process.cwd());

const args    = process.argv.slice(2);
const QUIET   = args.includes('--quiet');
const AS_JSON = args.includes('--json');
const EXTRA   = args.filter(a => !a.startsWith('--')).map(p => resolve(p.replace(/^~/, homedir())));

// Scan the workspace plus the scratch areas that sit OUTSIDE it — that is where the
// duplicates breed, and it is the blind spot the nf-guard hook cannot see into.
const SCRATCH = [join(homedir(), 'Desktop'), join(homedir(), 'Downloads'), join(homedir(), 'Documents')]
  .filter(existsSync);
// A scratch root often CONTAINS the workspace (~/Desktop/NoFilter). Scanning both would
// double every file and invent duplicates that do not exist. Drop any root nested in another.
const ROOTS = (() => {
  const all = [...new Set([ROOT, ...SCRATCH, ...EXTRA].map(p => resolve(p)))];
  return all.filter(a => !all.some(b => b !== a && a.startsWith(b + '/')));
})();

const SKIP_DIR = new Set(['node_modules', '.git', '.netlify', '_to_delete', 'Screenshots',
                          '.Trash', 'Library', '.cache', '_CDN-UPLOAD-SAFE',
                          '_CDN-INCOMPLETE-DO-NOT-DEPLOY', '_ASSET-RESTORE']);
// A SHIP-YYYY-MM-DD<letter> folder is a BUILD OUTPUT of the website master, not authored work.
// Successive builds are supposed to differ, so comparing them against each other produces
// "two sources of truth" errors that mean nothing — with 34 of them the duplicate-name check
// reported 404.html in 14 places, and once only two remained (one carrying an nf-ship stamp)
// it escalated to an ERROR. Skipped for the same reason _CDN-UPLOAD-SAFE is: generated, not
// authored. Added 30 Aug 2026.
const SKIP_DIR_RE = /^SHIP-\d{4}-\d{2}-\d{2}[a-z]?$/;

const MAX_SCAN_BYTES = 12 * 1024 * 1024;

const findings = [];
const add = (level, check, msg, detail) => findings.push({ level, check, msg, detail: detail || [] });

// ── walk ──────────────────────────────────────────────────────────────────────
function walk(dir, out, depth = 0) {
  if (depth > 10) return out;
  let ents;
  try { ents = readdirSync(dir, { withFileTypes: true }); } catch { return out; }
  for (const e of ents) {
    if (e.name.startsWith('.') && e.name !== '.netlify') continue;
    const p = join(dir, e.name);
    if (e.isDirectory()) { if (!SKIP_DIR.has(e.name) && !SKIP_DIR_RE.test(e.name)) walk(p, out, depth + 1); }
    else if (e.isFile()) { try { out.push({ path: p, ...statSync(p) }); } catch {} }
  }
  return out;
}

const files = [];
{
  const seen = new Set();                         // (dev,ino) — a hard link is one file
  for (const r of ROOTS) {
    const batch = walk(r, []);
    for (const f of batch) {
      const k = `${f.dev}:${f.ino}`;
      if (seen.has(k)) continue;
      seen.add(k); files.push(f);
    }
  }
}
const html = files.filter(f => extname(f.path).toLowerCase() === '.html');
const read = f => { try { return f.size > MAX_SCAN_BYTES ? '' : readFileSync(f.path, 'utf8'); } catch { return ''; } };
const show = p => p.startsWith(ROOT) ? relative(ROOT, p) : p.replace(homedir(), '~');
const stripComments = s => s.replace(/<!--[\s\S]*?-->/g, ' ');

// ── CHECK 1 · the same filename in more than one place, with different bytes ──
// index.html is the deploy artifact name BY CONVENTION (one per deploy folder), so it is not a
// duplicate. A copied shared asset is not a duplicate either — but an ODD ONE OUT among those
// copies is exactly the drift worth catching, so report the minority sizes, not the whole set.
{
  const byName = new Map();
  for (const f of html) {
    if (basename(f.path) === 'index.html') continue;
    if (/\.(PRE-|WORKING-|SUPERSEDED|LIVE-)/i.test(basename(f.path))) continue;
    const k = basename(f.path);
    if (!byName.has(k)) byName.set(k, []);
    byName.get(k).push(f);
  }
  for (const [name, list] of byName) {
    if (list.length < 2) continue;
    if (new Set(list.map(f => f.ino)).size === 1) continue;          // hard links: one file, many doors
    const bySize = new Map();
    for (const f of list) { if (!bySize.has(f.size)) bySize.set(f.size, []); bySize.get(f.size).push(f); }
    if (bySize.size === 1) {
      add('INFO', 'duplicate-name', `"${name}" copied to ${list.length} places, all identical.`, []);
      continue;
    }
    const groups = [...bySize.entries()].sort((a, b) => b[1].length - a[1].length);
    const [domSize, domFiles] = groups[0];
    const outliers = groups.slice(1);
    const isMinority = outliers.reduce((n, [, g]) => n + g.length, 0) <= domFiles.length;
    const fmt = f => `${String(f.size).padStart(9)} bytes  ${new Date(f.mtimeMs).toISOString().slice(0,10)}  ${show(f.path)}`;
    if (isMinority && domFiles.length >= 3) {
      add('WARN', 'duplicate-name',
        `"${name}" has ${domFiles.length} identical copies (${domSize} bytes) and ` +
        `${outliers.reduce((n,[,g])=>n+g.length,0)} that differ. The odd ones out have drifted.`,
        outliers.flatMap(([, g]) => g.map(fmt)));
    } else {
      add('ERROR', 'duplicate-name',
        `"${name}" exists in ${list.length} places with DIFFERENT contents. Two sources of truth.`,
        list.sort((a, b) => b.mtimeMs - a.mtimeMs).slice(0, 8).map(fmt));
    }
  }
}

// ── CHECK 1b · a WORKING file named index.html (the name is reserved for deploys) ──
{
  for (const f of html.filter(f => basename(f.path) === 'index.html' && f.path.startsWith(join(ROOT, 'Clients')))) {
    const d = dirname(f.path);
    if (/deploy|_live|dist|public|build/i.test(basename(d))) continue;   // a real deploy folder
    if (existsSync(join(d, '.netlify'))) continue;
    add('WARN', 'reserved-name',
      `${show(f.path)} is named index.html but is not in a deploy folder. That name has caused overwrites.`, []);
  }
}

// ── CHECK 2 · the same version label on more than one distinct file ───────────
{
  const byVer = new Map();
  for (const f of html) {
    const s = read(f); if (!s) continue;
    for (const m of new Set((s.match(/\bv\d{2,4}\b/g) || []))) {
      if (!byVer.has(m)) byVer.set(m, new Map());
      byVer.get(m).set(f.path, f.size);
    }
  }
  for (const [ver, hits] of byVer) {
    if (hits.size < 2) continue;
    if (new Set(hits.values()).size < 2) continue;         // same bytes: a copy, not a fork
    const rows = [...hits].sort((a,b) => b[1]-a[1]).map(([p, sz]) => `${String(sz).padStart(9)} bytes  ${show(p)}`);
    add('ERROR', 'version-collision',
      `Version label "${ver}" appears on ${hits.size} files across ${new Set(hits.values()).size} distinct sizes. ` +
      `The label cannot identify a build — use the path.`,
      rows.slice(0, 6).concat(rows.length > 6 ? [`… and ${rows.length - 6} more`] : []));
  }
}

// ── CHECK 3 · paths asserted in the SOPs that are wrong ──────────────────────
{
  const md = files.filter(f => f.path.startsWith(ROOT) && extname(f.path) === '.md');
  const newestByName = new Map();
  for (const f of html) {
    const k = basename(f.path), cur = newestByName.get(k);
    if (!cur || f.mtimeMs > cur.mtimeMs) newestByName.set(k, f);
  }
  for (const f of md) {
    const s = read(f); if (!s) continue;
    const lines = s.split('\n');
    lines.forEach((line, i) => {
      for (const m of line.matchAll(/`([~\w][^`]*?\.(?:html|json|mjs|md))`/g)) {
        const raw = m[1].trim();
        if (/[*{}<>|]|\[\[/.test(raw) || raw.includes(' ')) continue;   // globs and <Client> placeholders are prose
        if (/^https?:/.test(raw)) continue;
        // Resolve against the doc's own folder first, then each parent up to ROOT, then ROOT
        // itself. A runbook inside _Part2-Master/ writes `_tools/nf-stamp.mjs` meaning
        // ../_tools/…, and treating that as broken is a false alarm that trains you to
        // ignore the checker — the worst outcome for a tool like this.
        const bases = [];
        for (let d = dirname(f.path); d.startsWith(ROOT); d = dirname(d)) bases.push(d);
        bases.push(ROOT);
        const abs = raw.startsWith('~') ? raw.replace(/^~/, homedir())
                  : raw.startsWith('/') ? raw
                  : (bases.map(b => join(b, raw)).find(existsSync) || join(ROOT, raw));
        const where = `${show(f.path)}:${i + 1}`;
        if (!existsSync(abs)) {
          // a bare filename may just be prose; only flag paths that look like locations
          if (!raw.includes('/') && !raw.startsWith('~')) continue;
          if (/\be\.g\.|for example|such as/i.test(line)) continue;   // an illustrative path, not a claim
          // Does it exist SOMEWHERE else? Then the doc is not lying, it is just naming the
          // wrong prefix — say where it actually is, so the fix is one edit rather than a hunt.
          const tail = raw.replace(/^~\//, '').replace(/^NoFilter\//, '');
          const actual = files.filter(x => x.path.endsWith('/' + tail) && !/_to_delete|_archive/.test(x.path));
          if (actual.length) {
            add('WARN', 'stale-doc-path',
              `${where} says \`${raw}\`, which does not resolve. It actually lives at: ` +
              actual.slice(0, 2).map(x => show(x.path)).join(' · '), [line.trim().slice(0, 150)]);
          } else {
            add('ERROR', 'stale-doc-path',
              `${where} points at a file that exists nowhere: ${raw}`, [line.trim().slice(0, 150)]);
          }
          continue;
        }
        const newest = newestByName.get(basename(abs));
        if (newest && resolve(newest.path) !== resolve(abs) && newest.mtimeMs > statSync(abs).mtimeMs + 60000) {
          add('WARN', 'stale-doc-path',
            `${where} points at ${raw}, but a newer file of the same name exists elsewhere.`,
            [`doc points at : ${show(abs)}  (${new Date(statSync(abs).mtimeMs).toISOString().slice(0,10)})`,
             `newer copy    : ${show(newest.path)}  (${new Date(newest.mtimeMs).toISOString().slice(0,10)})`]);
        }
      }
    });
  }
}

// ── CHECK 4 · a build carrying another client's identity ─────────────────────
{
  const clientsDir = join(ROOT, 'Clients');
  const clients = [];
  if (existsSync(clientsDir)) {
    for (const sector of readdirSync(clientsDir, { withFileTypes: true })) {
      if (!sector.isDirectory() || sector.name.startsWith('_')) continue;
      for (const c of readdirSync(join(clientsDir, sector.name), { withFileTypes: true })) {
        if (c.isDirectory() && !c.name.startsWith('_')) clients.push({ name: c.name, dir: join(clientsDir, sector.name, c.name) });
      }
    }
  }
  // identities that outlived the build they came from, plus brand colours that give them away
  const RETIRED = [
    { id: 'UWCSEA',    re: /\bUWCSEA\b/i },
    { id: 'Accenture', re: /\bAccenture\b/i },
    { id: 'Sprinklr',  re: /\bSprinklr\b/i },
    { id: 'Accenture brand purple #A100FF', re: /#A100FF\b|rgba?\(\s*161\s*,\s*0\s*,\s*255/i },
  ];
  const own = d => {
    const c = clients.find(c => d.startsWith(c.dir));
    return c ? c.name : null;
  };
  const scan = html.filter(f => f.path.startsWith(clientsDir) || f.path.startsWith(join(ROOT, 'DO-NOT-TOUCH-Claude-files')));
  for (const f of scan) {
    const raw = read(f); if (!raw) continue;
    const s = stripComments(raw);              // provenance comments are honest, not leaks
    const mine = own(f.path);
    const hits = [];
    for (const r of RETIRED) {
      if (mine && r.id.toLowerCase().startsWith(mine.toLowerCase())) continue;
      const n = (s.match(new RegExp(r.re.source, 'gi')) || []).length;
      if (n) hits.push(`${r.id} ×${n}`);
    }
    for (const c of clients) {
      if (mine && c.name === mine) continue;
      if (RETIRED.some(r => r.id.toLowerCase().startsWith(c.name.toLowerCase()))) continue;
      const n = (s.match(new RegExp('\\b' + c.name.replace(/[.*+?^${}()|[\]\\]/g,'\\$&') + '\\b', 'gi')) || []).length;
      if (n > 1) hits.push(`${c.name} ×${n}`);
    }
    if (!hits.length) continue;
    const isMaster = f.path.includes('DO-NOT-TOUCH-Claude-files');
    const isDonorOrArchive = /_device-donor|_archive|_staging/.test(f.path);
    if (isDonorOrArchive) continue;
    add(isMaster ? 'ERROR' : 'WARN', 'foreign-identity',
      `${show(f.path)}${mine ? ` (a ${mine} file)` : ''} carries: ${hits.join(', ')}` +
      (isMaster ? ' — a master leaks this into EVERY future stamp.' : ''), []);
  }
}

// ── CHECK 5 · a _TEMPLATE with a real client baked into it ───────────────────
{
  for (const f of html.filter(f => /_TEMPLATE/.test(f.path))) {
    const s = stripComments(read(f)); if (!s) continue;
    const named = /Auckland|UWCSEA|Accenture|Sprinklr|Dulwich|Tanglin|Eastspring|Bronx|Taronga|Perth/gi;
    const hits = s.match(named) || [];
    if (hits.length > 3) {
      const tally = {}; hits.forEach(h => { const k = h.toLowerCase(); tally[k] = (tally[k]||0)+1; });
      add('ERROR', 'branded-template',
        `${show(f.path)} is in a _TEMPLATE folder but carries a real client identity ` +
        `(${Object.entries(tally).map(([k,v]) => `${k} ×${v}`).join(', ')}). ` +
        `A branded template becomes a rogue second source of truth.`, []);
    }
  }
}

// ── CHECK 6 · unfilled tokens in a client build ──────────────────────────────
{
  const DEPLOY_OK = [/^RATE_CM/, /^PURCHASE_CM/, /^CONTRACT_URL$/, /^PART2_URL$/, /^MACHINE_COBRAND_LOGO$/,
                     /^DEFAULT_MACHINE$/, /^DEFAULT_ORIGIN$/, /^DEFAULT_PATH$/, /^COST_PER_KG$/, /^SHARED_BASE$/];
  for (const f of html.filter(f => f.path.startsWith(join(ROOT, 'Clients')) && !/_archive|_to_delete/.test(f.path))) {
    const s = read(f); if (!s) continue;
    const toks = [...new Set((s.match(/\[\[([A-Z0-9_]+)\]\]/g) || []).map(t => t.slice(2, -2)))]
      .filter(t => !DEPLOY_OK.some(re => re.test(t)));
    if (toks.length) add('ERROR', 'unfilled-token', `${show(f.path)} still has ${toks.length} unfilled token(s): ${toks.join(', ')}`, []);
    const ph = [...new Set(s.match(/\[[^\][]{0,60}?(?:to confirm|replace me|TBD|placeholder)[^\][]{0,20}?\]/gi) || [])];
    if (ph.length) add('WARN', 'placeholder', `${show(f.path)} still shows placeholder copy: ${ph.slice(0,4).join(' · ')}`, []);
  }
}

// ── report ────────────────────────────────────────────────────────────────────
const order = { ERROR: 0, WARN: 1, INFO: 2 };
findings.sort((a, b) => order[a.level] - order[b.level] || a.check.localeCompare(b.check));
const counts = findings.reduce((m, f) => (m[f.level] = (m[f.level] || 0) + 1, m), {});

if (AS_JSON) {
  console.log(JSON.stringify({ root: ROOT, scanned: { files: files.length, html: html.length }, counts, findings }, null, 2));
} else {
  const C = { ERROR: '\x1b[31m', WARN: '\x1b[33m', INFO: '\x1b[36m', off: '\x1b[0m', dim: '\x1b[2m' };
  console.log(`\nnf-doctor — ${ROOT}`);
  console.log(`${C.dim}scanned ${files.length} files (${html.length} html) across ${ROOTS.length} roots${C.off}\n`);
  let last = '';
  for (const f of findings) {
    if (QUIET && f.level === 'INFO') continue;
    if (f.check !== last) { console.log(`${C.dim}── ${f.check} ${'─'.repeat(Math.max(0, 60 - f.check.length))}${C.off}`); last = f.check; }
    console.log(`${C[f.level]}${f.level.padEnd(5)}${C.off} ${f.msg}`);
    for (const d of f.detail) console.log(`        ${C.dim}${d}${C.off}`);
  }
  if (!findings.length) console.log('clean — nothing to report.\n');
  else console.log(`\n${counts.ERROR || 0} error(s) · ${counts.WARN || 0} warning(s) · ${counts.INFO || 0} note(s)\n`);
}

process.exit((counts.ERROR || 0) > 0 ? 1 : 0);
