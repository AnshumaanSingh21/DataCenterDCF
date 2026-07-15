# KPMG × Knexus.AI — Design System Starter

> **How to use this file:** Drop it into any new project and upload it to a Claude Code session. It gives the session everything needed to scaffold UI components, enforce visual consistency, or audit an existing codebase. Fill in the `[PLACEHOLDER]` fields for each new project.

---

## 0. New Project Checklist

Before building, fill these in:

```
Product name:      [e.g. "K-Nexus.AI"]
Product tagline:   [e.g. "Datacenter Lifecycle"]
Logo file:         [e.g. /public/logo.png  or  /public/kpmg-logo.png]
Primary colour:    #00338D  (KPMG Navy — keep unless brand says otherwise)
Accent colour:     #0077C8  (keep unless brand says otherwise)
App shell type:    [sidebar-app | top-nav-app | public-site]
```

---

## 1. Brand Identity

### Logo
- **File:** `/public/[logo-filename].png` — PNG with transparency, ~30 KB
- **Usage rules:**
  - Minimum display size: `h-8` (32 px height), preserve aspect ratio
  - Placement: top-left of header/navbar, vertically centred
  - Clear space: at least `px-4` on each side
  - Never recolour, stretch, or place on a busy/patterned background
  - On dark surfaces use the white/reversed variant; otherwise add a white drop-shadow via CSS

### KPMG logo URL (public SVG)
```
https://upload.wikimedia.org/wikipedia/commons/d/db/KPMG_blue_logo.svg
```
Use this as `<img src="...">` in a pinch; for production copy the asset to `/public/`.

### Product Wordmark (text-based fallback)
```
Text:    [Product Name]
Font:    Plus Jakarta Sans, font-bold (700)
Colour:  text-white  (on dark headers)
Tagline: text-[10px] font-medium text-white/50  (one line below)
```

---

## 2. Colour Tokens

Register all colours in `tailwind.config.js`. **Never write raw hex values inline in component classes — always use the token name or the exact hex from this table.**

### tailwind.config.js — colours block
```js
colors: {
  navy:           '#00338D',
  'navy-deep':    '#1A1F36',
  'navy-darker':  '#0D1428',
  accent:         '#0077C8',
  'accent-light': '#1A8FE3',
  success:        '#00A36C',
  amber:          '#D4A017',
  danger:         '#DC2626',
  'success-light':'#F0FDF4',
  'amber-light':  '#FFFBEB',
  'danger-light': '#FEF2F2',
  'grey-bg':      '#F4F6F9',
  'grey-border':  '#E2E8F0',
  'text-primary': '#1A1F36',
  'text-secondary':'#6B7280',
  'text-muted':   '#9CA3AF',
},
```

### Reference table

| Role | Token | Hex |
|---|---|---|
| Brand primary | `navy` | `#00338D` |
| Dark surface | `navy-deep` | `#1A1F36` |
| Darkest surface | `navy-darker` | `#0D1428` |
| Accent / interactive | `accent` | `#0077C8` |
| Accent lighter | `accent-light` | `#1A8FE3` |
| Success / positive | `success` | `#00A36C` |
| Warning / caution | `amber` | `#D4A017` |
| Danger / error | `danger` | `#DC2626` |
| Page background | `grey-bg` | `#F4F6F9` |
| Card / input border | `grey-border` | `#E2E8F0` |
| Primary text | `text-primary` | `#1A1F36` |
| Secondary text | `text-secondary` | `#6B7280` |
| Muted / disabled | `text-muted` | `#9CA3AF` |

### Tint / opacity system
| Suffix | Use for |
|---|---|
| `/5` | Subtle hover backgrounds |
| `/10` | Badge fill backgrounds |
| `/18` | Icon container backgrounds (inline style: `color + '18'`) |
| `/20` | Badge borders |
| `/25` | Active sidebar item fill |
| `/30` | Active sidebar item border |
| `/40`, `/60` | Secondary text on dark surfaces (`text-white/40`, `text-white/60`) |

### Dark-surface white overlays
| Value | Use for |
|---|---|
| `white/[0.08]` | Navbar / header bottom border |
| `white/[0.06]` | Sidebar right border |
| `white/10` | DarkCard border, modal/panel borders on dark bg |

---

## 3. Typography

### Font stack — tailwind.config.js
```js
fontFamily: {
  heading: ["'Plus Jakarta Sans'", 'sans-serif'],
  body:    ["'DM Sans'", 'sans-serif'],
  mono:    ["'JetBrains Mono'", 'monospace'],
},
```

Load from Google Fonts in `app/layout.jsx`:
```
Plus Jakarta Sans — weights 400 500 600 700 800
DM Sans           — weights 300 400 500 600
JetBrains Mono    — weights 400 500 600
```

### globals.css baseline
```css
body  { font-family: 'DM Sans', sans-serif; color: #1A1F36; background: #F4F6F9; }
h1,h2,h3,h4,h5,h6 { font-family: 'Plus Jakarta Sans', sans-serif; }
```
Do not override font via `font-sans` or inline `fontFamily` in components.

### Size scale
```
text-[9px]   — micro labels, icon badge counts
text-[10px]  — section group headers (always: uppercase + tracking-widest + font-bold)
text-xs      — badges, table cells, meta / supporting info
text-sm      — body text, input labels, button text (sm / md sizes)
text-base    — button text (lg), prose paragraphs
text-lg      — button text (xl)
text-2xl     — primary metric / KPI values (always: font-mono + font-bold)
```

### Typography rules
| Element | Required classes |
|---|---|
| Metric / KPI value | `font-mono font-bold text-2xl text-[#1A1F36]` |
| Section group label | `text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF]` |
| Card title | `text-xs font-semibold text-[#1A1F36]` |
| Supporting / description | `text-xs text-[#6B7280]` or `text-sm text-[#6B7280]` |
| AI / rich output headings | `font-heading` applied via `.ai-output h2/h3` CSS rule |

---

## 4. Component Specs

### 4.1 Card

Four canonical variants. Pick one; do not invent others.

#### Default card — full content
```jsx
<div className="bg-white rounded-2xl border border-[#E2E8F0]
  shadow-[0_1px_3px_0_rgba(0,0,0,0.08),0_1px_2px_-1px_rgba(0,0,0,0.06)]
  transition-all duration-200 p-6">
  {children}
</div>
```
Hover (clickable cards only):
```
hover:shadow-[0_10px_25px_-5px_rgba(0,51,141,0.12),0_4px_10px_-5px_rgba(0,51,141,0.08)]
hover:-translate-y-0.5 cursor-pointer
```

#### Dark card
```jsx
<div className="bg-[#1A1F36] rounded-2xl border border-white/10 p-6">
  {children}
</div>
```

#### Metric card (icon + number + label)
```jsx
<div className="bg-white rounded-2xl border border-[#E2E8F0] p-5
  shadow-[0_1px_3px_0_rgba(0,0,0,0.08)]
  hover:shadow-[0_4px_12px_rgba(0,51,141,0.1)]
  transition-all duration-200">

  {/* Icon container */}
  <div className="w-10 h-10 rounded-xl flex items-center justify-center mb-3"
       style={{ backgroundColor: color + '18' }}>
    <Icon size={20} style={{ color }} />
  </div>

  {/* Value */}
  <div className="font-mono font-bold text-2xl text-[#1A1F36]">
    {value}
    {unit && <span className="text-sm font-normal text-[#6B7280] ml-1">{unit}</span>}
  </div>

  {/* Label */}
  <div className="text-sm text-[#6B7280] mt-1 font-medium">{label}</div>

  {/* Optional trend badge */}
  {trend && (
    <span className={`text-xs font-semibold px-2 py-1 rounded-full
      ${trend > 0 ? 'text-[#00A36C] bg-[#00A36C]/10' : 'text-[#EF4444] bg-[#EF4444]/10'}`}>
      {trend > 0 ? '+' : ''}{trend}%
    </span>
  )}
</div>
```

#### KPI card (compact, left accent stripe)
```jsx
<div className="bg-white rounded-xl border border-[#E2E8F0] border-l-[3px] p-4
  min-w-[160px] shadow-sm hover:shadow-md transition-all duration-200"
  style={{ borderLeftColor: statusColor }}>

  <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-1">
    {title}
  </div>
  <div className="text-2xl font-semibold font-mono text-[#1A1F36]">{value}</div>
  {unit && <div className="text-xs text-[#9CA3AF] mt-0.5">{unit}</div>}
</div>
```
`statusColor` values: success `#00A36C` · warning `#D4A017` · danger `#DC2626`

**Card anti-patterns:**
- Full cards must be `rounded-2xl` — never `rounded-xl` or `rounded-lg`
- KPI/compact cards are the exception: `rounded-xl`
- Default shadow is the custom string — never bare `shadow-sm` or `shadow-md` on a card
- Padding: `p-6` for full cards, `p-5` for metric cards, `p-4` for KPI/compact

---

### 4.2 Button

Base classes (always present on every button):
```
inline-flex items-center justify-center gap-2 font-semibold rounded-lg
transition-all duration-200 cursor-pointer border-0 outline-none
focus:ring-2 focus:ring-offset-2
disabled:opacity-50 disabled:cursor-not-allowed
```

#### Variants
| Variant | Classes |
|---|---|
| `primary` | `bg-[#00338D] text-white hover:bg-[#0044b8] focus:ring-[#00338D] shadow-sm hover:shadow-md active:scale-[0.98]` |
| `accent` | `bg-[#0077C8] text-white hover:bg-[#0088e0] focus:ring-[#0077C8] shadow-sm hover:shadow-md active:scale-[0.98]` |
| `outline` | `bg-transparent text-[#00338D] border-2 border-[#00338D] hover:bg-[#00338D] hover:text-white focus:ring-[#00338D] active:scale-[0.98]` |
| `ghost` | `bg-transparent text-[#6B7280] hover:bg-[#F4F6F9] hover:text-[#1A1F36] focus:ring-[#CBD5E1] active:scale-[0.98]` |
| `danger` | `bg-[#EF4444] text-white hover:bg-[#DC2626] focus:ring-[#EF4444] shadow-sm active:scale-[0.98]` |
| `amber` | `bg-[#D4A017] text-white hover:bg-[#b8891a] focus:ring-[#D4A017] shadow-sm active:scale-[0.98]` |
| `white` | `bg-white text-[#00338D] hover:bg-[#F4F6F9] focus:ring-white shadow-sm active:scale-[0.98]` |

#### Sizes
| Size | Classes |
|---|---|
| `sm` | `px-3 py-1.5 text-sm` |
| `md` | `px-5 py-2.5 text-sm` |
| `lg` | `px-7 py-3.5 text-base` |
| `xl` | `px-8 py-4 text-lg` |

**Button anti-patterns:**
- Never `rounded-xl` or `rounded-full` — always `rounded-lg`
- Never omit `active:scale-[0.98]`
- Never Tailwind colour names (`bg-blue-600`) — use the exact hex tokens

---

### 4.3 Badge

Base: `inline-flex items-center font-semibold rounded-md border`

#### Colour schemes
| Prop | Classes |
|---|---|
| `blue` | `bg-[#0077C8]/10 text-[#0077C8] border-[#0077C8]/20` |
| `navy` | `bg-[#00338D]/10 text-[#00338D] border-[#00338D]/20` |
| `green` | `bg-[#00A36C]/10 text-[#00A36C] border-[#00A36C]/20` |
| `amber` | `bg-[#D4A017]/10 text-[#D4A017] border-[#D4A017]/20` |
| `red` | `bg-red-50 text-red-600 border-red-200` |
| `grey` | `bg-[#F4F6F9] text-[#6B7280] border-[#E2E8F0]` |

#### Sizes
| Prop | Classes |
|---|---|
| `xs` | `px-1.5 py-0.5 text-xs` |
| `sm` | `px-2 py-1 text-xs` |
| `md` | `px-3 py-1.5 text-sm` |

#### Status dot (optional, inside badge)
```jsx
<span className="w-1.5 h-1.5 rounded-full mr-1.5 inline-block" style={{ backgroundColor: dotColor }} />
```
Dot colour matches badge text colour. Common: active `#00A36C` · pending `#D4A017` · inactive `#0077C8`

---

### 4.4 Icon Containers

```jsx
{/* Medium — MetricCard, section headers */}
<div className="w-10 h-10 rounded-xl flex items-center justify-center"
     style={{ backgroundColor: color + '18' }}>
  <Icon size={20} style={{ color }} />
</div>

{/* Small — inline / compact */}
<div className="w-7 h-7 rounded-lg flex items-center justify-center"
     style={{ backgroundColor: color + '18' }}>
  <Icon size={14} style={{ color }} />
</div>
```

Icon library: **lucide-react**. Always use the `size` prop, not Tailwind `w-` / `h-` on the `<Icon>` itself.

Common icon sizes: `size={12}` `size={14}` `size={16}` `size={18}` `size={20}` `size={24}`

---

### 4.5 Section Group Label
```jsx
<div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-2">
  Group Name
</div>
```
Used above: sidebar nav groups, context panel sections, card sub-sections.

---

### 4.6 Dividers
```jsx
<div className="border-t border-[#E2E8F0]" />       {/* light surfaces */}
<div className="border-t border-white/[0.08]" />     {/* dark surfaces */}
```
Never `border-gray-200`, `border-slate-200`, or other Tailwind named colours.

---

### 4.7 Input Fields
```jsx
<input className="w-full px-3 py-2 text-sm rounded-lg border border-[#E2E8F0]
  bg-white text-[#1A1F36] placeholder:text-[#9CA3AF]
  focus:outline-none focus:ring-2 focus:ring-[#0077C8]/30 focus:border-[#0077C8]/50
  transition-all duration-200" />
```

---

### 4.8 Loading Dots
```jsx
<div className="flex items-center gap-1.5">
  {[0,1,2].map(i => (
    <div key={i} className="typing-dot w-2 h-2 rounded-full bg-[#0077C8]" />
  ))}
</div>
```
CSS (in globals.css):
```css
@keyframes pulse-dot {
  0%, 80%, 100% { transform: scale(0.6); opacity: 0.4; }
  40%           { transform: scale(1);   opacity: 1; }
}
.typing-dot:nth-child(1) { animation: pulse-dot 1.4s infinite ease-in-out 0s; }
.typing-dot:nth-child(2) { animation: pulse-dot 1.4s infinite ease-in-out 0.2s; }
.typing-dot:nth-child(3) { animation: pulse-dot 1.4s infinite ease-in-out 0.4s; }
```

### 4.9 Shimmer Skeleton
```jsx
<div className="shimmer h-4 rounded-lg w-3/4" />
```
CSS:
```css
@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.shimmer {
  background: linear-gradient(90deg, #f0f4f8 25%, #e2e8f0 50%, #f0f4f8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}
```

---

## 5. Layout System

### App Shell — Sidebar (collapsible)
```
Collapsed width:  w-16
Expanded width:   w-64
Background:       bg-[#0D1428]
Right border:     border-r border-white/[0.06]
Transition:       transition-all duration-300
```

Nav item (inactive): `px-2.5 py-2 rounded-lg border border-transparent text-white/40`
Nav item (active): `px-2.5 py-2 rounded-lg bg-[#00338D]/25 border border-[#00338D]/30 text-[#0077C8]`

### App Shell — Header
```
Height:      h-14  (app shell)  |  h-16  (marketing/public pages)
Background:  bg-[#1A1F36]/95
Blur:        backdrop-filter: blur(20px)
Border:      border-b border-white/[0.08]
```

### Page Content Container
```jsx
<div className="max-w-screen-xl mx-auto px-6 py-8">
```
Standard inner padding: `px-4 pb-6 space-y-4`

### Common Grid Layouts
| Pattern | Classes |
|---|---|
| Single column | `grid grid-cols-1` |
| Two-column (large screens) | `grid grid-cols-1 xl:grid-cols-2 gap-4` |
| Three-column | `grid grid-cols-1 md:grid-cols-3 gap-4` |
| Form + output split (2:3) | `grid grid-cols-1 lg:grid-cols-5 gap-6` |

### Context / Detail Side Panel
```jsx
<div className="w-80 flex-shrink-0 bg-white border-l border-[#E2E8F0] p-4 overflow-y-auto">
```

### Standard Spacing
| Context | Value |
|---|---|
| Grid gap | `gap-4` |
| Tight list | `space-y-2` or `space-y-3` |
| Section spacing | `space-y-4` |
| Card inner sections | `mb-3` or `mb-4` |
| Inline icon + text | `gap-1.5` or `gap-2` |

---

## 6. Animation & Interaction

### Transition rules
| Context | Class |
|---|---|
| All interactive elements | `transition-all duration-200` |
| Sidebar collapse/expand | `transition-all duration-300` |
| Colour-only changes | `transition-colors` |

### Card hover lift
```
hover:-translate-y-0.5
hover:shadow-[0_10px_25px_-5px_rgba(0,51,141,0.12),0_4px_10px_-5px_rgba(0,51,141,0.08)]
```

### Button press
```
active:scale-[0.98]
```

### Framer Motion — standard page/card enter
```jsx
<motion.div
  initial={{ opacity: 0, y: 8 }}
  animate={{ opacity: 1, y: 0 }}
  transition={{ duration: 0.3 }}
>
```

### Special CSS effects (globals.css)
```css
/* Glassmorphism — light */
.glass {
  background: rgba(255,255,255,0.08);
  backdrop-filter: blur(16px);
  border: 1px solid rgba(255,255,255,0.12);
}

/* Glassmorphism — dark */
.glass-dark {
  background: rgba(26,31,54,0.82);
  backdrop-filter: blur(20px);
  border: 1px solid rgba(255,255,255,0.08);
}

/* Navy gradient hero/header */
.bg-navy-gradient {
  background: linear-gradient(135deg, #00338D 0%, #1A1F36 55%, #0D1428 100%);
}

/* Subtle navy gradient (sidebar, panels) */
.bg-navy-gradient-subtle {
  background: linear-gradient(180deg, #1A1F36 0%, #0D1428 100%);
}

/* Dot-grid background overlay */
.bg-grid-pattern {
  background-image:
    linear-gradient(rgba(0,119,200,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,119,200,0.05) 1px, transparent 1px);
  background-size: 48px 48px;
}
```

### Scrollbar (globals.css)
```css
::-webkit-scrollbar        { width: 5px; height: 5px; }
::-webkit-scrollbar-track  { background: #F4F6F9; }
::-webkit-scrollbar-thumb  { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }
```

---

## 7. Consistency Rules & Anti-Patterns

> Give these rules to Claude Code when auditing a codebase. Violations of any rule below are refactor targets.

### Border radius
| Element | Correct | Anti-pattern |
|---|---|---|
| Full content card | `rounded-2xl` | `rounded-xl`, `rounded-lg` |
| Compact card / panel | `rounded-xl` | `rounded-2xl`, `rounded-lg` |
| Button | `rounded-lg` | `rounded-xl`, `rounded-full` |
| Badge | `rounded-md` | `rounded-lg`, `rounded-full` |
| Icon container (medium) | `rounded-xl` | `rounded-full` |
| Icon container (small) | `rounded-lg` | `rounded-full` |
| Status dot / pill | `rounded-full` | anything else |

### Shadows
| Surface | Correct | Anti-pattern |
|---|---|---|
| Default card | `shadow-[0_1px_3px_0_rgba(0,0,0,0.08),0_1px_2px_-1px_rgba(0,0,0,0.06)]` | `shadow-sm` |
| Hovering card | `hover:shadow-[0_10px_25px_-5px_rgba(0,51,141,0.12),0_4px_10px_-5px_rgba(0,51,141,0.08)]` | `hover:shadow-lg` |
| Metric card hover | `hover:shadow-[0_4px_12px_rgba(0,51,141,0.1)]` | `hover:shadow-md` |
| Button | `shadow-sm hover:shadow-md` | custom navy shadows |

### Colours
| Use | Avoid |
|---|---|
| `bg-[#00338D]` / `bg-navy` | `bg-blue-900`, `bg-indigo-800` |
| `bg-[#0077C8]` / `bg-accent` | `bg-blue-500`, `bg-blue-600` |
| `bg-[#00A36C]` / `bg-success` | `bg-green-500`, `bg-emerald-500` |
| `bg-[#D4A017]` / `bg-amber` | `bg-yellow-500`, `bg-amber-500` |
| `bg-[#DC2626]` / `bg-danger` | `bg-red-600`, `bg-rose-600` |
| `bg-[#F4F6F9]` / `bg-grey-bg` | `bg-gray-100`, `bg-slate-100` |
| `border-[#E2E8F0]` | `border-gray-200`, `border-slate-200` |
| Dark: `#1A1F36` / `#0D1428` | `bg-gray-900`, `bg-slate-900`, `bg-zinc-900` |

### Padding (card hierarchy)
| Card type | Padding |
|---|---|
| Full content card | `p-6` |
| Metric card | `p-5` |
| KPI / compact card | `p-4` |
| Compact row (table row, list item) | `px-4 py-3` |
| Section header bar | `px-6 py-4` |

### Typography
| Correct | Avoid |
|---|---|
| Metric values: `font-mono font-bold text-2xl` | `font-semibold` without `font-mono` |
| Section labels: `text-[10px] font-bold uppercase tracking-widest` | `text-xs uppercase` without `tracking-widest` |
| Inline `fontFamily` only on metric value elements | Inline font-family anywhere else |
| `font-heading`, `font-body`, `font-mono` tokens | `font-sans`, raw font names in class strings |

### Dark surfaces
| Rule |
|---|
| Sidebar background: `#0D1428` only |
| Header/navbar background: `#1A1F36` at `/95` opacity + `backdrop-blur` |
| Dark cards: `#1A1F36` only |
| Dark borders: `border-white/10` (not `border-gray-700`) |
| Dark secondary text: `text-white/40` or `text-white/60` (not `text-gray-400`) |

---

## 8. Recommended File Structure

For any new project built on this design system:

```
/public
  logo.png                  ← project logo
  kpmg-logo.png             ← KPMG logo (if co-branded)

/app
  globals.css               ← base styles, animations, scrollbar, .glass, .bg-navy-gradient
  layout.jsx                ← Google Fonts <head> link, font-body on body

/components
  /shared
    Card.jsx                ← Card, DarkCard, MetricCard, KPICard
    Button.jsx              ← Button (all variants + sizes)
    Badge.jsx               ← Badge, StatusBadge
    LoadingDots.jsx         ← typing dots animation
  /layout
    AppShell.jsx            ← sidebar + header wrapper
    Navbar.jsx              ← top nav (public/marketing pages)

tailwind.config.js          ← colour tokens + font family tokens
```

---

## 9. Starter globals.css

```css
@tailwind base;
@tailwind components;
@tailwind utilities;

*, *::before, *::after { box-sizing: border-box; }
html { scroll-behavior: smooth; }

body {
  margin: 0; padding: 0;
  font-family: 'DM Sans', sans-serif;
  color: #1A1F36;
  background-color: #F4F6F9;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
}

h1,h2,h3,h4,h5,h6 { font-family: 'Plus Jakarta Sans', sans-serif; }

.glass      { background: rgba(255,255,255,0.08); backdrop-filter: blur(16px); border: 1px solid rgba(255,255,255,0.12); }
.glass-dark { background: rgba(26,31,54,0.82);   backdrop-filter: blur(20px); border: 1px solid rgba(255,255,255,0.08); }

.bg-navy-gradient        { background: linear-gradient(135deg, #00338D 0%, #1A1F36 55%, #0D1428 100%); }
.bg-navy-gradient-subtle { background: linear-gradient(180deg, #1A1F36 0%, #0D1428 100%); }

.bg-grid-pattern {
  background-image:
    linear-gradient(rgba(0,119,200,0.05) 1px, transparent 1px),
    linear-gradient(90deg, rgba(0,119,200,0.05) 1px, transparent 1px);
  background-size: 48px 48px;
}

::-webkit-scrollbar        { width: 5px; height: 5px; }
::-webkit-scrollbar-track  { background: #F4F6F9; }
::-webkit-scrollbar-thumb  { background: #CBD5E1; border-radius: 3px; }
::-webkit-scrollbar-thumb:hover { background: #94A3B8; }

@keyframes pulse-dot {
  0%,80%,100% { transform: scale(0.6); opacity: 0.4; }
  40%         { transform: scale(1);   opacity: 1;   }
}
.typing-dot:nth-child(1) { animation: pulse-dot 1.4s infinite ease-in-out 0s;   }
.typing-dot:nth-child(2) { animation: pulse-dot 1.4s infinite ease-in-out 0.2s; }
.typing-dot:nth-child(3) { animation: pulse-dot 1.4s infinite ease-in-out 0.4s; }

@keyframes shimmer {
  0%   { background-position: -200% 0; }
  100% { background-position:  200% 0; }
}
.shimmer {
  background: linear-gradient(90deg, #f0f4f8 25%, #e2e8f0 50%, #f0f4f8 75%);
  background-size: 200% 100%;
  animation: shimmer 1.5s infinite;
}

/* AI / rich-text output */
.ai-output h2 { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 1.05rem; font-weight: 700; color: #00338D; margin-top: 1.25rem; margin-bottom: 0.5rem; border-bottom: 2px solid #E2E8F0; padding-bottom: 0.25rem; }
.ai-output h3 { font-family: 'Plus Jakarta Sans', sans-serif; font-size: 0.95rem; font-weight: 600; color: #0077C8; margin-top: 1rem; margin-bottom: 0.35rem; }
.ai-output p  { margin-bottom: 0.65rem; line-height: 1.7; font-size: 0.9rem; }
.ai-output ul { padding-left: 1.25rem; margin-bottom: 0.65rem; }
.ai-output li { margin-bottom: 0.2rem; font-size: 0.9rem; line-height: 1.6; }
.ai-output strong { color: #1A1F36; font-weight: 600; }
```

---

## 10. Starter tailwind.config.js

```js
/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './app/**/*.{js,jsx,ts,tsx}',
    './components/**/*.{js,jsx,ts,tsx}',
  ],
  theme: {
    extend: {
      colors: {
        navy:            '#00338D',
        'navy-deep':     '#1A1F36',
        'navy-darker':   '#0D1428',
        accent:          '#0077C8',
        'accent-light':  '#1A8FE3',
        success:         '#00A36C',
        amber:           '#D4A017',
        danger:          '#DC2626',
        'success-light': '#F0FDF4',
        'amber-light':   '#FFFBEB',
        'danger-light':  '#FEF2F2',
        'grey-bg':       '#F4F6F9',
        'grey-border':   '#E2E8F0',
        'text-primary':  '#1A1F36',
        'text-secondary':'#6B7280',
        'text-muted':    '#9CA3AF',
      },
      fontFamily: {
        heading: ["'Plus Jakarta Sans'", 'sans-serif'],
        body:    ["'DM Sans'",           'sans-serif'],
        mono:    ["'JetBrains Mono'",    'monospace'],
      },
    },
  },
  plugins: [],
};
```

---

## 11. Starter Component Files

Copy these verbatim into a new project. Remove `'use client'` if not using Next.js App Router.

### components/shared/Card.jsx
```jsx
'use client';

export function Card({ children, className = '', hover = false, onClick, padding = 'p-6' }) {
  const base = 'bg-white rounded-2xl border border-[#E2E8F0] transition-all duration-200';
  const shadow = hover
    ? 'hover:shadow-[0_10px_25px_-5px_rgba(0,51,141,0.12),0_4px_10px_-5px_rgba(0,51,141,0.08)] hover:-translate-y-0.5 cursor-pointer'
    : 'shadow-[0_1px_3px_0_rgba(0,0,0,0.08),0_1px_2px_-1px_rgba(0,0,0,0.06)]';
  return (
    <div className={`${base} ${shadow} ${padding} ${className}`} onClick={onClick}>
      {children}
    </div>
  );
}

export function DarkCard({ children, className = '', padding = 'p-6' }) {
  return (
    <div className={`bg-[#1A1F36] rounded-2xl border border-white/10 ${padding} ${className}`}>
      {children}
    </div>
  );
}

export function MetricCard({ label, value, unit, icon: Icon, color = '#0077C8', trend }) {
  return (
    <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 shadow-[0_1px_3px_0_rgba(0,0,0,0.08)] hover:shadow-[0_4px_12px_rgba(0,51,141,0.1)] transition-all duration-200">
      <div className="flex items-start justify-between mb-3">
        <div className="w-10 h-10 rounded-xl flex items-center justify-center" style={{ backgroundColor: color + '18' }}>
          {Icon && <Icon size={20} style={{ color }} />}
        </div>
        {trend !== undefined && (
          <span className={`text-xs font-semibold px-2 py-1 rounded-full ${trend >= 0 ? 'text-[#00A36C] bg-[#00A36C]/10' : 'text-[#EF4444] bg-[#EF4444]/10'}`}>
            {trend >= 0 ? '+' : ''}{trend}%
          </span>
        )}
      </div>
      <div className="font-mono font-bold text-2xl text-[#1A1F36]" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
        {value}
        {unit && <span className="text-sm font-normal text-[#6B7280] ml-1">{unit}</span>}
      </div>
      <div className="text-sm text-[#6B7280] mt-1 font-medium">{label}</div>
    </div>
  );
}

export function KPICard({ title, value, unit, statusColor = '#0077C8' }) {
  return (
    <div
      className="bg-white rounded-xl border border-[#E2E8F0] border-l-[3px] p-4 min-w-[160px] shadow-sm hover:shadow-md transition-all duration-200"
      style={{ borderLeftColor: statusColor }}
    >
      <div className="text-[10px] font-bold uppercase tracking-widest text-[#9CA3AF] mb-1">{title}</div>
      <div className="text-2xl font-semibold font-mono text-[#1A1F36]" style={{ fontFamily: "'JetBrains Mono', monospace" }}>
        {value}
      </div>
      {unit && <div className="text-xs text-[#9CA3AF] mt-0.5">{unit}</div>}
    </div>
  );
}
```

---

### components/shared/Button.jsx
```jsx
'use client';

const variants = {
  primary: 'bg-[#00338D] text-white hover:bg-[#0044b8] focus:ring-[#00338D] shadow-sm hover:shadow-md active:scale-[0.98]',
  accent:  'bg-[#0077C8] text-white hover:bg-[#0088e0] focus:ring-[#0077C8] shadow-sm hover:shadow-md active:scale-[0.98]',
  outline: 'bg-transparent text-[#00338D] border-2 border-[#00338D] hover:bg-[#00338D] hover:text-white focus:ring-[#00338D] active:scale-[0.98]',
  ghost:   'bg-transparent text-[#6B7280] hover:bg-[#F4F6F9] hover:text-[#1A1F36] focus:ring-[#CBD5E1] active:scale-[0.98]',
  danger:  'bg-[#EF4444] text-white hover:bg-[#DC2626] focus:ring-[#EF4444] shadow-sm active:scale-[0.98]',
  amber:   'bg-[#D4A017] text-white hover:bg-[#b8891a] focus:ring-[#D4A017] shadow-sm active:scale-[0.98]',
  white:   'bg-white text-[#00338D] hover:bg-[#F4F6F9] focus:ring-white shadow-sm active:scale-[0.98]',
};

const sizes = {
  sm: 'px-3 py-1.5 text-sm',
  md: 'px-5 py-2.5 text-sm',
  lg: 'px-7 py-3.5 text-base',
  xl: 'px-8 py-4 text-lg',
};

export function Button({ children, variant = 'primary', size = 'md', onClick, disabled, className = '', type = 'button', ...props }) {
  const base = 'inline-flex items-center justify-center gap-2 font-semibold rounded-lg transition-all duration-200 cursor-pointer border-0 outline-none focus:ring-2 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed';
  return (
    <button
      type={type}
      onClick={onClick}
      disabled={disabled}
      className={`${base} ${variants[variant]} ${sizes[size]} ${className}`}
      {...props}
    >
      {children}
    </button>
  );
}
```

---

### components/shared/Badge.jsx
```jsx
'use client';

const colors = {
  blue:  'bg-[#0077C8]/10 text-[#0077C8] border-[#0077C8]/20',
  navy:  'bg-[#00338D]/10 text-[#00338D] border-[#00338D]/20',
  green: 'bg-[#00A36C]/10 text-[#00A36C] border-[#00A36C]/20',
  amber: 'bg-[#D4A017]/10 text-[#D4A017] border-[#D4A017]/20',
  red:   'bg-red-50 text-red-600 border-red-200',
  grey:  'bg-[#F4F6F9] text-[#6B7280] border-[#E2E8F0]',
};

const sizes = {
  xs: 'px-1.5 py-0.5 text-xs',
  sm: 'px-2 py-1 text-xs',
  md: 'px-3 py-1.5 text-sm',
};

export function Badge({ children, color = 'blue', size = 'sm' }) {
  return (
    <span className={`inline-flex items-center font-semibold rounded-md border ${colors[color] ?? colors.blue} ${sizes[size]}`}>
      {children}
    </span>
  );
}

const dotColors = { green: '#00A36C', amber: '#D4A017', blue: '#0077C8', red: '#DC2626', grey: '#9CA3AF' };

export function StatusBadge({ label, status = 'blue' }) {
  return (
    <Badge color={status}>
      <span className="w-1.5 h-1.5 rounded-full mr-1.5 inline-block" style={{ backgroundColor: dotColors[status] ?? dotColors.blue }} />
      {label}
    </Badge>
  );
}
```

---

### components/shared/LoadingDots.jsx
```jsx
'use client';

export function LoadingDots({ color = '#0077C8', size = 8 }) {
  return (
    <div className="flex items-center gap-1.5">
      {[0, 1, 2].map(i => (
        <div key={i} className="typing-dot rounded-full" style={{ width: size, height: size, backgroundColor: color }} />
      ))}
    </div>
  );
}

export function PageLoader({ label = 'Loading...' }) {
  return (
    <div className="fixed inset-0 bg-[#1A1F36] flex items-center justify-center z-50">
      <div className="text-center">
        <div className="w-12 h-12 border-2 border-[#0077C8]/30 border-t-[#0077C8] rounded-full animate-spin mx-auto mb-4" />
        <p className="text-white/60 text-sm font-medium">{label}</p>
      </div>
    </div>
  );
}

export function AIThinkingLoader({ label = 'Generating analysis...' }) {
  return (
    <div className="flex items-center gap-3 p-4 bg-[#00338D]/5 rounded-xl border border-[#00338D]/10">
      <div className="w-8 h-8 rounded-lg bg-[#00338D] flex items-center justify-center flex-shrink-0">
        <span className="text-white text-xs font-bold">AI</span>
      </div>
      <div>
        <p className="text-xs text-[#6B7280] mb-1.5">{label}</p>
        <LoadingDots />
      </div>
    </div>
  );
}
```

---

## 12. Starter AppShell (Sidebar + Header)

Generic, project-agnostic. Replace `NAV_GROUPS` with your own nav items.

### components/layout/AppShell.jsx
```jsx
'use client';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { ChevronLeft, ChevronRight, Search } from 'lucide-react';

// ── Configure nav groups for your project ────────────────────────────────────
const NAV_GROUPS = [
  {
    label: 'Core',
    items: [
      // { id: 'dashboard', label: 'Dashboard', icon: LayoutDashboard, href: '/dashboard' },
    ],
  },
];
// ─────────────────────────────────────────────────────────────────────────────

function Sidebar({ collapsed, onToggle }) {
  const pathname = usePathname();
  return (
    <div className={`${collapsed ? 'w-16' : 'w-64'} flex-shrink-0 bg-[#0D1428] border-r border-white/[0.06] flex flex-col transition-all duration-300 overflow-hidden h-full`}>
      <div className="flex items-center justify-end px-2 py-3 border-b border-white/[0.06]">
        <button
          onClick={onToggle}
          className="w-7 h-7 rounded-lg bg-white/5 hover:bg-white/10 flex items-center justify-center text-white/50 hover:text-white transition-colors"
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      <div className="flex-1 overflow-y-auto py-3 space-y-4 px-2">
        {NAV_GROUPS.map(group => (
          <div key={group.label}>
            {!collapsed && (
              <p className="text-[9px] font-bold uppercase tracking-widest text-white/25 px-2 mb-1.5">{group.label}</p>
            )}
            <div className="space-y-0.5">
              {group.items.map(item => {
                const Icon = item.icon;
                const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
                return (
                  <Link
                    key={item.id}
                    href={item.href}
                    className={`flex items-center gap-3 px-2.5 py-2 rounded-lg transition-colors group ${
                      isActive
                        ? 'bg-[#00338D]/25 border border-[#00338D]/30 text-white'
                        : 'text-white/50 hover:text-white hover:bg-white/5 border border-transparent'
                    }`}
                  >
                    <Icon size={16} className={`flex-shrink-0 ${isActive ? 'text-[#0077C8]' : 'group-hover:text-white/80'}`} />
                    {!collapsed && <span className="text-xs font-semibold truncate">{item.label}</span>}
                  </Link>
                );
              })}
            </div>
          </div>
        ))}
      </div>

      <div className="border-t border-white/[0.06] px-2 py-3">
        <div className="flex items-center gap-2 px-2">
          <div className="relative flex-shrink-0">
            <span className="w-2 h-2 rounded-full bg-[#00A36C] block" />
            <span className="absolute inset-0 rounded-full bg-[#00A36C] animate-ping opacity-50" />
          </div>
          {!collapsed && <span className="text-[10px] text-white/40">All Systems Operational</span>}
        </div>
      </div>
    </div>
  );
}

function Header({ title, actions }) {
  return (
    <div
      className="h-14 flex-shrink-0 bg-[#1A1F36]/95 border-b border-white/[0.08] flex items-center gap-3 px-4"
      style={{ backdropFilter: 'blur(20px)' }}
    >
      <span className="font-bold text-sm text-white flex-shrink-0" style={{ fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
        [Product Name] {/* ← replace */}
      </span>
      <span className="text-white/30">|</span>
      <span className="text-white/70 text-sm">{title}</span>

      <div className="flex-1 max-w-xs mx-2">
        <div className="relative">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-white/30" />
          <input
            type="text"
            placeholder="Search..."
            className="w-full bg-white/5 border border-white/10 rounded-lg pl-8 pr-3 py-1.5 text-xs text-white placeholder:text-white/30 focus:outline-none focus:border-[#0077C8]/50 transition-colors"
          />
        </div>
      </div>

      <div className="flex-1" />
      {actions}
    </div>
  );
}

export default function AppShell({ title = '', children, headerActions }) {
  const [collapsed, setCollapsed] = useState(() =>
    typeof window !== 'undefined' ? localStorage.getItem('sidebar-collapsed') === 'true' : false
  );
  const toggle = () => {
    const next = !collapsed;
    setCollapsed(next);
    if (typeof window !== 'undefined') localStorage.setItem('sidebar-collapsed', String(next));
  };
  return (
    <div className="flex h-screen overflow-hidden bg-[#F4F6F9]">
      <Sidebar collapsed={collapsed} onToggle={toggle} />
      <div className="flex-1 flex flex-col overflow-hidden">
        <Header title={title} actions={headerActions} />
        <div className="flex-1 overflow-y-auto">{children}</div>
      </div>
    </div>
  );
}
```

---

## 13. Starter layout.jsx (Next.js App Router)

```jsx
import './globals.css';

export const metadata = {
  title:       '[Product Name]',
  description: '[Product description]',
  icons: { icon: '/favicon.svg' },
};

export default function RootLayout({ children }) {
  return (
    <html lang="en">
      <head>
        <link
          href="https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:ital,wght@0,400;0,500;0,600;0,700;0,800;1,400&family=DM+Sans:wght@300;400;500;600&family=JetBrains+Mono:wght@400;500;600&display=swap"
          rel="stylesheet"
        />
      </head>
      <body>{children}</body>
    </html>
  );
}
```

---

## 14. Required Dependencies

```json
{
  "dependencies": {
    "lucide-react":  "^1.14.0",
    "framer-motion": "^12.0.0",
    "recharts":      "^3.0.0"
  },
  "devDependencies": {
    "tailwindcss":  "^3.4.0",
    "postcss":      "^8.0.0",
    "autoprefixer": "^10.0.0"
  }
}
```

Install:
```bash
npm install lucide-react framer-motion recharts
npm install -D tailwindcss postcss autoprefixer
npx tailwindcss init -p
```
