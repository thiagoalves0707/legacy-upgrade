# Go

Sources of truth: Go release notes per version, the Go 1 compatibility promise and
the `GODEBUG` history (go.dev/doc/godebug), module changelogs.

## Inventory
```bash
go version
go list -m -u all            # available updates
govulncheck ./...            # go install golang.org/x/vuln/cmd/govulncheck@latest
go mod graph | wc -l
```
Check the `go` and `toolchain` lines in `go.mod`, `vendor/`, GOPATH-era layout
(`Gopkg.toml`/dep, glide), cgo usage, replace directives.

## Baseline
```bash
go build ./... && go vet ./... && go test -race -count=1 ./...
```

## Hop strategy
- GOPATH/dep -> modules first (`go mod init`, then `go mod tidy`), as its own hop.
- Go toolchain: Go keeps strong compatibility, but bump the `go` directive one or two minors at a time, because language and `GODEBUG` defaults follow the `go` line in `go.mod`, not the installed toolchain.
- Dependencies: `go get -u=patch ./...` first, then minor, then majors (major versions change the import path: `/v2`, `/v3`) one module at a time. `go mod tidy` after each.

## Useful tools
`govulncheck`, `go fix`, `gopls` modernize analyzers, `staticcheck`, `golangci-lint`.

## Silent behavior changes to check
- **Loop variable per-iteration semantics (go 1.22 in go.mod):** goroutines/closures capturing loop vars behave differently. Usually fixes bugs, but changes behavior.
- **`math/rand` auto-seeded (1.20):** code relying on the default deterministic sequence now gets different numbers.
- **`GODEBUG` defaults change with the `go` directive:** e.g. TLS and x509 behavior (SHA-1 certificates rejected, minimum TLS versions, RSA key exchange), HTTP/2 and `net/http` parsing changes.
- **`net/http` routing patterns (1.22 ServeMux):** method and wildcard patterns change matching when the go version is bumped.
- **Time and JSON:** `encoding/json` and `time` formatting are stable, but third-party JSON libraries and ORM major versions often are not.

## Common workarounds (ledger them)
`//go:debug` lines or `godebug` blocks restoring old behavior, `replace` directives to forks, pinning old majors, `//nolint`.
