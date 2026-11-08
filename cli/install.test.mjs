import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, writeFileSync, readFileSync, readdirSync, realpathSync, rmSync, symlinkSync, statSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { dirname, join } from 'node:path';
import { spawnSync } from 'node:child_process';
import { install, preflightAgent, parseArgs, SOURCE, REF, MARKETPLACE, PLUGIN } from './install.mjs';

function fixture(t, marketplaces = []) {
  // macOS /var is a symlink: canonicalize the temporary root, never use real config.
  const root = mkdtempSync(join(realpathSync(tmpdir()), 'edgex-install-'));
  t.after(() => rmSync(root, { recursive: true, force: true }));
  const home = join(root, 'home');
  const agentSource = join(root, 'agent.toml');
  mkdirSync(home);
  writeFileSync(agentSource, 'name = "edgex-researcher"\n');
  const calls = [];
  const run = (command, args, options) => {
    calls.push(args);
    assert.equal(command, 'codex');
    assert.equal(options.shell, false);
    return { status: 0, stdout: args.includes('--json') ? JSON.stringify(args[0] === 'plugin' && args[1] === 'add' ? { pluginId: PLUGIN, version: REF.slice(1) } : { marketplaces }) : 'codex-cli test', stderr: '' };
  };
  const deps = { home, agentSource, run };
  const target = join(home, '.codex', 'agents', 'edgex-researcher.toml');
  return { root, target, deps, calls, put(bytes) { mkdirSync(dirname(target), { recursive: true }); writeFileSync(target, bytes); } };
}

test('dry run plans pinned GitHub install without writes or mutating commands', t => {
  const f = fixture(t);
  const result = install(['--dry-run', '--target', 'codex'], f.deps);
  assert.deepEqual(result.commands, [
    ['plugin', 'marketplace', 'add', SOURCE, '--ref', REF], ['plugin', 'add', PLUGIN, '--json'],
  ]);
  assert.deepEqual(f.calls, [['--version'], ['plugin', 'marketplace', 'list', '--json']]);
  assert.deepEqual(readdirSync(f.deps.home), []);
});

test('different unowned file fails before any marketplace mutation, even dry run', t => {
  for (const argv of [[], ['--dry-run']]) {
    const f = fixture(t);
    f.put('user content');
    assert.throws(() => install(argv, f.deps), /unowned or modified/);
    assert.deepEqual(f.calls, [['--version']]);
    assert.equal(readFileSync(f.target, 'utf8'), 'user content');
  }
});

test('identical unowned bytes are accepted and repeat installs preserve file and manifest', t => {
  const f = fixture(t);
  f.put(readFileSync(f.deps.agentSource));
  assert.equal(install([], f.deps).changed, false);
  const manifest = preflightAgent(f.deps).manifest;
  const before = [statSync(f.target).mtimeMs, statSync(manifest).mtimeMs];
  assert.equal(install([], f.deps).changed, false);
  assert.deepEqual([statSync(f.target).mtimeMs, statSync(manifest).mtimeMs], before);
});

test('managed bytes can update; user edits cannot', t => {
  const f = fixture(t);
  install([], f.deps);
  writeFileSync(f.deps.agentSource, 'name = "updated"\n');
  assert.equal(install([], f.deps).changed, true);
  assert.equal(readFileSync(f.target, 'utf8'), 'name = "updated"\n');
  writeFileSync(f.target, 'user edit');
  f.calls.length = 0;
  assert.throws(() => install([], f.deps), /unowned or modified/);
  assert.deepEqual(f.calls, [['--version']]);
});

test('matching existing marketplace upgrades; mismatched or unknown sources fail closed', t => {
  const matching = { name: MARKETPLACE, marketplaceSource: { sourceType: 'git', source: SOURCE } };
  const f = fixture(t, [matching]);
  install([], f.deps);
  assert.deepEqual(f.calls.slice(2), [['plugin', 'marketplace', 'upgrade', MARKETPLACE], ['plugin', 'add', PLUGIN, '--json']]);
  for (const marketplaceSource of [undefined, { sourceType: 'local', source: SOURCE }, { sourceType: 'git', source: 'https://evil.test/repo.git' }]) {
    const conflict = fixture(t, [{ name: MARKETPLACE, marketplaceSource }]);
    assert.throws(() => install([], conflict.deps), /mismatched or unverifiable source/);
    assert.equal(conflict.calls.length, 2);
    assert.deepEqual(readdirSync(conflict.deps.home), []);
  }
});

test('reject target, ancestor, home, and manifest symlinks before mutations', t => {
  for (const kind of ['target', 'ancestor', 'home', 'manifest']) {
    const f = fixture(t);
    const destination = join(f.root, 'elsewhere');
    mkdirSync(destination);
    if (kind === 'home') {
      rmSync(f.deps.home, { recursive: true });
      symlinkSync(destination, f.deps.home);
    } else if (kind === 'ancestor') symlinkSync(destination, join(f.deps.home, '.codex'));
    else {
      mkdirSync(dirname(f.target), { recursive: true });
      symlinkSync(join(destination, 'missing'), kind === 'target' ? f.target : join(dirname(f.target), '.edgex-researcher.manifest.json'));
    }
    assert.throws(() => install([], f.deps), /Unsafe path/);
    assert.deepEqual(f.calls, [['--version']]);
    assert.deepEqual(readdirSync(destination), []);
  }
});

test('missing Codex and failed JSON inspection cause no writes', t => {
  const f = fixture(t);
  assert.throws(() => install([], { ...f.deps, run: () => ({ error: { code: 'ENOENT' } }) }), /Codex is unavailable/);
  const run = (_, args) => args[0] === '--version' ? { status: 0 } : { status: 2, stderr: 'unsupported --json' };
  assert.throws(() => install([], { ...f.deps, run }), /must support.*--json/);
  assert.deepEqual(readdirSync(f.deps.home), []);
});

test('failed plugin command never writes custom agent', t => {
  const f = fixture(t);
  const run = (cmd, args, options) => args[1] === 'add' ? { status: 1, stderr: 'install failed' } : f.deps.run(cmd, args, options);
  assert.throws(() => install([], { ...f.deps, run }), /install failed/);
  assert.deepEqual(readdirSync(f.deps.home), []);
});

test('help avoids commands and file reads; unsupported arguments error', () => {
  assert.match(install(['--help'], { run() { assert.fail('must not execute'); } }).help, /npx --yes github:/);
  for (const args of [['--force'], ['--target'], ['--target', 'claude'], ['--target=codex'], ['install'], ['--help', '--bad']]) {
    assert.throws(() => parseArgs(args), /Unsupported argument|supports only codex/);
  }
});

test('missing bundled agent and malformed ownership fail before marketplace mutations', t => {
  const f = fixture(t);
  rmSync(f.deps.agentSource);
  assert.throws(() => install([], f.deps), /ENOENT/);
  assert.deepEqual(f.calls, [['--version']]);
  writeFileSync(f.deps.agentSource, 'agent');
  f.put('old managed bytes');
  const manifest = join(dirname(f.target), '.edgex-researcher.manifest.json');
  writeFileSync(manifest, JSON.stringify({ file: 'another-agent.toml', sha256: 'a'.repeat(64) }));
  assert.throws(() => install([], f.deps), /Invalid ownership manifest/);
  assert.equal(readFileSync(f.target, 'utf8'), 'old managed bytes');
});

test('invalid marketplace JSON fails without writes or mutating commands', t => {
  for (const stdout of ['{', '{}', '{"marketplaces":[null]}']) {
    const f = fixture(t);
    const run = (cmd, args, options) => args.includes('--json') ? { status: 0, stdout } : f.deps.run(cmd, args, options);
    assert.throws(() => install([], { ...f.deps, run }));
    assert.deepEqual(f.calls, [['--version']]);
    assert.deepEqual(readdirSync(f.deps.home), []);
  }
});

test('CLI works through npm-style bin symlink without invoking Codex for help or bad flags', t => {
  const f = fixture(t);
  const bin = join(f.root, 'edgex-agent');
  symlinkSync(realpathSync(new URL('./install.mjs', import.meta.url)), bin);
  const options = { encoding: 'utf8', env: { ...process.env, HOME: f.deps.home, PATH: '' } };
  const help = spawnSync(process.execPath, [bin, '--help'], options);
  assert.equal(help.status, 0, help.stderr);
  assert.match(help.stdout, /Usage: edgex-agent/);
  const invalid = spawnSync(process.execPath, [bin, '--unsupported'], options);
  assert.equal(invalid.status, 1);
  assert.match(invalid.stderr, /Unsupported argument/);
  assert.deepEqual(readdirSync(f.deps.home), []);
});
