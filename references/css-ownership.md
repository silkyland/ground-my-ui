# Ownership audit

Two elements fighting over one axis is the most common cause of UI that
looks *almost* right. This phase settles, for each axis, **who owns it** —
before you write a single new rule.

Nothing here throws an error. Every declaration is valid CSS that applies
successfully to an element that cannot act on it.

## Question 1 — Who owns layout and scrolling?

Framework layout components routinely look like this:

```html
<div class="lib-view">              <!-- position: absolute; width/height: 100% -->
  <div class="lib-view__content">   <!-- padding: 40px; overflow-y: auto  ← real container -->
    <your-section />                <!-- your children live HERE -->
    <your-section />
  </div>
</div>
```

Put `class="my-layout"` on `<lib-view>` and style it with
`display: flex; gap: 24px; max-width: 1440px; margin: 0 auto; padding: 24px`
and every single declaration "works" — while achieving nothing:

- `gap` spaces the wrapper's **one** child, so sections stay jammed.
- `padding` stacks on the inner `40px`.
- `max-width` clips the scroll container, insetting the scrollbar from the
  viewport edge.
- `margin: 0 auto` cannot centre an absolutely positioned element.

### The probe

Walk the chain and print the numbers. The scroll owner is the level where
`scrollHeight` exceeds `clientHeight`:

```js
(() => {
  const info = (el, n) => {
    if (!el) return { n, missing: true };
    const cs = getComputedStyle(el), b = el.getBoundingClientRect();
    return { n, w: Math.round(b.width), left: Math.round(b.left),
             display: cs.display, gap: cs.gap, padding: cs.padding,
             maxWidth: cs.maxWidth, overflowY: cs.overflowY,
             position: cs.position,
             scrollH: el.scrollHeight, clientH: el.clientHeight };
  };
  const wrap = document.querySelector('.lib-view');
  const inner = document.querySelector('.lib-view__content');
  return JSON.stringify({
    wrapper: info(wrap, 'wrapper'),
    scroller: info(inner, 'scroller'),
    // These are the elements your gap must space. If there is exactly one,
    // your gap is doing nothing.
    kids: [...(inner?.children || [])].map(c =>
      c.className + ' w=' + Math.round(c.getBoundingClientRect().width)),
  }, null, 1);
})()
```

### The fix

Own an element. Add a plain wrapper of your own inside the framework's
container and lay out there:

```html
<lib-view>
  <div class="my-page__layout">   <!-- flex / gap / max-width live here -->
    …sections…
  </div>
</lib-view>
```

Leave a comment saying why, or someone will "simplify" it back onto the
framework root.

### The same trap elsewhere

| Stack | The wrapper you must not lay out on |
|-------|-----------------------------------|
| Scroll containers | `ScrollView` / `RecyclerView` / `FlatList` — pad the *content*, not the viewport |
| SwiftUI | Modifier order changes ownership: `.padding().background()` ≠ `.background().padding()` |
| Flutter | `Expanded`/`Flexible` only mean something to a direct `Row`/`Column` parent |
| Compose | A `Modifier` chain on the wrong composable silently no-ops the same way |
| Shadow DOM | Outside styles do not cross the boundary at all — you need parts/custom properties |

## Question 2 — Can your selector win?

Compute specificity as (id, class, type). Attribute selectors and
pseudo-classes count at the **class** level:

| Selector | Specificity |
|----------|-------------|
| `.lib-card` | (0,1,0) |
| `.lib-card[data-v-abc]` | (0,2,0) ← scoped styles |
| `.my-card.lib-card` | (0,2,0) ← **ties**; load order decides |
| `.my-page .my-card.lib-card` | (0,3,0) ← wins outright |

A tie is not a win. Library CSS usually loads after plugin/app CSS, so
**the library wins every tie**. If your computed value disagrees with the
rule you wrote and specificity is equal, it is order.

**Prefer specificity over `!important`.** One extra owned ancestor class is
readable, debuggable, and does not start an escalation war. Reserve
`!important` for genuinely unreachable cases and comment why.

Things that change the answer:

- **Scoped styles** (`[data-v-…]`, CSS modules hashes) add a class-level
  unit. A class you add from a parent *does* still match the scoped
  selector, because the scope attribute lives on the element itself.
- **`@layer`** beats specificity entirely: any unlayered rule wins over any
  layered one, regardless of specificity.
- **`:where()`** contributes zero specificity — libraries use it
  deliberately so you can override cheaply.
- **Inline styles** beat all selectors; if the library sets style
  attributes, you need a different hook (a prop, a CSS variable it reads).
- **Shadow DOM** blocks selectors outright — use `::part()`, exposed custom
  properties, or the component's own API.

## Question 3 — What does the library already impose?

Read the component's own CSS before writing yours. The usual culprits:

```bash
grep -nE 'max-width|margin|padding|gap|position' <lib>/dist/<component>.css
```

- **Default `max-width`** — a card capped at `60rem` inside a full-width
  grid row will be narrower than its neighbours and often centred by an
  `auto` margin. Check for an official opt-out (a `full-width` prop or an
  `ignore-max-width` modifier) before overriding by hand.
- **Default bottom margin** — fights your grid `gap`. Pick one owner: if
  the grid owns vertical rhythm, zero the component margin.
- **Content padding** — decides the negative margin you need to let a
  table span a card edge to edge. Use the library's own padding token so
  the two stay in sync.

## Ownership rules of thumb

1. **One owner per axis.** Either the grid spaces children (`gap`) or the
   children space themselves (`margin`) — never both.
2. **Style what you own.** Your own element, or an element you have added a
   class to for exactly this purpose.
3. **Verify by measurement, not by looking.** "Looks right" survives until
   someone opens a narrower viewport.
4. **Comment every fight with a framework default**, with the reason. The
   specificity trick that looks redundant is the one that stops working
   when someone tidies it.
