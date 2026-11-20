# Node.js / JavaScript / TypeScript (backends and frontends)

Sources of truth: Node.js release notes and the release schedule (only even-numbered
LTS lines for production), each framework's migration guide (Express, NestJS,
React, Angular, Vue, Next.js, webpack...).

## Inventory
```bash
node -v; npm -v      # or yarn -v / pnpm -v
npm outdated
npm audit --omit=dev
npm ls --all --depth=1
npx npm-check-updates          # shows latest majors, does not change anything without -u
```
Check `engines` in package.json, `.nvmrc`, Dockerfile base image, which lockfile is
committed (`package-lock.json`, `yarn.lock`, `pnpm-lock.yaml`) and stay with that manager.
Flag: `node-sass`, `request`, `moment`, `tslint`, `babel-preset-es2015`, webpack 4,
`gulp` 3, native modules (`bcrypt`, `sharp`, `canvas`, `grpc`).

## Baseline
```bash
npm ci
NODE_OPTIONS="--trace-deprecation" npm test 2> deprecations.txt
npm run build
```
For frontends, snapshot built output size and run existing e2e tests if any; for a
backend API use `scripts/snapshot.py`.

## Hop strategy
- Node: LTS to LTS (e.g. 12 -> 14 -> 16 -> 18 -> 20 -> 22 -> 24). Rebuild native modules on every hop (`npm rebuild`).
- Framework majors one at a time, using their tooling: `ng update` (Angular, one major per step), `npx @next/codemod`, React codemods, `vue` migration build.
- TypeScript: bump separately; new versions add stricter checks.
- Never mix a package-manager change (npm -> pnpm) with a version hop.

## Useful tools
`npm-check-updates`, `npm audit`, framework codemods, `depcheck` (unused deps), `madge` (circular imports, useful for ESM moves).

## Silent behavior changes to check
- **OpenSSL 3 (Node 17+):** old webpack builds fail with `ERR_OSSL_EVP_UNSUPPORTED`; legacy ciphers/hashes in your code stop working.
- **Stable `Array.prototype.sort` (V8 7.0 / Node 11):** order of equal elements changes; lists and reports reorder.
- **ICU / Intl data updates:** `toLocaleString`, `Intl.DateTimeFormat`, currency formatting outputs change between Node versions (e.g. spaces, abbreviations, pt-BR formatting). Snapshot anything formatted.
- **Global `fetch` (Node 18+):** clashes with `node-fetch`/polyfills; behavior of timeouts and headers differs.
- **CommonJS vs ESM:** packages that went ESM-only (e.g. `chalk` 5, `node-fetch` 3) break `require`.
- **Express 5:** route path syntax changes (path-to-regexp), `req.query` handling, removed methods; unmatched routes can silently 404.
- **`Buffer()` constructor, `url.parse`** deprecations; DNS result order changed (Node 17: `verbatim`), so `localhost` may resolve to IPv6 `::1`.
- **React 18:** automatic batching and StrictMode double-invoking effects in dev; React 19 removes legacy APIs.
- **Date libraries:** moving from `moment` to `date-fns`/`dayjs`/`Temporal` changes parsing leniency and time zone defaults.

## Common workarounds (ledger them)
`--legacy-peer-deps`, `--force`, `NODE_OPTIONS=--openssl-legacy-provider`, `overrides`/`resolutions` pinning transitive deps, `skipLibCheck: true`, `// @ts-ignore`, `eslint-disable`.
