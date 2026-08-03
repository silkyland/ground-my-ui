---
name: ground-my-ui
description: >-
  Diagnoses and rebuilds UI that looks broken, ugly, or off-system by
  verifying every contract the code touches against the INSTALLED source
  on disk — component props, slot names, enum values, design tokens, icon
  names, i18n keys, and which element actually owns layout — before any
  redesign is attempted. Built for the failure class that raises no error:
  an invalid variant renders unstyled, a misspelled slot renders nothing,
  an undefined custom property voids the whole declaration, a missing
  translation key prints itself. Stack-agnostic (React, Vue, Svelte,
  Angular, Twig/PHP, Rails, SwiftUI, Compose, Flutter, .NET) and works
  inside any design system, then locks the verified contracts into tests.
  Use when a screen looks wrong, unstyled, misaligned, or inconsistent
  with its design system, when components render blank or ignore their
  props, when raw translation keys or unformatted values appear in the UI,
  when asked to redesign or restyle a view, or when the user mentions
  ground-my-ui or /ground-my-ui.
license: MIT
argument-hint: "[url or screen] [project-root]"
---

# Ground My UI

Most "ugly" UI is not a taste problem. It is code quietly lying to a
framework: a `variant="danger"` the badge never styled, a `#header-right`
the card never read, a `var(--scale-size-13)` that does not exist, a
`display: flex` on an element the framework positions absolutely. None of
it errors. The build passes, the tests pass, and the page renders as a
pile of half-applied intentions.

So this skill does not start with taste. It starts by reading the
installed component library, token file, icon set, and translation catalog
that the page actually runs against — then rebuilds on what is provably
there.

## The Prime Directive (family rule)

> **No prop, slot, event, enum value, token, icon name, or i18n key that
> you have not read in the installed source.** Not remembered from
> training, not inferred from a sibling component, not copied from the
> library's public docs — read from the copy on this disk, at a
> `file:line` you can cite. Design decisions come *after* the contract
> audit, never before.

## Hard rules

1. **Look at the rendered thing — before and after.** A diagnosis from
   source alone is a guess. Screenshot it, measure the real box model,
   read the console. If you cannot render it, say so and mark every
   finding `UNVERIFIED`.
2. **Never enter credentials to reach the screen.** Ask the user to log
   in, or to hand you a reachable URL. Waiting is cheaper than a wrong
   assumption about what the page looks like.
3. **Silence is the enemy.** The defects that matter here throw nothing.
   Hunt them with the catalog in
   [references/silent-failures.md](references/silent-failures.md) instead
   of waiting for an error.
4. **The host system's primitives before a new dependency.** A design
   system you must obey plus a library you bolted on is two design
   systems. New packages need a written justification (what the host
   cannot do) and a cost line (bundle size, review/audit rules, upgrade
   surface). Check what already ships in the host first — it is routinely
   more than the team remembers.
5. **Scope discipline, with one exception.** Do not restyle neighbouring
   screens. Do fix the destinations *your* screen links to — a beautiful
   card whose button leads to the wrong page is not finished.
6. **Delete redundancy instead of restyling it.** If two elements do the
   same job, the fix is one element, not two prettier ones.

## Progress checklist

Copy this into your response and check items off:

```
Ground Progress:
- [ ] Phase 0: Rendered — screenshot, box model measured, console read, defect list written
- [ ] Phase 1: Contract source located on disk (library, tokens, icons, i18n)
- [ ] Phase 2: Contract audit — every prop/slot/enum/token/icon/key verified, ledger cited
- [ ] Phase 3: Ownership audit — layout/scroll owner identified, selector can win
- [ ] Design Gate — IA + visual plan presented, dependency decision stated
- [ ] Phase 4: Rebuilt on verified contracts only
- [ ] Phase 5: Contracts locked into tests (each test names the defect it prevents)
- [ ] Phase 6: Re-verified rendered — clean console, responsive, focus, reduced motion
```

## Phase 0 — Render it first

Open the actual screen. Then, in this order:

1. **Screenshot** it at a realistic viewport.
2. **Measure**, do not eyeball: dump width/left/display/gap/padding/
   max-width/overflow and `scrollHeight` vs `clientHeight` for the page
   wrapper, the scroll container, and each major block. Misalignment you
   can *see* is a symptom; the number that explains it is the finding.
3. **Read the console** — and treat the buffer as stale until proven
   otherwise. Reload, then re-read, before blaming a live error.
4. **Write the defect list** in plain language: "first tile's icon is a
   blank square", "the budget card is narrower than the row above it",
   "the button shows `global.default.refresh`". Each line becomes a row in
   the ledger and, later, a test.

Deliverable: a numbered visual defect list. No causes yet.

## Phase 1 — Locate the contract source

Find the truth on disk, not on the web — the installed version is the one
that renders. Per-ecosystem locations and enumeration commands are in
[references/contract-discovery.md](references/contract-discovery.md).

Four artifacts to pin down, each with a path:

| Artifact | You need to be able to answer |
|----------|-------------------------------|
| **Component library** | What props/slots/events does this component declare, and what enum values are actually styled? |
| **Design tokens** | Does `--x` exist? Is it a spacing step or a type size? |
| **Icon set** | Is `foo-bar` a real icon name in this version? |
| **i18n catalog** | Does this key resolve, in every shipped locale? |

Also pin the **host version** (lockfile, `composer.lock`, `Package.resolved`,
`pubspec.lock`). A contract answer is only true for a version.

## Phase 2 — Contract audit

For every component the screen uses, verify each attribute the code passes
against the declaration you located. Cite `file:line`. Record in the ledger
([references/audit-ledger.md](references/audit-ledger.md)) — one row per
defect: what the code says, what the contract says, what the user sees.

The high-yield checks, in cost-benefit order:

- **Enum props** — is that exact string in the union? Off-list values are
  the single most common cause of "unstyled but present".
- **Slot names** — exact spelling and case. `headerRight` ≠ `header-right`.
  A wrong slot name renders *nothing*, silently.
- **Required props** — omitted required props degrade quietly in
  production builds.
- **Token existence and kind** — a spacing token used as a font size is
  both wrong and invisible.
- **Icon names** — verify against the installed icon directory listing.
- **i18n keys** — resolve every key the screen references, in *all*
  locales; a key present in `en` and missing in `de` ships a raw key.
- **Deprecations** — a component that still works today but is scheduled
  for removal is a defect with a due date.

Then close the loop the other way: grep the screen for every key, icon,
and token it references and confirm each resolves. Auditing only what you
suspect leaves the rest of the file unaudited.

## Phase 3 — Ownership audit

This is where the biggest silent defects live, and it is the phase most
often skipped. Method in
[references/css-ownership.md](references/css-ownership.md). Answer three
questions:

1. **Who owns layout?** Framework wrapper components frequently position
   their root absolutely and delegate scrolling and padding to an inner
   element. Layout applied to the wrapper is *inert* — your gaps and
   max-widths do nothing and nothing warns you. Style an element you own.
2. **Can your selector win?** Compute specificity against the library rule
   you are overriding, and check load order for ties. Scoped-style
   attribute selectors (`[data-v-…]`), CSS layers, and shadow boundaries
   all change the answer. Prefer an extra owned ancestor class over
   `!important`.
3. **What does the library already impose?** Default `max-width`, default
   margins, and content padding fight hand-written grids. Reconcile
   explicitly — one owner per axis.

## Design Gate

Only now, with the defect ledger in hand, decide what the screen should
be. Present in chat, briefly:

- **Information architecture** — what the viewer needs first; what gets
  cut. Prefer deleting a redundant element over restyling it: a repeated
  page title, or a "quick actions" row pointing where the tiles already
  point, is noise the redesign should remove.
- **Visual plan** — the host system's primitives you will use, and which
  ledger rows each change closes.
- **Dependency decision** — stated either way. If a new package is
  warranted, name what the host cannot do. If not, say so plainly rather
  than staying silent: "no new dependency; the accessible form for
  ≤5-category part-to-whole is a stacked meter, which is CSS."
- **Accessibility intent** — what carries meaning besides colour.

Ask once. If the user cannot respond (headless), proceed with the
lowest-risk reading and tag the design choices `UNCONFIRMED`.

## Phase 4 — Rebuild

Build against verified contracts only. While rebuilding:

- Use the library's own escape hatches (icon slots, size props,
  full-width modifiers) rather than re-implementing them with custom CSS.
- Route every number and date through the platform's formatters — raw
  floats and ISO timestamps in a cell read as broken, and a dead
  `formatDate` helper nobody called is a tell that this was never wired.
- Make the primary target the whole element, and use a real link or button
  so keyboard and middle-click work.
- Never encode meaning in colour alone — put the value or share in text.
- Give hover motion a `prefers-reduced-motion` opt-out and keep a visible
  `:focus-visible` ring.
- Leave a comment where you fight a framework default, saying *why* — the
  next person will otherwise "clean up" your specificity fix.

## Phase 5 — Lock the contracts in

An audit that lives only in chat gets re-broken next sprint. Write tests
that fail on reintroduction — patterns per ecosystem in
[references/contract-tests.md](references/contract-tests.md). Each test
names the defect it prevents in a comment. Cheap, high-value asserts:

- Every enum value used appears in the library's allowed set.
- No non-existent slot name; no deprecated component name.
- Every `font-size` uses a type token, not a spacing token.
- Every i18n key the screen references resolves in every locale.
- Every route the screen navigates to is registered.

Then run the **whole** suite, not just yours. Distinguish failures you
caused from failures already there, and say which is which.

## Phase 6 — Re-verify rendered

Repeat Phase 0 against the rebuild and compare like for like:

- Screenshot at wide and narrow; no horizontal scroll, no orphaned column.
- Re-measure: the numbers that explained each defect must have moved.
- Console clean — after a reload, so you are not reading stale errors.
- Keyboard: tab to the interactive elements, confirm the focus ring.
- Click through at least one link you claimed to fix.

Report inline: the defect list from Phase 0 with each row marked
**FIXED / PARTIAL / OUT-OF-SCOPE**, the root-cause classes found, the
dependency decision, and any pre-existing failures you deliberately left
alone.

## When things go wrong

| Situation | Response |
|-----------|----------|
| **Cannot reach the screen (auth wall)** | Ask the user to log in; never type credentials. Audit source meanwhile, mark findings UNVERIFIED until rendered |
| **Library source not on disk (CDN/binary only)** | Use the version-pinned published types/docs, say the evidence is second-hand, and verify each contract in the browser instead |
| **Contract is a private/internal API** | Prefer a public alternative; if none, isolate the usage in one place with a comment naming the risk |
| **Override keeps losing to library CSS** | Ownership audit, not `!important` — check specificity ties, load order, scoped attributes, layers, shadow DOM |
| **Console errors persist after the fix** | Reload and re-read; buffers keep stale entries. Then confirm the DOM actually contains the offender before chasing it |
| **The defect is in the data, not the UI** | Render an explicit empty/fallback state — a blank primary cell reads as a rendering fault, not as missing data |
| **Screen links to a half-built destination** | Fix the wiring so the link lands correctly; report the destination's own defects instead of silently absorbing them |
| **Test deps or lockfile wiped by the host build** | Reinstall after the build, not before; note the ordering trap so the next run does not repeat it |
| **Design system genuinely lacks the primitive** | Then a dependency is justified — state what is missing, the cost, and keep the host's tokens for colour and spacing |
