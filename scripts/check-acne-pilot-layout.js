#!/usr/bin/env node
// Use the same stdlib HTML parser/checks as check_site.py; no npm dependencies.
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const result = spawnSync(process.env.PYTHON || 'python',
  ['-B', '-X', 'utf8', '-m', 'scripts.acne_pilot', ...process.argv.slice(2)],
  { cwd: path.resolve(__dirname, '..'), stdio: 'inherit' });
if (result.error) console.error(result.error.message);
process.exit(result.status ?? 1);
