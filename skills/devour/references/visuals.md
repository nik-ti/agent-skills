# Visuals

A visual earns its place when it shows a mechanism the reader would otherwise have to assemble from prose: how data flows, which parts talk to each other, what changes between two options, how something moves through stages. If a sentence says it faster, keep the sentence. For technical material, expect a diagram for most major concepts. For softer topics, a few well-chosen ones are enough.

## Choosing a form

| The idea is... | Use |
|---|---|
| A process or pipeline | Flow diagram, left to right |
| An architecture or layered system | Stacked boxes showing what talks to what |
| A relationship between concepts | A small concept map with labelled edges |
| A choice or trade-off | Two options side by side, or a 2×2 |
| A sequence that builds up | Stepper explainer |
| Before and after, or A versus B | Tabs explainer |
| An effect that depends on a number | Small custom slider explainer |
| Change over time | Timeline, or a simple chart from real numbers |

Interactive pieces are for when doing something teaches more than seeing it. Use a few good ones, and never invent numbers to feed one: if a slider needs a formula, it has to be one from the source or plainly labelled as an illustration.

## Inline SVG diagrams

Hand-write inline `<svg>`. Mermaid and similar sources won't render here, and the page has to work offline, so no libraries, no remote images and no remote fonts.

- Wrap each one in `<figure class="diagram">` with a `<figcaption>` that states what it shows, and give the svg `role="img"` plus an `aria-label` making the same claim.
- Size it with `viewBox` only, no fixed width, and keep it 360 to 440 units wide. On a phone a diagram has about 320 pixels, so a 640-wide drawing would shrink 14-unit labels to an unreadable 7 pixels. Where there's more to show, go taller and stack vertically. The template caps diagrams at 520 pixels so they don't balloon on a desktop; add `class="wide"` to the svg only for a chart that needs the full column.
- Use `currentColor` and the template's classes for a consistent light-theme palette: `.box` for shapes, `.box.accent` for the one element that matters, `.edge` for lines, `.label` and `.label.small` for text.
- Label the arrows ("writes", "polls every 30s"). An unlabelled arrow says almost nothing.
- Keep labels to a few words, and put the explanation in the caption. Align to a grid with even gaps.
- For arrowheads, use the template's shared markers: `marker-end="url(#arrow)"`, or `url(#arrow-accent)` on an `.edge.accent` line.

Depict the mechanism, not its name. Show the parts the idea turns on and leave out the rest.

## Ready-made explainers

The template's script drives these with no extra code.

**Stepper**, for something that builds up. Each `.step` shows one at a time:

```html
<div class="explainer stepper" aria-label="How a request is handled">
  <div class="step"><svg ...>...</svg><p>First the request arrives.</p></div>
  <div class="step"><svg ...>...</svg><p>Then the cache is checked.</p></div>
</div>
```

**Tabs**, for comparing. Each `.tab` needs a `data-label`:

```html
<div class="explainer tabs" aria-label="Two ways to do it">
  <div class="tab" data-label="With a queue">...</div>
  <div class="tab" data-label="Without">...</div>
</div>
```

**Self-test**, a question with a hidden answer, which is a cheap way to make the reader recall. It needs no script:

```html
<details class="recall"><summary>Without scrolling up: why does rereading feel like it works?</summary><p>...</p></details>
```

For anything custom, such as a slider, add a `<style>` in the head and a small `<script>` at the end of the body. It must work with no network, no `alert`, and with storage wrapped in try/catch. All content stays readable with scripts off, since steppers and tabs display in full until the script runs.
