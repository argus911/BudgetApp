# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A single-file static PWA for 中華電信 彰化營運處 budget management. There is no build step — `index.html` is the entire application and is served directly via GitHub Pages at `https://argus911.github.io/BudgetApp/`.

## Deployment

GitHub Pages serves from the `main` branch. After merging a feature branch, the site updates automatically.

## How to Update Budget Data

When a new monthly CSV export arrives from TAIS:

1. Replace the `RAW` array (starts at `var RAW = [` near the top of `<script>`) with the new data converted to JSON. Each row must include all 12 fields: `明細帳`, `會計項目`, `本月動支數`, `本月餘額`, `本月預算數`, `至本月預算數累計`, `累計動支率`, `本年度預算`, `年度動支率`, `剩餘可動支數`, `預算主管單位`, `費用分類`, `分類代碼`. Fields that are blank in the CSV become empty string `""`.
2. Update the four metadata strings in `id="tab-info"`: `資料年月`, `更新時間`, `總筆數`, `資料來源`.
3. Update the `<div class="header-sub">` subtitle (年月 display).

## Architecture

Everything lives in `index.html`. The structure is:

- **Lines 1–128**: `<head>` with all inline CSS + Chart.js CDN import
- **Lines 129–235**: HTML structure — header, two tab-bars (top sticky + bottom fixed), five `tab-content` divs, bottom sheet overlay
- **Lines 236–826**: Single `<script>` block containing all JS

### JavaScript layout (inside `<script>`)

| Variable / Function | Purpose |
|---|---|
| `RAW` | Inline JSON array of all budget rows (~346 items) |
| `CAT_COLORS` | Fixed color map for the 6 費用分類 categories |
| `UNIT_PALETTE` / `unitColorMap` | Colors for 預算主管單位, assigned dynamically on load |
| `curKw`, `curCat`, `curUnit`, `curPage` | Filter & pagination state |
| `filterData()` | Returns filtered subset of `RAW` based on state |
| `renderAll()` | Orchestrates stats + active-filters + cards + pager |
| `renderCards(rows)` | Renders paginated budget cards (20 per page) |
| `openSheet(acc)` | Populates and opens the bottom-sheet detail panel |
| `buildChips()` | Builds category and unit filter chip buttons |
| `switchTab(name)` | Shows/hides tab panels; lazily calls render functions |
| `renderSummary()` | Horizontal progress bars for category & unit overview |
| `renderCharts()` | Chart.js charts (donut, bar, stacked bar) |
| `destroyChart(id)` | Tears down a Chart.js instance before re-rendering |
| `renderWarn()` | Lists items where 年度動支率 ≥ 70% |
| `rateColor(r)` | Returns red (`#c62828`) ≥ 90%, orange (`#e07b00`) ≥ 70%, green (`#128048`) otherwise |

### Tabs

| Tab ID | Render trigger |
|---|---|
| `tab-search` | `renderAll()` on load + filter change |
| `tab-summary` | `renderSummary()` on first visit |
| `tab-charts` | `renderCharts()` on first visit (Chart.js) |
| `tab-warn` | `renderWarn()` on first visit |
| `tab-info` | Static HTML |

### Key data fields

`累計動支率` = cumulative utilisation rate for the month-to-date budget slice (NOT the same as 年度動支率 ÷ 本年度預算). `本月餘額` is the TAIS ledger balance, not `本月預算數 − 本月動支數`.

### Expense categories (費用分類)

Fixed ordered list used in `renderSummary` and `renderCharts`:
`人事費`, `業務外包`, `業務成本`, `專案建置成本`, `設備及折舊`, `管銷費用`

If a new category is introduced by TAIS, add it to `CAT_COLORS` and to the `CATS` array inside `renderCharts()`.

### Chart.js instance management

`_chartInstances` (object keyed by chart id) tracks live Chart.js instances. Always call `destroyChart(id)` before creating a new chart on the same canvas, or Chart.js will throw a "Canvas is already in use" error on repeated tab visits.
