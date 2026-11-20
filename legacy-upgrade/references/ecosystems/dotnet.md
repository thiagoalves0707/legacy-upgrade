# .NET (.NET Framework, .NET Core, modern .NET)

Sources of truth: Microsoft "Breaking changes in .NET N" pages, the .NET Framework
to .NET porting guide, ASP.NET Core and EF Core migration guides.

## Inventory
```bash
dotnet --info
dotnet list package --outdated --include-transitive
dotnet list package --vulnerable --include-transitive
dotnet list package --deprecated
```
Check `TargetFramework`(s) in `.csproj`, `packages.config` (old style), `global.json`,
`web.config`. Flag: `System.Web`, WCF server, WebForms, Remoting, AppDomains,
`BinaryFormatter`, `Newtonsoft.Json` customizations, EF6, Windows-only APIs
(registry, `System.Drawing` on Linux).

## Baseline
```bash
dotnet build -warnaserror-   # keep warnings visible, save them
dotnet test --logger "trx"
```

## Hop strategy
- .NET Framework -> modern .NET is a **port**, not a bump: convert to SDK-style projects first (still targeting Framework), migrate `packages.config` to `PackageReference`, then multi-target (`net48;net8.0`) libraries before switching the app.
- Modern .NET: LTS to LTS (6 -> 8 -> 10). Bump `global.json` SDK, `TargetFramework`, then `Microsoft.*` packages together for that version.
- ASP.NET (System.Web) -> ASP.NET Core: migrate incrementally (strangler pattern / YARP proxy in front) for large apps.
- EF6 -> EF Core is its own track.

## Useful tools
Microsoft's upgrade tooling (the .NET Upgrade Assistant or its successor in Visual Studio/Copilot - check which is current), `try-convert` for SDK-style projects, .NET Portability/API analyzers, `dotnet list package`.

## Silent behavior changes to check
- **Globalization uses ICU (.NET 5+, also on Windows):** culture-sensitive `string.IndexOf`, `Compare`, `StartsWith` give different results (e.g. `"\r\n".IndexOf("\n")`). Use ordinal comparisons where intended.
- **System.Text.Json vs Newtonsoft.Json:** case sensitivity, camelCase defaults in ASP.NET Core, null handling, date formats, enum serialization, reference loops. API payloads change.
- **EF Core vs EF6:** different SQL translation, client evaluation throws (EF Core 3+), cascade delete defaults, lazy loading off by default.
- **Npgsql 6+ timestamp handling:** `DateTime` Kind must match `timestamp with time zone`; values shift or throw.
- **`BinaryFormatter` disabled/removed:** session state, caches or files serialized with it fail.
- **Default HTTP/TLS behavior and certificate validation** differ on Linux containers.
- **Floating point formatting** (`double.ToString()`) became shortest round-trippable in .NET Core 3.0.

## Common workarounds (ledger them)
`InvariantGlobalization`/`UseNls` switches, `<NoWarn>`, `#pragma warning disable`, Newtonsoft kept via `AddNewtonsoftJson()`, `EnableUnsafeBinaryFormatterSerialization`, `Npgsql.EnableLegacyTimestampBehavior`, Windows Compatibility Pack.
