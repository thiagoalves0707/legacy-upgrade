# Ruby / Rails

Always confirm versions and compatibility against the official Rails upgrade guide
(guides.rubyonrails.org/upgrading_ruby_on_rails.html), each release's notes, and
Ruby's NEWS file. The notes below are a starting checklist, not the source of truth.

## Inventory
```bash
ruby -v; bundle -v; bundle exec rails -v
bundle outdated --only-explicit
bundle exec bundle-audit check --update   # gem: bundler-audit
gem list | grep -i -E "pg|mysql2|nokogiri|ffi|sassc|therubyracer|mini_racer"   # native extensions
```
Look for: gems with no version constraint, `git:` / `path:` gems, monkey patches in
`config/initializers` and `lib/`, `config.autoloader = :classic`, `protected_attributes`,
`therubyracer`, `sass-rails`/`sassc`, `paperclip` (abandoned), `devise` and `rspec-rails` major versions.

## Baseline
```bash
RAILS_ENV=test bundle exec rspec        # or: bin/rails test
RUBYOPT="-W:deprecated" bundle exec rspec 2> deprecations.txt
```
Set `ActiveSupport::Deprecation.behavior = :log` (or `:raise` in CI later) and collect the output.
Dump the schema: `bin/rails db:schema:dump` and keep a copy.

## Hop strategy
- Rails: one minor at a time: 5.2 -> 6.0 -> 6.1 -> 7.0 -> 7.1 -> 7.2 -> 8.0...
- Interleave Ruby with Rails following each Rails release's minimum/maximum Ruby. Typical path from Rails 5.2 / Ruby 2.7:
  Rails 6.0 -> 6.1 (on Ruby 2.7) -> Ruby 3.0/3.1 -> Rails 7.0 -> 7.1 -> 7.2 -> newer Ruby.
  Rails 7.2 needs Ruby >= 3.1. Verify the Ruby you target is supported by the Rails you target before jumping (e.g. Ruby 4.0 with Rails 7.2).
- Check maintenance status: Rails supports only recent series. If the requested target (e.g. 7.2) is out of security support, tell the user and propose the next one.
- Per Rails hop: bump in Gemfile -> `bundle update rails --conservative` -> `bin/rails app:update` (review every diff, do not accept blindly) -> keep `config.load_defaults <old>` -> pass tests -> flip `new_framework_defaults_X_Y.rb` options **one by one** -> finally bump `load_defaults`.
- Optional dual boot: the `next_rails` gem lets you run the suite on current and next Rails from one branch.

## Useful tools
`next_rails` (dual boot, deprecation tracking), `bundler-audit`, `rubocop` with `rubocop-rails`, `zeitwerk:check` (`bin/rails zeitwerk:check`), `rails app:update`.

## Silent behavior changes to check
- **Framework defaults** (`new_framework_defaults_*.rb`): each flag changes behavior. Examples: `belongs_to` required by default, `has_many_inverse`, `to_time_preserves_timezone`, cache format versions, partial inserts.
- **Key generator digest SHA1 -> SHA256 (7.0 defaults):** invalidates existing signed/encrypted cookies and messages unless you add rotations. Users get logged out, encrypted data fails to read.
- **Cookie and message serializer changes** (Marshal/JSON/message_pack): old cookies unreadable without a hybrid/rotation step.
- **Zeitwerk autoloading (classic removed in 7.0):** file names must match constants. `zeitwerk:check` must pass; lazy-loaded code that never runs in tests can still break in production.
- **Ruby 3.0 keyword argument separation:** some calls silently bind a hash as a positional argument instead of raising.
- **Psych 4 (Ruby 3.1):** `YAML.load` is safe by default; YAML with aliases or symbols, and YAML-serialized columns, fail. Rails added `yaml_column_permitted_classes` / `use_yaml_unsafe_load` - turning on unsafe load is a ledger item.
- **Default gems moved to bundled gems** in recent Rubies (e.g. `base64`, `bigdecimal`, `csv`, `mutex_m`, `drb` in 3.4): add them to the Gemfile explicitly.
- **Frozen string literals:** newer Rubies warn on mutation of string literals; in-place mutations (`<<`) in old code show up.
- **Time zones:** `ActiveRecord.default_timezone`, `Time.zone` vs `Time.now`; JSON date formats in serializers.
- **JSON rendering:** `as_json` of decimals, times (precision of fractional seconds) can change between versions. Snapshot comparison catches this.
- **Strong parameters / `ActionController::Parameters`** no longer behaves like a Hash in old code paths.

## Common workarounds (ledger them)
`config.load_defaults` kept at old version, `config.autoloader = :classic` (only until 6.1), `use_yaml_unsafe_load`, `config.active_record.belongs_to_required_by_default = false`, pinning gems to forks, `RUBYOPT=-W0` to hide warnings.
