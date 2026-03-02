#!/usr/bin/env node
/**
 * Pre-commit hook: run Prettier on staged files in apps/pwa.
 * Usage: node scripts/prettier_precommit.js [files...]
 */
import { spawnSync } from 'node:child_process'
import { resolve, dirname } from 'node:path'
import { fileURLToPath } from 'node:url'

const root = resolve(dirname(fileURLToPath(import.meta.url)), '..')
const files = process.argv.slice(2).filter((f) => f.includes('apps' + '/pwa/'))

if (files.length === 0) process.exit(0)

const result = spawnSync(
  'pnpm',
  ['--filter', 'docling-pwa', 'exec', 'prettier', '--write', ...files],
  { cwd: root, stdio: 'inherit', shell: true }
)

process.exit(result.status ?? 1)
