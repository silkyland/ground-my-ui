# Locating the contract source

The version on disk is the version that renders. Published docs describe
*a* version; the lockfile decides *yours*. Always read the installed copy.

## The four artifacts

Before auditing anything, produce a path for each:

| Artifact | Question it answers |
|----------|--------------------|
| Component library | Which props/slots/events exist, and which enum values are actually styled? |
| Design tokens | Does this custom property/constant exist, and is it spacing or type? |
| Icon set | Is this icon name real in this version? |
| i18n catalog | Does this key resolve, in every shipped locale? |

Plus the **host version**, from the lockfile. Record it in the ledger —
a contract answer is only true for a version.

## Where the installed copy lives

### JavaScript / TypeScript

```bash
# The library, its dist CSS, and its version
ls node_modules/<lib>/{package.json,dist,src}
node -p "require('./node_modules/<lib>/package.json').version"

# Nested installs are common in monorepos and PHP/Ruby apps that vendor a JS admin
find . -path '*/node_modules/<lib>' -maxdepth 6 -type d
```

Prefer `src/` (readable source, comments, `@deprecated` notes) over
`dist/` when both ship. `.d.ts` files are the fallback when only `dist`
exists.

### Framework-hosted admin/SPA inside a server app

PHP (Shopware/Magento/Symfony), Rails, and Django apps often vendor a full
JS admin. The contract source is *inside the vendored framework*, not the
project root:

```bash
find vendor -maxdepth 8 -type d -name node_modules 2>/dev/null | head
```

The same applies to template-side contracts: a Twig/Blade/ERB/Jinja
component's accepted attributes live in the framework's own template
source.

### Other ecosystems

| Stack | Installed contract source |
|-------|--------------------------|
| Python | `site-packages/<pkg>/` (`pip show -f <pkg>` to list) |
| Ruby | `$(gem env gemdir)/gems/<gem>-<v>/` or `bundle show <gem>` |
| Swift / iOS | `.build/checkouts/`, `Package.resolved`, `Pods/`, or the SDK in Xcode |
| Android / Kotlin | `~/.gradle/caches/modules-2/files-2.1/<group>/`; unzip the `.aar` for resources |
| Flutter / Dart | `~/.pub-cache/hosted/pub.dev/<pkg>-<v>/lib/`, `pubspec.lock` |
| .NET | `~/.nuget/packages/<pkg>/<v>/lib/` |
| Rust | `~/.cargo/registry/src/*/<crate>-<v>/` |
| Go | `$(go env GOMODCACHE)/<module>@<v>/` |

## Enumerating a component's contract

The goal is a definitive list of props (with enum unions), slots, and
events. Match the pattern to the framework:

| Framework | Where the contract is declared | Grep for |
|-----------|-------------------------------|----------|
| Vue 3 SFC | `defineProps` / `defineSlots` / `defineEmits`; `props: {}` in options API | `sed -n '/defineProps/,/^);/p' Comp.vue` |
| React + TS | The props interface/type; the `variant` union | `type .*Props`, `interface .*Props` |
| Svelte | `export let` (v4) or `$props()` (v5); `<slot name=…>` | `export let`, `\$props\(` |
| Angular | `@Input()` / `@Output()`; `ng-content select=` | `@Input\(`, `ng-content` |
| Web components | `static properties` / `observedAttributes`; `<slot name=>` | `observedAttributes`, `slot name=` |
| SwiftUI | `init` signatures; enums conforming to the style protocol | `public init`, `enum .*Style` |
| Compose | `@Composable fun` parameter lists; sealed classes for variants | `@Composable fun <Name>` |
| Flutter | Widget constructor named params; `enum` for variants | `const <Widget>({`, `enum ` |
| Twig/Blade/ERB/Jinja | The component template's own params/blocks | the template file itself |

Two checks that pay for themselves every time:

```bash
# 1. Which enum values are actually STYLED (not merely accepted)?
grep -oE '\.c-badge--variant-[a-z-]+' node_modules/<lib>/dist/*.css | sort -u
# Compare against the declared union. A value can type-check and still have no rule.

# 2. What does the library impose by default that will fight your layout?
grep -nE 'max-width|margin|padding|position' node_modules/<lib>/dist/<comp>.css
```

Also grep the components you use for `@deprecated` — a working component
with a removal date is a defect with a deadline.

## Enumerating tokens

```bash
# All available token names, by family
grep -ohE '\--(color|space|scale-size|font-size|font-weight|border-radius)[a-z0-9-]*' \
  <tokens>/**/*.css | sort -u

# Does this exact one exist?
grep -- '--scale-size-13:' <tokens>/*.css || echo "MISSING"
```

Non-CSS equivalents: `Theme.of(context)` / `MaterialTheme` token objects
(Flutter/Compose), `Color`/`Font` extensions and asset catalogs (SwiftUI),
`ThemeResource` keys (.NET), a Tailwind/Panda/Vanilla-Extract config, or a
Sass/Less variables partial.

**Separate the families.** Spacing scales and type scales are different
vocabularies; using a spacing step as a font size is a defect even when
the token exists. If both families are `--scale-*`, that ambiguity is
itself a finding worth a lint rule.

## Enumerating icons

```bash
ls <icon-pkg>/icons/<style>/ | head                 # the vocabulary
for i in $NAMES; do [ -f "$D/$i.svg" ] && echo "OK $i" || echo "MISS $i"; done
ls <icon-pkg>/icons/<style>/ | grep -iE 'build|office|company'   # find the real name
```

Sprite-based sets: grep the `<symbol id=…>` list. Font-based sets: read the
codepoint map. Native: the SF Symbols catalog / `Icons.*` (Flutter) /
Material Symbols name list.

## Enumerating i18n keys

```bash
# Resolve one key across every locale
python3 - <<'PY'
import json, glob
KEY = "namespace.section.key"
for p in sorted(glob.glob("**/locales/*.json", recursive=True)):
    node = json.load(open(p, encoding="utf-8"))
    for part in KEY.split("."):
        node = (node or {}).get(part) if isinstance(node, dict) else None
    print(f"{'OK  ' if node else 'MISS'} {p}")
PY
```

Then invert it: extract every key the screen references and check them all
at once. That grep-then-resolve loop is the Phase 5 test almost verbatim.

Formats vary — nested JSON, flat `.properties`, gettext `.po`, Rails YAML,
`.xcstrings`, Android `strings.xml`, ARB — but the discipline is identical:
**every key, every locale.**

## Recording the evidence

One ledger row per verified contract, with the `file:line` you read it at.
"I checked" is not evidence; a citation is — and it is what makes the
Phase 5 tests obvious to write.
