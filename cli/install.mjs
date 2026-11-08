#!/usr/bin/env node
import { createHash, randomUUID } from 'node:crypto';
import { lstatSync, readFileSync, mkdirSync, writeFileSync, renameSync, unlinkSync, realpathSync } from 'node:fs';
import { homedir } from 'node:os';
import { dirname, join, resolve } from 'node:path';
import { spawnSync } from 'node:child_process';
import { fileURLToPath } from 'node:url';

export const MARKETPLACE = 'edgex-agents';
export const SOURCE = 'https://github.com/KashyapSinh-Gohil/edgex-agents.git';
export const REF = 'v0.4.0';
export const PLUGIN = 'edgex@edgex-agents';
const AGENT = 'edgex-researcher.toml';
const DEFAULT_SOURCE = fileURLToPath(new URL(`../codex/${AGENT}`, import.meta.url));
export const HELP = `Usage: edgex-agent [--help] [--dry-run] [--target codex]
Install the native Codex plugin and global custom agent (~/.codex/agents/${AGENT}).
Requires Node >=18 and Codex with plugin marketplace JSON support.
From GitHub: npx --yes github:KashyapSinh-Gohil/edgex-agents#v0.4.0`;

export function parseArgs(argv) {
  const options = { help: false, dryRun: false, target: 'codex' };
  for (let i = 0; i < argv.length; i++) {
    if (argv[i] === '--help') options.help = true;
    else if (argv[i] === '--dry-run') options.dryRun = true;
    else if (argv[i] === '--target') {
      if (argv[++i] !== 'codex') throw new Error('--target supports only codex');
    } else throw new Error(`Unsupported argument: ${argv[i]}`);
  }
  return options;
}

const hash = bytes => createHash('sha256').update(bytes).digest('hex');
function stat(path) {
  try { return lstatSync(path); }
  catch (error) { if (error.code === 'ENOENT') return null; throw error; }
}

// lstat every component, including the home directory and ownership manifest.
function checkPath(path) {
  const parent = dirname(path);
  if (parent !== path) checkPath(parent);
  const entry = stat(path);
  if (entry && (entry.isSymbolicLink() || (!entry.isDirectory() && !entry.isFile()))) {
    throw new Error(`Unsafe path (symlink or special file): ${path}`);
  }
  if (parent !== path && stat(parent) && !stat(parent).isDirectory()) {
    throw new Error(`Path ancestor is not a directory: ${parent}`);
  }
  return entry;
}

export function preflightAgent({ home = homedir(), agentSource = DEFAULT_SOURCE } = {}) {
  const target = join(resolve(home), '.codex', 'agents', AGENT);
  const manifest = join(dirname(target), '.edgex-researcher.manifest.json');
  for (const path of [target, manifest]) {
    if (checkPath(path)?.isDirectory()) throw new Error(`Expected a file: ${path}`);
  }
  const bytes = readFileSync(agentSource);
  if (!bytes.length) throw new Error(`Bundled custom agent is empty: ${agentSource}`);
  const current = stat(target) ? readFileSync(target) : null;
  const recorded = stat(manifest) ? JSON.parse(readFileSync(manifest, 'utf8')) : null;
  if (recorded && (recorded.file !== AGENT || !/^[a-f0-9]{64}$/.test(recorded.sha256))) {
    throw new Error(`Invalid ownership manifest: ${manifest}`);
  }
  const changed = !current?.equals(bytes);
  if (current && changed && (!recorded || hash(current) !== recorded.sha256)) {
    throw new Error(`Refusing to replace unowned or modified custom agent: ${target}`);
  }
  return { target, manifest, bytes, changed, ownership: `${JSON.stringify({ file: AGENT, sha256: hash(bytes) })}\n` };
}

function atomicWrite(path, bytes) {
  const temporary = `${path}.${randomUUID()}.tmp`;
  writeFileSync(temporary, bytes, { flag: 'wx', mode: 0o600 });
  try { renameSync(temporary, path); }
  finally { if (stat(temporary)) unlinkSync(temporary); }
}

export function install(argv = [], { home = homedir(), run = spawnSync, agentSource = DEFAULT_SOURCE } = {}) {
  const options = parseArgs(argv);
  if (options.help) return { help: HELP };
  const call = args => run('codex', args, { shell: false, encoding: 'utf8' });
  const checked = args => {
    const result = call(args);
    if (result.error || result.status !== 0) {
      throw new Error(`codex ${args.join(' ')} failed: ${result.error?.message || result.stderr || result.status}`);
    }
    return result.stdout;
  };
  const version = call(['--version']);
  if (version.error || version.status !== 0) throw new Error('Codex is unavailable; install Codex and ensure codex is on PATH.');
  // All local conflicts must be discovered before marketplace/plugin mutations.
  let agent = preflightAgent({ home, agentSource });
  const listing = call(['plugin', 'marketplace', 'list', '--json']);
  if (listing.error || listing.status !== 0) {
    throw new Error(`Cannot inspect marketplaces; Codex must support plugin marketplace list --json. ${listing.stderr || listing.error?.message || ''}`);
  }
  const data = JSON.parse(listing.stdout);
  const markets = Array.isArray(data) ? data : data.marketplaces;
  if (!Array.isArray(markets) || markets.some(m => !m || typeof m.name !== 'string')) {
    throw new Error('Invalid marketplace JSON; refusing to mutate Codex.');
  }
  const existing = markets.filter(m => m.name === MARKETPLACE);
  if (existing.some(m => m.marketplaceSource?.sourceType !== 'git' || m.marketplaceSource.source !== SOURCE)) {
    throw new Error(`Marketplace ${MARKETPLACE} has a mismatched or unverifiable source; expected ${SOURCE}`);
  }
  const commands = [existing.length
    ? ['plugin', 'marketplace', 'upgrade', MARKETPLACE]
    : ['plugin', 'marketplace', 'add', SOURCE, '--ref', REF],
  ['plugin', 'add', PLUGIN, '--json']];
  if (!options.dryRun) {
    let installed;
    for (const args of commands) installed = checked(args);
    const receipt = JSON.parse(installed);
    if (receipt.pluginId !== PLUGIN || receipt.version !== REF.slice(1)) {
      throw new Error(`Expected ${PLUGIN} ${REF}; the marketplace is pinned to another release. Refresh the matching marketplace ref before retrying.`);
    }
    agent = preflightAgent({ home, agentSource });
    mkdirSync(dirname(agent.target), { recursive: true });
    agent = preflightAgent({ home, agentSource });
    if (agent.changed) atomicWrite(agent.target, agent.bytes);
    if (!stat(agent.manifest) || readFileSync(agent.manifest, 'utf8') !== agent.ownership) {
      atomicWrite(agent.manifest, agent.ownership);
    }
  }
  return { dryRun: options.dryRun, commands, target: agent.target, changed: agent.changed };
}

// Resolve npm's bin symlink so importing this module never starts installation.
if (process.argv[1] && realpathSync(process.argv[1]) === fileURLToPath(import.meta.url)) {
  try {
    const result = install(process.argv.slice(2));
    console.log(result.help || `${result.dryRun ? 'Dry run' : 'Installed'}:\n${result.commands.map(args => `codex ${args.join(' ')}`).join('\n')}\nCustom agent: ${result.target}`);
  } catch (error) {
    console.error(`edgex-agent: ${error.message}`);
    process.exitCode = 1;
  }
}
