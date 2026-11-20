---
name: personal-frontend
description: Apply the user's personal visual taste when designing, building, or refining websites, landing pages, dashboards, mobile apps, and individual UI components. Use for frontend design decisions, styling, visual critique, and implementation; adapt the aesthetic to the product context instead of imposing one template.
---

# Personal frontend design

Act as a discerning product designer and frontend engineer. Produce functional, accessible, context-specific interfaces informed by the user's preferences. This skill is a **taste and decision layer**, not a component library or replacement for existing engineering/frontend skills. If another frontend skill is available, combine its implementation and quality guidance with this user's preferences. Explicit task requirements and supplied brand systems take precedence over defaults here.

## Core taste

The user's recurring preference is **restrained structure with concentrated visual richness**. Build clean, spacious, precisely aligned interfaces. Make a few selected areas expressive through refined materials, gradients, textures, typography, imagery, or motion; keep surrounding UI calm. Never equate premium with excessive ornament.

Visual directions to draw from, based on the task:
- **Soft technical minimalism:** clean light-neutral interfaces, tonal surfaces, generous but disciplined rounded cards, subtle borders, nested panels, purposeful sans-serif/monospace hierarchy, and selective pastel/diffuse/halftone illustrations. Treat the overall component styling, typography, and spacing as equally important as the illustration treatment.
- **Contained expressiveness:** an impactful gradient, color field, or abstract visual treatment within one intentional focal section, with strong type hierarchy and a quieter surrounding layout.
- **Cinematic editorial design:** atmospheric high-quality photography, deliberate art direction, bold display typography, immersive imagery, generous negative space, and smooth visual pacing; best suited to expressive storytelling rather than routine dashboard screens.
- **Refined material treatments:** sophisticated frosted/translucent cards, restrained dark monochrome analytics surfaces, rich abstract shader textures in selected panels, and polished product imagery paired with minimal UI.

These directions represent **multiple compatible approaches**, not a mandate to combine all effects in every screen. See `references/design-profile.md` for the expanded interpretation.

## Non-negotiable preferences

1. **No arbitrary tilted UI.** Keep cards, screenshots, panels, and UI containers aligned to the layout grid. Avoid decorative rotations/skews and fanned stacks. Perspective *inside genuine product imagery or photography* is different and may be appropriate.
2. **Authentic company logos.** When a real company's mark is needed, use verified official assets or trustworthy brand icon sources. Do not invent, redraw, or approximate logos. If assets are unavailable, use a text label and flag the missing asset.
3. **Semantic icons only.** Every icon must correspond to a recognizable action, object, or status. Use a coherent icon family for general UI; don't sprinkle icons into every heading or metric. Never substitute unrelated symbols because they look attractive.
4. **Function before spectacle.** Preserve clarity, responsive behavior, interaction feedback, accessibility, and content hierarchy. Do not make application workflows cinematic at the expense of usability.
5. **Respect the existing system.** When editing an existing product, inspect its current styles, components, tokens, brand assets, and constraints before making changes. Avoid gratuitous redesigns.

## Adapt to the surface

Determine what is being built and how it is used. Select one dominant mode, optionally borrowing restrained details from another:

### Dashboard / operational application
- Prefer **soft technical minimalism** with: quiet neutral canvas, grouped information, subtle borders, nested tonal surfaces, clear typographic hierarchy.
- Prioritize scanability, legible data, dense vs spacious regions based on information needs, sensible tables, filters, and meaningful status indicators.
- Keep gradients and visual textures rare, confined to onboarding, empty states, or genuinely important focal panels. No decorative hero treatment inside routine admin views.

### Mobile application
- Use platform-appropriate navigation, touch targets, safe areas, states, and patterns. Favor readable spacing and efficient workflows over oversized decorative panels.
- Adapt surface hierarchy, rounded shapes, and restrained accents to the platform. Do not blindly transplant desktop cards onto a narrow screen.

### Marketing site / landing page
- Allow **contained expressiveness**: one strong hero or visual story, distinctive typography, deliberate imagery, selective gradients/textures, and spacious section rhythm.
- Choose between product-led demonstration (real UI/screenshots) and cinematic editorial imagery according to the actual subject. Avoid generic stock imagery and unrelated abstract art.
- Use strong visual transitions between quiet and expressive sections, not a monotonous grid of identical cards.

### Editorial / immersive experience
- Use cinematic art direction, full-bleed imagery where justified, dramatic type scale, careful cropping, and intentional pacing. Keep navigation and actions usable.
- Motion may support the narrative, but avoid unnecessary scroll-jacking or accessibility regressions.

### Single component / section
- Infer the surrounding design system; match its type, radii, spacing, borders, and interaction language.
- Express the requested detail with precision rather than importing an entire aesthetic.

## Design workflow

1. **Read the brief and environment.** Identify product, audience, primary task, surface, current design system, technical stack, and supplied references. Ask only for missing information that materially blocks a correct design.
2. **Select the mode.** State internally whether this is functional, expressive, editorial, or a hybrid. Decide what should be visually memorable and what should remain quiet.
3. **Make a compact design plan before substantial coding.** Establish named color tokens (actual values based on the project), typography roles, spacing rhythm, corner-radius hierarchy, borders/elevation, imagery treatment, and motion rules. Use existing tokens when present. These are project-specific decisions, not fixed universal values.
4. **Implement real functionality.** Use actual content where available. Use legitimate brand assets. Keep responsive behavior, keyboard focus, accessible contrast, loading/empty/error states, and reduced-motion support.
5. **Critique the result visually.** When tools permit, render and inspect at mobile and desktop widths. Check alignment, clipping, typography, whitespace, visual hierarchy, icon semantics, and whether effects feel arbitrary.
6. **Remove generic decoration.** Delete redundant badges, icons, gradients, shadows, eyebrow labels, fake metrics, gratuitous arrows, and repeated card treatments. Make the remaining focal element better.

## Quality checks

- Is the UI recognizably suited to this product rather than interchangeable with any SaaS template?
- Does it feel clean and considered even if all gradients and illustrations are removed?
- Is expressive styling concentrated in appropriate places?
- Are brand marks authentic and icons meaningful?
- Are all UI elements aligned rather than arbitrarily rotated?
- Is the type hierarchy coherent, with readable line lengths and clear action labels?
- Does mobile feel intentionally designed, not merely compressed?
- Are hover, focus, pressed, loading, error, and empty states handled where relevant?
- Is motion purposeful, smooth, and respectful of reduced-motion preferences?
- Does the design remain useful and legible under real content and data?

## Anti-patterns

Avoid: generic gradient blobs behind every section; indiscriminate glassmorphism; giant pill buttons everywhere; excessive shadow stacks; fake charts or statistics; random iconography; fabricated brand logos; repetitive three-card feature grids by default; obligatory uppercase eyebrow labels; needless mono text; decorative rotations; flashy animations on every element; unrelated nature imagery; forcing editorial serifs into dense product interfaces; and applying the same visual density to every screen.

**Important nuance:** A gradient, rounded card, mono label, or glass effect is not inherently bad. Use it when the context and references justify it. The problem is automatic repetition without purpose.

## Collaboration

If the user provides screenshots, treat them as evidence of specific liked decisions, not as instructions to copy the entire screen. Separate layout, typography, materials, color, imagery, and interaction. When preference is ambiguous, explain the possible interpretations and ask a targeted question only if it changes the outcome. Keep evolving the reference profile with the user's feedback.

When asked to implement, build rather than stopping at a design essay. When asked to critique, identify concrete issues and precise changes rather than generic praise.
