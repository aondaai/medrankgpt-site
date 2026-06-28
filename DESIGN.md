# Design System — MedRankGPT

> Source of truth for every visual and UI decision. Read this before touching any
> markup, style, or component. Do not deviate without explicit approval.
> Tokens: [`design-system/tokens.css`](design-system/tokens.css). Component library:
> [`design-system/`](design-system/), synced to the "MedRankGPT Design System"
> project on claude.ai/design.

## Product Context
- **What this is:** "Feito-para-você" consultancy that positions doctors and clinics
  as the answer ChatGPT, Google AI, Gemini and Perplexity recommend — SEO + AEO/GEO +
  offsite mentions, within CFM rules.
- **Who it's for:** Tier A premium/elective specialists, clinics/medical groups,
  health marketing managers. PT-BR / Brazil.
- **Project type:** Marketing site (landing) + client report/dashboard views.
- **The one memorable thing:** a **living, vibrant proof that you are the doctor the
  AI recommends** — energetic and human, never a cold clinical template.

## Aesthetic Direction
- **Direction:** "Crescimento" (Vitality) — light, vibrant, **product-led**.
  Energy comes from real product UI + a crafted abstract-clinical illustration, on a
  clean light base. References: **Ryze** (vibrant, illustrated, bold grotesk, live
  dashboards) + **Zocdoc** (healthcare warmth + trust). Deliberately NOT the muted
  editorial "tasteful AI default", and NOT the dark AEO-tools crowd.
- **Decoration level:** expressive but disciplined — vibrant palette, a signature
  illustrated hero motif, colorful data viz. No default gradients-as-skin, no blobs,
  no stock-photo hero.
- **Mood:** energetic, optimistic, credible, results-driven. "Growth on autopilot,
  for medicine."

## Typography
- **Display / Hero:** **Satoshi** (700 / 900) — big, bold, confident grotesk; tight
  tracking (-.025em). Highlight key words with a **lime underline-block** (`.hl`).
- **Body / UI:** **Satoshi** (400 / 500) — friendly geometric sans, approachable +
  legible (Zocdoc register).
- **Data / Metrics:** **Geist Mono** (400–600) — Índice, share of voice, deltas.
  Measurement reads like a live instrument.
- **Loading:** Satoshi via Fontshare
  (`https://api.fontshare.com/v2/css?f[]=satoshi@400,500,700,900&display=swap`);
  Geist Mono via Google Fonts.
- **Scale (px / line-height):** display-xl 60/1.0 · display-lg 48/1.04 ·
  display-md 36/1.08 · h1 30/1.12 · h2 24/1.2 · h3 20/1.3 · body-lg 18/1.6 ·
  body 16/1.6 · body-sm 14/1.55 · caption 13/1.5 · mono-sm 12/1.4 ·
  overline 11/1, uppercase, letter-spacing .1em.

## Color
- **Approach:** vibrant, but anchored. ONE lead (emerald), warm/cool energy accents,
  near-black ink and clean light neutrals. Color carries energy AND meaning.
- **Primary — Emerald `#0BA56A`** (health + growth + "rank up"). Hover `#0A8F5C`,
  deep/accessible-on-light `#075E45`, soft tint `#E6F7EF`. On-primary `#FFFFFF`.
- **Ink button — `#0C1410`** (near-black; the confident Ryze "dark CTA").
  On-ink `#FFFFFF`.
- **Support — Indigo `#1E3A8A`** (trust/depth) + soft `#E7ECFB`.
- **Energy accents:** lime `#9AE600` (highlights, the headline underline) ·
  coral `#FF6B4A` (warmth, attention) · amber `#FF9E2C`.
- **Data viz ramp (vibrant, ordered):** emerald `#0BA56A` · blue `#2D6BFF` ·
  lime `#9AE600` · coral `#FF6B4A` · amber `#FF9E2C`. Use this set for charts so
  dashboards "pop" (the Ryze move).
- **Neutrals:** white `#FFFFFF` · bg-subtle (mint) `#F1FAEF` · surface-2 `#F7FAF6` ·
  border `#E4EAE4` · border-strong `#D4DCD4` · ink `#0C1410` · muted `#5B6660` ·
  subtle `#8A938C`.
- **Semantic:** success `#0BA56A` · warning `#FF9E2C` · error `#E23D2E` ·
  info `#2D6BFF`.
- **Dark mode:** green-black bg `#07120D`, surface `#0E1A14`, text `#ECF3EE`,
  border `rgba(236,243,238,.12)`; primary lightens to `#2BD68C`, lime/coral keep.
  Defined in `tokens.css` under `[data-theme="dark"]`.
- **Contrast:** body on white ≥ 7:1; lime is a HIGHLIGHT/fill, never body text on
  white (use emerald-deep `#075E45` for green text). On-emerald & on-ink ≥ 4.5:1.

## Spacing
- **Base unit:** 4px. **Density:** comfortable, generous (product-landing rhythm).
- **Scale:** 2xs 2 · xs 4 · sm 8 · md 16 · lg 24 · xl 32 · 2xl 48 · 3xl 64 · 4xl 96.

## Layout
- **Approach:** product-led marketing — bold hero with real UI + illustrated motif,
  clear modular sections, generous whitespace, vibrant section tints alternating
  white / mint / indigo-soft.
- **Grid:** 12 columns, 24px gutter. **Max content width:** 1180px. Measure ≤ 64ch.
- **Border radius (friendly):** sm 8 · md 11 (buttons, inputs) · lg 14 · xl 18
  (cards) · 2xl 24 · pill 999 (tags, the medal).

## Elevation
- **e1:** `0 1px 3px rgba(12,20,16,.06)` — subtle.
- **e2:** `0 6px 18px rgba(12,20,16,.07), 0 2px 6px rgba(12,20,16,.05)` — cards.
- **e3:** `0 22px 50px rgba(12,20,16,.12)` — raised / floating product UI.
- **e-primary:** `0 12px 28px rgba(11,165,106,.22)` — emerald CTA glow.

## Motion
- **Approach:** lively, springy, but not silly. Honor `prefers-reduced-motion`.
- **Easing:** standard / spring `cubic-bezier(.2,.8,.2,1)`; exit `cubic-bezier(.4,0,1,1)`.
- **Duration:** micro 90ms · short 180ms · medium 260ms · long 420ms.
- **Hover:** lift `translateY(-2px)` + shadow/scale; charts can animate in.

## Signature Elements (what kills the "AI template" feel)
- **Real product UI as proof:** the **Índice MedRankGPT** dashboard — share of voice
  per engine, deltas, citation rows — rendered with the vibrant data-viz ramp and
  Geist Mono. See `patterns/dashboard.html`. This is the centerpiece, like Ryze's
  live dashboard.
- **Abstract-clinical hero illustration:** a crafted organic motif (pulse/ECG line +
  abstract botanical/growth forms + soft mesh) in the brand palette — NOT stock
  photos, NOT default gradients. See `foundations/illustration.html`; applied in
  `patterns/hero.html`.
- **Bold grotesk + lime highlight:** big Satoshi 900 headlines with key words on a
  lime underline-block.

## Component Notes
- **Buttons:** primary (emerald), ink (near-black, Ryze CTA), accent (coral),
  ghost (bordered). Radius md (11), friendly. Sizes sm/md/lg. Hover lift 2px.
- **Badges:** overline (mono), pill tag, the "Recomendado pela IA" medal (emerald
  pill), status pills, trust chips.
- **Cards:** Índice metric, pillar, featured plan (emerald border + e3 + medal).
- **Forms:** light inputs, emerald focus ring, friendly radius.
- **Dashboard:** the live Índice/share-of-voice UI (vibrant ramp).

## Decisions Log
| Date | Decision | Rationale |
|------|----------|-----------|
| 2026-06-28 | Direction "Crescimento" (emerald-led, vibrant, product-led) | Replaces the muted "Clinical Authority" v1; user found that too "AI-template". Pivot toward Ryze energy + Zocdoc trust with vibrant color. |
| 2026-06-28 | Emerald primary + indigo support + lime/coral energy; drop gold/serif | User wants vibrant color and a bolder, less-editorial feel; emerald = health/growth, vibrant data-viz ramp gives the Ryze "pop". |
| 2026-06-28 | Satoshi (bold grotesk), real Índice dashboard, abstract-clinical hero art | Bold type + real product UI + crafted illustration are the three levers that remove the generic-AI-site look. |
