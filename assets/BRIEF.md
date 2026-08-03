# Social preview brief — ground-my-ui

Produce the GitHub social preview for the `ground-my-ui` agent skill so it
matches its ten sibling skills. Deliver **two** files in this directory:

| File | Size | Contents |
|------|------|----------|
| `social-preview-base.png` | ~1731×909 | Illustration only. Left ~40% fades out to flat cream so text can sit on it. No text. |
| `social-preview.png` | **1200×630** | The final card: base cropped/scaled to 1200×630 with the text block composited on the left. |

`README.md` already expects `assets/social-preview.png` (first line:
`![ground-my-ui social preview](assets/social-preview.png)`).

## Reference files — study these first

Sibling repos live at `~/Sites/skills/`. Open both members of at least
three pairs and match them:

- `~/Sites/skills/seed-ah/assets/social-preview-base.png` + `social-preview.png`
- `~/Sites/skills/reproduce-my-bug/assets/social-preview-base.png` + `social-preview.png`
- `~/Sites/skills/know-my-repo/assets/social-preview-base.png` + `social-preview.png`
- `~/Sites/skills/transform-my-repo/assets/`, `twin-my-site/assets/`, `jury-my-repo/assets/` for more range

**The references are the spec.** Where this brief and the reference images
disagree, the images win — measure them rather than trusting the numbers
below.

## House style (measured from the references)

**Canvas** 1200×630, flat cream background `#FEF5E5`–`#FFF9ED`.

**Illustration** A friendly anthropomorphic **cat** as the protagonist,
mid-task in a themed workspace. Warm children's-book / flat-vector
illustration: soft shading, rounded shapes, visible but gentle outlines,
no photorealism, no 3D render, no gradient-mesh glossiness. Occupies the
right ~60%; bleeds off the right and bottom edges. Props are drawn
diagrammatically (cards, boards, screens, checklists), never as real
screenshots.

**Palette** cream `#FEF5E5` · near-black ink `#10212B` · teal `#1F8F8A` ·
coral/red `#E2564A` · mustard `#E8A33D` · muted blue-grey `#7A9AAE` ·
warm wood browns. Use a *subset* — the references are restrained, not
rainbow.

**Left text block** (vertically centred, generous left margin ~80px, all
left-aligned):

1. **Skill name** — `ground-my-ui`, very heavy geometric sans (Poppins /
   Nunito ExtraBold class), ink `#10212B`, the largest element by far.
   Siblings set the name lowercase, either on one line (`seed-ah`) or
   wrapped across two (`reproduce / my bug`). Pick whichever balances the
   composition; two lines (`ground / my ui`) is likely.
2. **Subtitle** — 1–2 lines, semibold, teal `#1F8F8A`.
3. **Punchline** — one short line, bold, coral `#E2564A`.
4. *(Optional)* a small rounded pill badge, cream text on teal — only if
   the composition wants it. Several siblings omit it.

Some siblings put the subtitle above the punchline (`seed-ah`), some
below (`reproduce-my-bug`). Either is in-house.

## Copy — use exactly this

- **Name:** `ground-my-ui`
- **Subtitle:** `Verify the contracts. Then design.`
- **Punchline:** `Nothing errored. That is the problem.`

Do not invent alternative wording.

## What this skill is about (drives the illustration)

Most "ugly" UI is not a taste problem — it is code quietly lying to a
framework. An invalid variant renders unstyled; a misspelled slot renders
nothing at all; an undefined CSS custom property voids the whole
declaration; a missing translation key prints its own name. **Nothing
throws.** The skill reads the *installed* component library, token file,
icon set and translation catalog on disk, verifies every contract the
screen touches, and only then redesigns.

So the cat is an **inspector of contracts**, not a decorator. Visual ideas
(pick and combine — do not cram all of them in):

- The cat holding a **loupe or calipers** up to a UI mockup, checking it
  against an open **spec/contract book** or a pinned reference sheet.
- A UI card on the wall/easel that is **visibly half-applied**: one tile in
  a row of four is an empty outlined box where a glyph should be; one chip
  is a plain unstyled rectangle while its neighbours are proper pills; one
  button's label reads as a literal dotted key like `button.label`.
- Small ticked/crossed tags pinned beside elements — the verified vs
  invented contract.
- A measuring/alignment motif: guide lines, a ruler, one card obviously
  narrower than the row above it.
- Deliberately **no red error markers, no crash icons, no bug** — the
  point is that nothing complained. `reproduce-my-bug` owns the bug
  imagery; this skill must not duplicate it.

Keep any lettering inside the illustration to short fragments; it must not
compete with the left text block.

## Technique

Do whatever you have available, in this order of preference:

1. An image-generation tool/API you can actually reach (check your
   configured tools/MCP servers and any API key in the environment).
2. Hand-authored **SVG** rendered to PNG (`rsvg-convert`, `resvg`,
   `cairosvg`, or headless Chrome). This is a legitimate route — the house
   style is flat vector illustration, and it is fully reproducible.
3. If neither is reachable: **do not ship a placeholder.** Produce the
   compositing script plus the exact text-layer geometry, write
   `assets/STATUS.md` explaining precisely what is missing and how to
   finish it, and stop.

Whatever you use, **commit the generator** (`assets/` script or `.svg`
source) alongside the PNGs so the card can be regenerated. That is the
family's habit: a `-base` plus a repeatable text composite.

## Acceptance checks — run these before you claim done

- [ ] `social-preview.png` is exactly **1200×630**.
- [ ] `social-preview-base.png` exists, is text-free, and is ~1731×909.
- [ ] Placed beside three sibling `social-preview.png` files, it reads as
      the same set: same cream, same ink, same cat-protagonist idiom, same
      left-text/right-illustration split.
- [ ] All three copy strings appear, spelled exactly as above.
- [ ] No text is clipped; nothing important sits in the outer 24px, which
      GitHub may crop.
- [ ] Legible as a **thumbnail** — squint at it at 300px wide; the name
      must still be readable.
- [ ] No bug/error/crash imagery.
- [ ] Generator source committed next to the PNGs.
- [ ] `git status` in this repo shows only intended files (no strays, no
      temp renders).

Do not `git push` and do not create releases — leave the commit for review.
