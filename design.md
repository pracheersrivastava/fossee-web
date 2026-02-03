# FOSSEE Scientific Analytics UI

**Design System v1.0**

**Purpose**
A unified visual and interaction system for scientific data analytics applications under FOSSEE. Optimized for **clarity, trust, academic credibility, and cross-platform consistency** (Web + Desktop).

---

## 1. Design Principles (Non-Negotiable)

1. **Data First**

   * UI must never compete with charts or tables.
   * Decorative elements are secondary to data legibility.

2. **Academic Neutrality**

   * No flashy gradients, neon colors, or marketing-style visuals.
   * Design must feel suitable for research labs and classrooms.

3. **Predictable Interactions**

   * One primary action per screen.
   * Progressive disclosure for advanced analytics.

4. **Cross-Platform Parity**

   * Visual hierarchy and spacing must match across React and PyQt5.
   * Desktop UI should not feel “ported” from web.

---

## 2. Color System

### 2.1 Core Brand Colors

| Role                  | Name          | Hex       | RGB             | Usage                         |
| --------------------- | ------------- | --------- | --------------- | ----------------------------- |
| Primary Text / Header | Deep Indigo   | `#1E2A38` | `30, 42, 56`    | Page titles, top bars         |
| Primary Action        | Academic Blue | `#2F80ED` | `47, 128, 237`  | Upload, Analyze, Generate PDF |
| Secondary Text        | Slate Gray    | `#6B7280` | `107, 114, 128` | Labels, metadata              |
| Background            | Off-White     | `#F8FAFC` | `248, 250, 252` | App background                |
| Surface               | Pure White    | `#FFFFFF` | `255, 255, 255` | Cards, tables                 |

---

### 2.2 Data Visualization Palette

| Metric         | Color        | Hex       | RGB            |
| -------------- | ------------ | --------- | -------------- |
| Flowrate       | Teal         | `#14B8A6` | `20, 184, 166` |
| Temperature    | Amber        | `#F59E0B` | `245, 158, 11` |
| Pressure       | Crimson      | `#EF4444` | `239, 68, 68`  |
| Equipment Type | Muted Violet | `#8B5CF6` | `139, 92, 246` |

**Rules**

* ❌ Never use more than **4 colors per chart**
* ❌ No gradients inside charts
* ✅ Use opacity (0.7–0.85) instead of new colors

---

### 2.3 Status Colors

| State   | Hex       | Usage                       |
| ------- | --------- | --------------------------- |
| Success | `#22C55E` | Upload complete, valid data |
| Warning | `#F59E0B` | Partial data issues         |
| Error   | `#DC2626` | Invalid CSV / API error     |
| Info    | `#3B82F6` | System messages             |

---

## 3. Typography System

### 3.1 Font Families

| Platform          | Font                            |
| ----------------- | ------------------------------- |
| Web (Primary)     | `Inter`                         |
| Desktop (Primary) | `Source Sans 3`                 |
| Fallback          | `Roboto`, `Arial`, `sans-serif` |

**Rules**

* ❌ No serif fonts in UI
* ❌ No custom or decorative fonts
* ✅ Font weights create hierarchy, not colors

---

### 3.2 Type Scale

| Token      | Size | Weight | Line Height | Usage           |
| ---------- | ---- | ------ | ----------- | --------------- |
| H1         | 24px | 600    | 32px        | Page title      |
| H2         | 18px | 500    | 26px        | Section headers |
| H3         | 16px | 500    | 24px        | Subsections     |
| Body       | 14px | 400    | 22px        | Paragraphs      |
| Table Text | 13px | 400    | 20px        | Tables          |
| Caption    | 12px | 400    | 18px        | Axis labels     |
| Meta       | 11px | 400    | 16px        | Timestamps      |

---

### 3.3 Typography Do’s & Don’ts

✅ DO

* Use sentence case for labels
* Use title case for page headers

❌ DON’T

* Use ALL CAPS
* Use font size below 11px
* Use bold for entire paragraphs

---

## 4. Spacing & Grid System

### 4.1 Base Unit

**Base Spacing Unit = 8px**

All margins and padding must be multiples of **8px**.

| Token | Value |
| ----- | ----- |
| xs    | 4px   |
| sm    | 8px   |
| md    | 16px  |
| lg    | 24px  |
| xl    | 32px  |
| xxl   | 48px  |

---

### 4.2 Layout Grid

#### Web

* Max width: **1200px**
* Columns: **12**
* Gutter: **24px**

#### Desktop

* Flexible layout
* Minimum content width: **960px**
* Sidebar width: **240px**

---

## 5. Component Specifications

### 5.1 Buttons

**Primary Button**

* Height: 40px
* Radius: 6px
* Background: `#2F80ED`
* Text: White
* Font: 14px / Medium

**Secondary Button**

* Background: Transparent
* Border: 1px solid `#2F80ED`
* Text: `#2F80ED`

❌ Never use icon-only buttons for primary actions.

---

### 5.2 CSV Upload Component

* Border: 2px dashed `#CBD5E1`
* Radius: 8px
* Background: `#F8FAFC`
* Hover: border → `#2F80ED`

**Post-Upload Behavior**

* Upload zone transforms into **Summary Card**
* Show:

  * File name
  * Row count
  * Validation status

---

### 5.3 Cards

* Background: White
* Radius: 8px
* Padding: 16px
* Shadow:
  `0px 2px 6px rgba(0,0,0,0.05)`

❌ No colored card backgrounds
❌ No heavy shadows

---

### 5.4 Tables

* Header background: `#F1F5F9`
* Row height: 44px
* Zebra striping: `#FAFAFA`
* Sticky headers: Enabled

❌ No vertical grid lines
✅ Hover highlight only

---

### 5.5 Charts

**Common Rules**

* No borders
* Gridlines: `#E5E7EB`
* Tooltip background: Dark Indigo @ 90%

**Web**

* Chart.js with responsive scaling

**Desktop**

* Matplotlib with consistent DPI
* Match color tokens exactly

---

## 6. Visual Hierarchy Rules

1. Page Title (H1)
2. Primary Action (Upload)
3. Summary KPIs
4. Charts (Top → Bottom)
5. Secondary Actions

❌ Never place charts above the upload section
❌ Never show advanced analytics by default

---

## 7. Motion & Feedback

### Allowed Animations

* Fade in (150–200ms)
* Progress bars
* Chart draw animation

### Forbidden

* Bounce
* Elastic easing
* Auto-playing motion

---

## 8. Accessibility Rules

* Minimum contrast: **4.5:1**
* Color never conveys meaning alone
* All icons must have text labels
* Keyboard navigation required (Web + Desktop)

---

## 9. Common Violations (Strictly Avoid)

❌ Gradient backgrounds
❌ Material-style shadows
❌ Over-colored dashboards
❌ Dashboard tiles with no data meaning
❌ Fancy loaders unrelated to data

---

## 10. Design Intent Summary

> This system must feel like **scientific instrumentation software**, not a startup dashboard.

If a choice is unclear:

* Prefer **clarity over beauty**
* Prefer **consistency over creativity**
* Prefer **academic tone over trendiness**

---

If you want, next I can:

* Convert this into **React component tokens**
* Create **PyQt5 style sheets (QSS)**
* Write **chart configuration templates**
* Add **PDF report layout specs**

Just tell me the next step.
