# PHP (Laravel, Symfony, WordPress, plain PHP)

Sources of truth: php.net migration guides per version ("Migrating from PHP 7.4.x to
PHP 8.0.x", etc.), Laravel upgrade guide per major, Symfony UPGRADE-x.y.md files.

## Inventory
```bash
php -v; composer --version
composer outdated --direct
composer audit
composer why-not php 8.3        # what blocks a PHP version
php -m                          # loaded extensions (mcrypt, mysql, etc.)
```
Flag: `mysql_*` functions, `mcrypt`, `ereg`, `each()`, `create_function`, dynamic
properties, abandoned packages (Composer marks them), `laravelcollective/html`.

## Baseline
```bash
vendor/bin/phpunit              # or pest
php -d error_reporting=E_ALL -d display_errors=1 vendor/bin/phpunit 2> deprecations.txt
php artisan route:list > routes-before.txt     # Laravel
```

## Hop strategy
- PHP: one minor at a time across 7.x -> 8.0 -> 8.1 -> 8.2 -> 8.3 -> 8.4.
- Laravel: one major at a time, following the official upgrade guide for each. Symfony: go to the last minor of a major (x.4 LTS), clear all deprecations, then jump to the next major.
- Run static analysis (PHPStan/Psalm) at a modest level before upgrading; it finds code that will break on the new PHP.

## Useful tools
**Rector** (automated upgrades for PHP versions, Laravel, Symfony, PHPUnit), PHPCompatibility for PHP_CodeSniffer, PHPStan/Psalm, `composer audit`, Laravel Shift (commercial).

## Silent behavior changes to check
- **PHP 8.0 string-to-number comparison:** `0 == "foo"` is now `false` (was `true`). `in_array`, `switch` and loose comparisons change results without any error.
- **PHP 8.0 stable sorting:** order of equal elements changes.
- **PHP 8.0 float to string is locale-independent:** output of floats changes on servers with a non-English locale (e.g. `1,5` becomes `1.5`).
- **PHP 8.1 passing `null` to non-nullable internal parameters** is deprecated (`strlen(null)`); behavior today, error tomorrow.
- **PHP 8.2 dynamic properties deprecated.**
- **Arithmetic/bitwise on arrays/objects now TypeError (8.0)**, warnings promoted to exceptions in many functions.
- **Laravel 7: model date serialization** changed to ISO-8601 with UTC (`2020-01-01T00:00:00.000000Z`) - API responses change silently. `serializeDate` override restores old format (ledger it).
- **Laravel `$dates` property removed (10)** in favor of `$casts`.
- **Carbon 2 -> 3:** `diffIn*` methods return floats and can be negative.

## Common workarounds (ledger them)
`error_reporting(E_ALL & ~E_DEPRECATED)`, `#[AllowDynamicProperties]`, `@` error suppression, `serializeDate` overrides, `composer --ignore-platform-reqs`, forked packages.
