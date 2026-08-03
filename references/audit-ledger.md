# The audit ledger

One document, written as you go, that turns "this page is ugly" into a
list of provable defects — and later into the report. Keep it in chat for
small jobs; write `docs/ui-audit/<screen>.md` when it is worth keeping.

## Structure

```markdown
# UI audit — <screen name>

**URL/route:** …
**Host + version:** <framework> <version from lockfile>
**Contract sources:**
- components: <path>
- tokens: <path>
- icons: <path>
- i18n: <paths, all locales>

## Phase 0 — Visual defects (before)

Plain language, numbered, no causes yet. One line each.

1. Button label reads `global.default.refresh`.
2. First KPI tile's icon is a blank square; the other three render.
3. No spacing between sections; the section heading touches the card above.
4. "Budget usage" card is narrower than the rows above it and centred.
5. "0 Declined" has no chip; its siblings do.
6. Amounts show as `45000`; dates as `2026-07-26T09:12:00+00:00`.

Screenshot: <path>
Measurements: <the numbers that matter — widths, gaps, scrollH vs clientH>

## Defect ledger

| # | Code says | Contract says (file:line) | User sees | Class | Fix |
|---|-----------|---------------------------|-----------|-------|-----|
| 1 | `$t('global.default.refresh')` | key absent from host catalog `<path>:1` | raw key as label | missing i18n key | own snippet `…dashboard.refresh` |
| 2 | `name="regular-building"` | not in icon dir `<path>/` | blank square | bad icon name | `regular-officebuilding` |
| 3 | layout on `.lib-view` | `position:absolute`, single child `<path>:3` | gaps inert, double padding | wrapper ownership | own `__layout` element inside |
| 4 | `.my-card.lib-card{max-width:none}` | `.lib-card[data-v]{max-width:60rem}` `<path>:14` | card narrower than row | specificity tie | add page-class ancestor |
| 5 | `variant="danger"` | union is neutral/info/attention/critical/positive `<path>:22` | unstyled badge | off-list enum | `critical` |
| 6 | raw values in cells | platform formatters at `<path>:35,100` | unformatted | unformatted values | route through formatter |

**Class** is the row's value: it is what the Phase 5 test asserts and what
tells you whether the defect is systemic. Use the names from
[silent-failures.md](silent-failures.md).

## Out of scope

Defects found but deliberately not fixed, with why. Being explicit here is
what keeps scope honest — and stops the same finding being rediscovered.

- `<neighbouring screen>`: status badge uses `rejected`, variant map has
  `declined` → unstyled chip. Pre-existing; different screen.

## Design Gate brief

- **Cut:** <redundant elements being deleted, not restyled>
- **Keep/change:** <IA — what the viewer needs first>
- **Primitives:** <host components used, and which ledger rows each closes>
- **Dependency decision:** <none, and why | this package, and what the host cannot do>
- **Accessibility:** <what carries meaning besides colour>

## Phase 6 — Verification (after)

| # | Status | Evidence |
|---|--------|----------|
| 1 | FIXED | label renders "Refresh" |
| 3 | FIXED | layout width 1425px (was 1297px inert); gap applies |
| 4 | FIXED | all row cards 701px, budget card full width |

Screenshot (wide): <path> · Screenshot (narrow): <path>
Console: clean after reload
Keyboard: focus ring visible on all N tiles
Links checked: <the ones you claimed to fix>

## Tests added

| Test | Prevents |
|------|----------|
| `every badge variant is one the library styles` | #5 |
| `font-size never uses a spacing token` | flat type hierarchy |
| `every key resolves in all locales` | #1 |
| `every route navigated to is registered` | dead navigation |

Suite: N passed / M pre-existing failures (named, untouched)
```

## Quality bar

Self-grade before presenting. A failing item sends you back to the phase
that fills it — not into the report.

- [ ] Every ledger row cites a **`file:line` in the installed source**, not
      a recollection or a public doc page.
- [ ] Every Phase 0 defect appears in the ledger, or in **Out of scope**
      with a reason. Nothing silently disappears.
- [ ] The **host version** is recorded — contract answers are
      version-scoped.
- [ ] Every row has a **class**, so systemic patterns are visible rather
      than filed as six unrelated bugs.
- [ ] The ownership audit was actually run (**measurements present**), not
      assumed.
- [ ] The dependency decision is **stated either way**, with a reason.
- [ ] Phase 6 evidence is **like-for-like** with Phase 0 — the same numbers
      re-measured, not a fresh screenshot and a claim.
- [ ] Console was re-read **after a reload** (buffers keep stale errors).
- [ ] Pre-existing test failures are **named and distinguished** from ones
      you caused.
- [ ] Every added test has a **non-emptiness guard** and a comment naming
      the defect it prevents.

## Reporting inline

Short. The ledger is the artifact; the message is the summary:

1. **Root-cause classes** found, with counts — "six defects, four of them
   the same class: values that type-check but the library never styles."
2. The **Phase 0 list** with FIXED / PARTIAL / OUT-OF-SCOPE per row.
3. The **dependency decision**, one sentence.
4. **Pre-existing failures** you left alone, named.

Lead with the class, not the list. "Nothing errored, which is why it
survived review" is the sentence that changes how the team looks at the
next ugly page.
