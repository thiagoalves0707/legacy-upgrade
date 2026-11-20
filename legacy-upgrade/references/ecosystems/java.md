# Java / Kotlin (Spring, Jakarta EE, Hibernate)

Sources of truth: JDK release notes (and the removal lists per release), Spring Boot
migration guides on the Spring Boot wiki, Hibernate migration guides, Jakarta EE notes.

## Inventory
```bash
java -version; mvn -v      # or ./gradlew --version
mvn versions:display-dependency-updates versions:display-plugin-updates
./gradlew dependencyUpdates         # plugin: com.github.ben-manes.versions
mvn dependency:tree                 # or ./gradlew dependencies
mvn org.owasp:dependency-check-maven:check   # or the Gradle plugin
```
Flag: `javax.*` imports, JAXB/JAX-WS usage, `sun.*` internals, reflection into JDK
internals, old Lombok, PowerMock, Spring XML config, application server specific code
(WebLogic, JBoss), Log4j 1.x.

## Baseline
```bash
mvn -B verify       # or ./gradlew build
```
Compile with `-Xlint:deprecation` (javac) and save the warnings. Run `jdeps --jdk-internals` on the jars.

## Hop strategy
- JDK: LTS to LTS: 8 -> 11 -> 17 -> 21 -> 25. Upgrade the build tool and plugins (Maven compiler/surefire, Gradle) first.
- Spring Boot: 1.5 -> 2.0 -> ... -> 2.7 (last 2.x, stepping stone) -> 3.0 -> 3.x. Boot 3 needs Java 17 and Jakarta EE 9+.
- `javax.*` -> `jakarta.*` is its own hop, done with tooling, never by hand.
- Add `spring-boot-properties-migrator` temporarily during Boot hops; it reports renamed properties at startup. Remove it at the end.

## Useful tools
**OpenRewrite** (recipes for Java 8->17/21, Spring Boot 2->3, javax->jakarta, JUnit 4->5), `jdeps`, `jdeprscan`, Maven Versions plugin, Gradle versions plugin, OWASP dependency-check.

## Silent behavior changes to check
- **Default locale data CLDR (JDK 9+):** date, number and currency formatting change (e.g. month abbreviations, separators in `pt_BR`). Reports, PDFs and API strings differ.
- **Default charset UTF-8 (JDK 18, JEP 400):** file reading/writing without explicit charset changes on Windows and on servers with a non-UTF-8 locale.
- **Strong encapsulation (JDK 16/17):** reflection into JDK internals fails at runtime, often only in code paths tests do not hit.
- **Removed Java EE modules (JDK 11):** JAXB, JAX-WS, `javax.annotation` must be added as dependencies.
- **Spring Framework 6 / Boot 3: trailing slash matching disabled** - `/movies/` no longer matches `/movies`; clients silently get 404.
- **Spring Boot 2.6: circular references prohibited by default; path matching strategy changed to PathPatternParser.**
- **Hibernate 5 -> 6:** ID generator and sequence naming defaults, HQL parsing, type mappings (e.g. `Instant`, booleans, enums) - inserts can fail or store different values.
- **Jackson upgrades:** date serialization, unknown property handling, `null` inclusion defaults via Boot properties.
- **Log4j/Logback/SLF4J 2:** binding changes can silently drop all logs.

## Common workarounds (ledger them)
`--add-opens` / `--add-exports`, `-Djava.locale.providers=COMPAT` (removed in JDK 23), `-Dfile.encoding=...`, `spring.main.allow-circular-references=true`, `setUseTrailingSlashMatch(true)`/redirect filters, excluding transitive deps, `@SuppressWarnings("deprecation")`, `<skipTests>`.
