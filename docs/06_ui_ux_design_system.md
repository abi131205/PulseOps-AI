# PulseOps AI - UI/UX Design System

This document outlines the visual identity, colors, typography, layout models, design tokens, and accessibility standards for the **PulseOps AI** Hospital Command Center dashboard.

---

## 🎨 1. Premium Color Palette

To represent operational urgency and decision support clearly, we use a sleek, high-contrast dark theme:

| Color Token | Hex Code | Purpose | Component |
| :--- | :--- | :--- | :--- |
| **`darkBg`** | `#0B0F19` | Main layout backdrop | Page container |
| **`cardBg`** | `#151C2C` | Layer panels & cards | Card wrappers |
| **`borderLight`**| `#222D44` | Panel divides & grids | Borders |
| **`accentBlue`** | `#2979FF` | Primary action indicator| Active tabs, info |
| **`accentGreen`**| `#00E676` | Healthy status metric | Normal ranges, OPS <60 |
| **`accentOrange`**| `#FF9100`| Warning alert metric | Medium alerts, OPS 60-79 |
| **`accentRed`**  | `#FF5252` | Critical action metric | Urgent alerts, OPS >=80 |
| **`textMuted`**  | `#94A3B8` | Subheadings & details  | Muted labels |

---

## ✍️ 2. Typography

* **Google Font:** **Outfit** (primary heading/body sans-serif), falling back to **Inter** and **sans-serif**.
  - Outfit is selected for its clean, geometric, and modern tech look, which makes statistical numbers highly readable.
* **Weights:**
  - `300 (Light)`: Auxiliary data labels.
  - `400 (Regular)`: General descriptions and lists.
  - `500 (Medium)`: Key actions, button texts, values.
  - `600 (Semibold)`: Panel headings and card metrics.
  - `700 (Bold)`: Logo headers and score readings.

---

## 📐 3. Grid & Spacing System

* **Base Grid Unit:** 4px (Tailwind standard spacing `space-y-1.5` / `p-4` / `gap-6`).
* **Sidebar Width:** Fixed 256px (`w-64`).
* **Main Container:** Grid layout with responsive column widths:
  - Small viewports: single column (`grid-cols-1`).
  - Tablet viewports: two-column layout.
  - Desktop viewports: three-column or four-column layouts.
* **Responsive Breakpoints:**
  - Sidebar: collapses or shifts off-canvas on mobile viewports.
  - Cards: stack vertically on mobile and align side-by-side on wide screens (`grid grid-cols-1 md:grid-cols-3 lg:grid-cols-4`).

---

## ♿ 4. Accessibility Standards (WCAG 2.1)

* **Contrast Ratios:** Foreground text against the slate and dark navy backgrounds maintains a contrast ratio exceeding **4.5:1** (AAA standard for text sizes).
* **Color Independence:** Alerts never rely solely on color. All warning indicators use a combination of color changes and explicit icon indicators (e.g., Lucide-react `AlertTriangle`, `CheckCircle2`, or numeric score labels).
* **Layout Scannability:** Key metrics (like the 92/100 Operational Priority Score) are sized at `text-3xl` (`font-extrabold`) to establish visual hierarchy.
