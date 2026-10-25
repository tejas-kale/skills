# Acceptance tests

Verify's step 3: your own tests, written from the task's acceptance criteria, run against the user's package and deleted. They live only in a temp directory, never under `packages/`, and never reach the chat or a commit.

## Behaviour tests (vitest)

1. Set up the temp directory. The symlink lets your test files resolve `vitest`; use the `node_modules` that holds it (the root's in a workspace with root dev dependencies, else the package's):

   ```bash
   tmp=$(mktemp -d)
   ln -s "$PWD/node_modules" "$tmp/node_modules"
   cat > "$tmp/vitest.config.mjs" <<EOF
   export default { test: { root: "$tmp", include: ["**/*.acceptance.test.ts"], exclude: ["node_modules/**"] } };
   EOF
   ```

2. Write `"$tmp"/<task>.acceptance.test.ts`. Import the task's `Interface` by absolute path to its source file (`"$PWD/packages/<pkg>/src/<module>.ts"`) and call nothing else. For a pi extension, drive it through the user's `FakeExtensionAPI`, imported the same way; before it exists (chapter 1), write a minimal stub of your own in the temp file. Run nothing that writes outside `$tmp`: the link script runs with its target override pointed into `$tmp`.
   - First, one test per `Interface` name that checks it is exported with the right `typeof`, titled `I: <name> is exported from <module>`. A missing export imports as `undefined` rather than failing the file.
   - Then one test per criterion, titled with its id (`A2 …`). Give every `expect` a message stating the criterion as a behaviour, in words: `expect(value, "A2: a denied call reports its reason")`.
3. Run with the JSON reporter, so no code frame of your tests reaches the terminal, and print only titles and first failure lines:

   ```bash
   pnpm exec vitest run --config "$tmp/vitest.config.mjs" --reporter=json --outputFile="$tmp/result.json" >/dev/null 2>&1
   node -e '
   const r = JSON.parse(require("fs").readFileSync(process.argv[1], "utf8"));
   for (const f of r.testResults) {
     if (f.assertionResults.length === 0) console.log("LOAD ERROR", (f.message || "").split("\n")[0]);
     for (const a of f.assertionResults)
       console.log(a.status, a.title, a.status === "failed" ? "| " + a.failureMessages[0].split("\n")[0] : "");
   }' "$tmp/result.json"
   ```

   A load error or a failed `I:` test means part of the `Interface` is missing: report which name.

## Type tests (tsc)

When a criterion is about types (a type derived from a schema, a union that rejects a bad value, a `readonly` that blocks mutation), check it with the compiler rather than at run time:

1. Write `"$tmp"/types.acceptance.ts`. Import from the package with the `.js` extension (`"$PWD/packages/<pkg>/src/<module>.js"`), as `NodeNext` expects. Put each criterion on its own lines under a `// A<n>` comment: an assignment that must compile, or a `// @ts-expect-error` line that must fail to compile.
2. Write `"$tmp"/tsconfig.json` that `extends` the root's shared tsconfig by absolute path (read its file name) and `include`s only `types.acceptance.ts`. Override the options that would reject a file outside the monorepo: `"noEmit": true, "rootDir": "/", "composite": false, "declaration": false, "incremental": false`.
3. Run `pnpm exec tsc -p "$tmp" --pretty false`. `--pretty false` prints `file(line,col): error …` without a code frame. Map each error line to its `// A<n>` comment; an unused `@ts-expect-error` means the type accepts what it should reject.

## Report and clean up

Report each failure as the behaviour the spec requires that the code lacks, in the criterion's words. Then `rm -rf "$tmp"`.
