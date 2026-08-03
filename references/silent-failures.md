# The silent-failure catalog

UI defects that throw **no error**, pass **every build**, and survive
**every type check** — because the value is a well-typed string that
happens to mean nothing to the receiver.

Work this table top to bottom in Phase 2. Each row: what the code does,
what the user sees, and the probe that proves it.

## 1. Off-list enum value

**Code** `variant="danger"` on a component whose union is
`"neutral" | "info" | "attention" | "critical" | "positive"`.

**User sees** The element present but unstyled — a badge with text and no
pill, a "0" with no chip next to siblings that have one. Reads as a
rendering bug, or as deliberate design.

**Why silent** The class is composed by template string
(`` `c--variant-${props.variant}` ``), so an off-list value produces a
class that simply has no rule. Runtime prop validation usually only warns
in dev builds, and often not at all for string unions.

**Probe** Read the union from the component source, then diff against
every value the code passes. In the browser, list the rendered classes and
look for a variant class with no matching CSS rule:

```js
[...document.querySelectorAll('.the-component')].map(e => e.className)
```

**Tell in review** Names from a *different* vocabulary than the library's:
`primary` / `danger` / `success` / `warning` where the library says
`neutral` / `critical` / `positive` / `attention`. Someone typed Bootstrap
into a non-Bootstrap system.

## 2. Wrong slot / named-child spelling

**Code** `#header-right` where the component declares `headerRight`.
`slot="trailing"` where it is `slot="suffix"`.

**User sees** The content is **entirely absent**. No gap, no placeholder —
as if it was never written.

**Why silent** Unknown named slots are dropped. Nothing enumerates the
slots you *passed* against the slots that exist.

**Probe** Confirm the container element for that slot is non-empty in the
DOM:

```js
[...document.querySelectorAll('.the-card')]
  .map(c => ({ title: c.querySelector('.the-card__title')?.textContent,
               right: c.querySelector('.the-card__right-slot')?.innerHTML.length || 0 }))
```

An entire column of `right: 0` means every one of those buttons is missing.

**Tell in review** kebab-case where the library uses camelCase (or the
reverse). Vue/Svelte props tolerate both; slot names do not.

## 3. Undefined CSS custom property

**Code** `font-size: var(--scale-size-13)` where no such token exists.

**User sees** No type hierarchy — "secondary" labels the same size as body
text, because the *whole declaration* is thrown away, not just the value.

**Why silent** An unresolvable `var()` makes the property invalid at
computed-value time: it becomes `unset` (inherit or initial). There is no
console warning, and the fallback is not "the number in the name".

**Probe** Grep every `var(--…)` in your stylesheet and confirm each name
exists in the token deliverable. Guard it with a test (Phase 5).

**Tell in review** Token names containing a number that is *not* on the
scale — a scale of 2/4/6/8/10/12/14/16/20/24 has no `13`. Also: a spacing
token used for a font size, which is wrong even when the token exists.

## 4. Non-existent icon name

**Code** `name="regular-building"` where the set ships
`regular-officebuilding`.

**User sees** A blank square, or an empty tinted box where a glyph should
be — sometimes the only broken tile in a row of four.

**Why silent** Icon components typically fetch or resolve lazily and
swallow the miss; the wrapper box is already styled, so the layout looks
intentional.

**Probe** List the installed icon directory and test each name you use:

```bash
for i in officebuilding users clock file-text; do
  [ -f "$ICON_DIR/$i.svg" ] && echo "OK   $i" || echo "MISS $i"
done
```

Then confirm in the DOM that the rendered icon class matches what you
intended.

**Gotcha** Console errors for icons persist in the buffer across a reload.
Reload, re-read, and confirm the offender is in the current DOM before
chasing it.

## 5. Missing i18n key

**Code** `t('global.default.refresh')` where the platform catalog has
`add`, `apply`, `cancel`, `save`… but no `refresh`.

**User sees** The raw key rendered as the label:
`global.default.refresh` on a button.

**Why silent** Most i18n runtimes fall back to echoing the key. That is a
deliberate, useful default — and it means a typo ships as UI text.

**Probe** Resolve every key the screen references against every shipped
locale catalog. A key that exists in `en` and not in `de` is a
locale-specific defect that an English-only check misses.

**Tell in review** Borrowing a key from a *host* namespace you did not
verify. Host catalogs are large; that makes them feel safe to guess at.

## 6. Styling a framework-owned wrapper

**Code** `flex`, `gap`, `padding`, `max-width` applied to a layout
component's root, when that root is `position: absolute` and its single
child is the real scroll container.

**User sees** Sections jammed together with no spacing; double padding;
a scrollbar inset from the viewport edge; `margin: 0 auto` that centres
nothing.

**Why silent** Every declaration is valid CSS and applies successfully —
to an element with one child, where `gap` has nothing to space.

**Probe** Walk the wrapper chain and print, for each level, `display`,
`gap`, `padding`, `maxWidth`, `overflowY`, `position`, plus `scrollHeight`
vs `clientHeight`. The scroll owner is the level where they differ. Then
list the scroll owner's children — those are the elements your gap needs
to be spacing.

**Fix** Put your own element inside the wrapper and lay out there. See
[css-ownership.md](css-ownership.md).

## 7. Specificity tie lost to load order

**Code** `.my-card.lib-card { max-width: none }` against the library's
`.lib-card[data-v-abc] { max-width: 60rem }`.

**User sees** One card narrower than its neighbours and centred, breaking
the grid — the override "did nothing".

**Why silent** Both selectors are (0,2,0). Ties go to whichever stylesheet
loads later, and the library's usually does.

**Probe** Compare the computed value against the rule you wrote; if they
disagree with equal specificity, it is order.

**Fix** Add one owned ancestor class to reach (0,3,0). Reserve
`!important` for genuinely last-resort cases, and comment it.

## 8. Omitted required prop

**Code** An empty-state component declared with a required `description`,
rendered without one.

**User sees** A cramped or lopsided component missing its supporting line.

**Why silent** Required-prop warnings are dev-only in most frameworks and
absent in production builds.

**Probe** Diff the component's required props against what each usage
passes. Assert it in a test — split the template on the tag and check each
occurrence.

## 9. Deprecated-but-working component

**Code** A wrapper component marked `@deprecated — removed in vNext`.

**User sees** Nothing today. Everything, one upgrade from now.

**Probe** Grep the library source for `@deprecated` near the components
you use. Treat a hit as a defect with a due date, and record the
replacement in the ledger.

## 10. Unformatted values

**Code** A raw float and an ISO timestamp passed straight into table cells.

**User sees** `45000` where money belongs; `2026-07-26T09:12:00+00:00`
where a date belongs. Instantly reads as unfinished.

**Why silent** Both are valid strings. Nothing knows the column meant
money.

**Tell in review** A `formatDate`/`formatAmount` helper defined in the
component and **never called from the template** — strong evidence the
view was written but never looked at.

**Fix** Route through the platform's own formatter so locale, timezone,
and currency follow the user's session rather than the machine's.

## 11. Meaning carried by colour alone

**Code** Three coloured chips distinguishing statuses, with the count
encoded only by hue.

**User sees** (if colour-blind, or on a poor display) three
indistinguishable chips.

**Fix** Put the number and the share in text next to the swatch. For
≤5-category part-to-whole, a 100% stacked meter with a labelled legend
beats a pie: pies rely on colour and area, and fail accessibility review
as a primary representation.

## 12. Non-existent route / dead navigation

**Code** A page whose links point at a route name that was never
registered, falling back to some parent path.

**User sees** A button that "works" but lands on the wrong screen.

**Probe** Extract every route name the screen navigates to and assert each
is registered. This is the cheapest test in Phase 5 and catches an entire
class of half-wired features.

## Quick triage by symptom

| Symptom | Suspect first |
|---------|---------------|
| Element present, unstyled | 1 (off-list enum) |
| Element entirely missing | 2 (slot name) |
| No type hierarchy / sizes look flat | 3 (undefined token) |
| Blank square where a glyph belongs | 4 (icon name) |
| Raw dotted string as a label | 5 (i18n key) |
| No spacing between sections; double padding | 6 (wrapper ownership) |
| One block narrower/centred vs its row | 7 (specificity tie) or library default max-width |
| Component looks cramped, missing a line | 8 (required prop) |
| Raw numbers or ISO dates in cells | 10 (unformatted values) |
| Button goes to the wrong screen | 12 (dead route) |
