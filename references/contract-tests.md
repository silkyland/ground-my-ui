# Locking contracts into tests

An audit that lives only in chat gets re-broken next sprint. These tests
are cheap (they mostly read source text), fast, and each one prevents a
specific defect that shipped once already.

## Principles

1. **One test per ledger row.** Name the defect it prevents in a comment,
   including what the user saw. That comment is why the test survives
   review.
2. **Assert the contract, not the pixels.** Screenshot diffing is a
   different tool with different costs; these tests answer "is this value
   in the library's allowed set", which is stable across redesigns.
3. **Derive the allowed set from the source when you can.** A hard-coded
   list is a snapshot; reading the union from the library survives an
   upgrade and tells you when it changes.
4. **Invert the check.** Do not test the five keys you remember — extract
   *every* key the screen references and assert all of them resolve. The
   invented sixth key is the one that ships.
5. **Assert the absence of the old bug**, not just the presence of the new
   code (`not.toContain('#header-right')` alongside
   `toContain('#headerRight')`).

## Pattern 1 — Enum values are in the styled set

```js
// The badge only styles these five; any other value renders an unstyled span.
const VALID = ['neutral', 'info', 'attention', 'critical', 'positive'];

test('every badge variant is one the library actually styles', () => {
  const used = [...source.matchAll(/TONE_[A-Z]+ = '([a-z]+)'/g)].map(m => m[1]);

  expect(used.length).toBeGreaterThan(0);          // guard: regex still matches
  used.forEach(v => expect(VALID).toContain(v));
  // Vocabulary from another design system — the original defect.
  expect(source).not.toMatch(/'(primary|danger|warning|success)'/);
});
```

Centralising tones in named constants is what makes this greppable. If
values are scattered as literals, hoist them first — the refactor *is* the
fix.

## Pattern 2 — Slot names

```js
// The card's slot is `headerRight`. `#header-right` rendered nothing at all,
// so every "View all" button was silently missing from the DOM.
test('card header actions use the real slot name', () => {
  expect(template).toContain('#headerRight');
  expect(template).not.toContain('#header-right');
});
```

## Pattern 3 — Required props on every usage

```js
// The empty-state component declares `description` as required.
test('every empty-state passes a description', () => {
  const usages = template.split('<mt-empty-state').slice(1);

  expect(usages.length).toBeGreaterThan(0);
  usages.forEach(u => expect(u.slice(0, u.indexOf('/>'))).toContain(':description='));
});
```

## Pattern 4 — Token family discipline

```js
// --scale-size-* are spacing steps. There is no --scale-size-13, and an
// undefined custom property invalidates the whole declaration, which is how
// this page lost its type hierarchy.
test('font-size never uses a spacing token', () => {
  const tokens = [...styles.matchAll(/font-size:\s*var\((--[a-z0-9-]+)\)/g)].map(m => m[1]);

  expect(tokens.length).toBeGreaterThan(0);
  tokens.forEach(t => expect(t).toMatch(/^--font-size-/));
});
```

Stronger version, when the token deliverable is readable from the test:
parse the available names once and assert every `var(--…)` in your
stylesheet is in that set. That catches typos in *any* family.

## Pattern 5 — Every i18n key resolves, in every locale

```js
const resolve = (tree, key) =>
  key.split('.').reduce((n, p) => (n == null ? undefined : n[p]), tree);

// A missing key renders as its own dotted path in the UI.
test('every key the screen references resolves in all locales', () => {
  const keys = new Set([
    ...[...template.matchAll(/\$t\('([^']+)'/g)].map(m => m[1]),
    ...[...source.matchAll(/this\.\$t\('([^']+)'/g)].map(m => m[1]),
  ]);

  const missing = [...keys]
    .filter(k => k.startsWith('my-plugin.'))
    .filter(k => !resolve(en, k) || !resolve(de, k));

  expect(missing).toEqual([]);   // array equality names the offenders on failure
});
```

Add a companion assert that no key outside your own namespace is invented —
borrowing an unverified host key is how a raw label ships.

## Pattern 6 — Navigation targets exist

```js
// Links used to fall back to a parent route because the target was never
// registered, sending reviewers to the wrong screen.
test('every route this screen navigates to is registered', () => {
  const targets = [...source.matchAll(/name: '(app\.section\.[a-zA-Z]+)'/g)].map(m => m[1]);

  expect(targets.length).toBeGreaterThan(0);
  targets.forEach(t => {
    const key = t.replace('app.section.', '');
    expect(routes).toMatch(new RegExp(`\\b${key}:\\s*\\{`));
  });
});
```

## Pattern 7 — Ownership and a11y guards

```js
test('layout is applied to an owned element, not the framework wrapper', () => {
  expect(styles).not.toMatch(/^\s*\.lib-view/m);
  expect(styles).toContain('&__layout');
  expect(template).toContain('my-page__layout');
});

test('interactive tiles keep a focus ring and honour reduced motion', () => {
  expect(styles).toContain(':focus-visible');
  expect(styles).toContain('prefers-reduced-motion');
});

test('uses the current component, not the deprecated wrapper', () => {
  expect(template).toContain('mt-icon');
  expect(template).not.toContain('sw-icon');
});
```

## Every regex assert needs a non-emptiness guard

```js
expect(used.length).toBeGreaterThan(0);
```

Without it, a renamed constant makes the regex match nothing and the test
passes vacuously — the worst outcome, because it reports safety it is not
providing.

## Beyond source-text asserts

Escalate only when the cheap layer cannot answer the question:

- **Component/unit tests** (Testing Library, Vue Test Utils, XCTest,
  Compose UI test) — assert the *rendered* tree: the slot content is
  present, the variant class is on the element.
- **Stylelint / ESLint rules** — a repo-wide `declaration-property-value-allowed-list`
  for `font-size` beats a per-file test once the pattern recurs.
- **Screenshot tests** — good for intentional visual regressions, poor for
  contract violations, and expensive to maintain. Not a substitute for
  these.
- **Console-clean assertion** in an E2E run — fails the build on the
  missing-icon and missing-key classes that *do* log.

## Running them

Run the **whole** suite, not just your file. Then separate:

- failures **you** caused → fix before reporting;
- failures **already present** → name them, say they are pre-existing and
  which feature they belong to, and leave them alone.

Watch for host build scripts that prune `node_modules` (or the equivalent):
if the framework's asset build runs after your install, reinstall test deps
*after* the build, and write the ordering down so the next run does not
lose an hour to it.
