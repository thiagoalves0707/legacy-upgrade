# Rust

Sources of truth: Rust release notes, the Edition Guide (doc.rust-lang.org/edition-guide),
crate changelogs, `rust-version` (MSRV) fields of dependencies.

## Inventory
```bash
rustc -V; cargo -V
cat rust-toolchain.toml 2>/dev/null
cargo tree --depth 1
cargo outdated            # cargo install cargo-outdated
cargo audit               # cargo install cargo-audit
```
Check `edition` and `rust-version` in each `Cargo.toml`, whether `Cargo.lock` is
committed (it should be for apps), `[patch]` sections, `build.rs` and `-sys` crates
with C dependencies.

## Baseline
```bash
cargo build --all-targets && cargo test --all-features && cargo clippy --all-targets -- -W warnings
```

## Hop strategy
- Toolchain bump first (update `rust-toolchain.toml`), fix new clippy/compiler warnings.
- Edition migration as its own hop, one edition at a time (2015 -> 2018 -> 2021 -> 2024): `cargo fix --edition`, then change `edition` in Cargo.toml, then `cargo fix --edition-idioms` if wanted.
- Dependencies: `cargo update` (semver-compatible) as one hop; each breaking major (e.g. `tokio`, `axum`, `hyper` 0.14 -> 1, `rand` 0.8 -> 0.9) as its own hop.
- For libraries: `cargo semver-checks` before publishing.

## Useful tools
`cargo fix`, `cargo clippy`, `cargo-audit`, `cargo-outdated`, `cargo-msrv`, `cargo-semver-checks`, `cargo-deny`.

## Silent behavior changes to check
- **Edition 2024 drop order changes:** temporaries in tail expressions and `if let` scrutinees are dropped earlier. Code relying on locks/guards living longer can change behavior.
- **Edition 2024 `impl Trait` lifetime capture rules** and `unsafe extern` blocks - mostly compile errors, but review fixes.
- **Edition 2021 disjoint closure captures:** closures capture fields, not whole structs, changing drop order.
- **`cargo update` within semver** can still change behavior (e.g. serialization formats, default features, TLS backends). Snapshot outputs.
- **Major crate bumps:** `serde` attributes, `chrono` time zone APIs, `reqwest` default features (TLS backend), `hyper`/`axum` routing and body handling.

## Common workarounds (ledger them)
`#[allow(...)]`, `[patch.crates-io]` forks, pinning `=x.y.z`, disabled default features, keeping an older edition.
