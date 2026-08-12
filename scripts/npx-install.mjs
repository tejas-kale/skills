#!/usr/bin/env node
/**
 * Entry point for `npx github:tejas-kale/skills`.
 *
 * Always delegates to the Vercel `skills` package (`skills@latest`), not
 * `skills-cli`. The latter also exposes a `skills` binary but treats
 * `owner/repo` as a registry id, which is why
 * `npx skills add tejas-kale/skills` fails with "not found in registry"
 * when that CLI is on PATH.
 */
import { spawnSync } from "node:child_process";

const SOURCE = "https://github.com/tejas-kale/skills";
const extra = process.argv.slice(2);
const args = ["-y", "skills@latest", "add", SOURCE, ...extra];

const result = spawnSync("npx", args, {
  stdio: "inherit",
  shell: process.platform === "win32",
});

process.exit(result.status === null ? 1 : result.status);
