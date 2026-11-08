#!/usr/bin/env node
// Start the bundled dependency-free controller without pip or provider credentials.
import { spawn, spawnSync } from 'node:child_process';
import { dirname, resolve, delimiter } from 'node:path';
import { fileURLToPath } from 'node:url';

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const candidates = process.env.EDGEX_PYTHON
  ? [process.env.EDGEX_PYTHON]
  : (process.platform === 'win32' ? ['python', 'python3', 'py'] : ['python3', 'python']);
const python = candidates.find(command => {
  const result = spawnSync(command, ['-c', 'import sys; raise SystemExit(sys.version_info < (3,10))'],
    { stdio: 'ignore', timeout: 5000, windowsHide: true });
  return result.status === 0;
});
if (!python) {
  console.error('EdgeX needs Python 3.10+ for its controller. Set EDGEX_PYTHON to a working interpreter.');
  process.exit(1);
}
const child = spawn(python, ['-m', 'edgex', 'serve'], {
  env: { ...process.env, PYTHONPATH: [resolve(root, 'src'), process.env.PYTHONPATH].filter(Boolean).join(delimiter) },
  stdio: 'inherit', windowsHide: true,
});
child.on('error', error => { console.error(error.message); process.exitCode = 1; });
child.on('exit', code => { process.exitCode = code ?? 1; });
for (const signal of ['SIGINT', 'SIGTERM']) process.on(signal, () => child.kill(signal));
