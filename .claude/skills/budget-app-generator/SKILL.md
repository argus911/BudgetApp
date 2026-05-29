---
name: budget-app-generator
description: |
  將中華電信彰化營運處的預算管理 TAIS/AS400 匯出資料（Excel 或 CSV 格式）轉換成
  可直接部署為 iOS PWA 的單檔 HTML 預算查詢 App，並自動推送至 GitHub Pages。

  使用時機（符合任一項即立即觸發）：
  - 使用者上傳預算管理 Excel 或 CSV 檔（欄位含 明細帳、會計項目、本月餘額、本月預算數 等）
  - 使用者同時上傳 TAIS_budget_*.csv + TAIS_report_budget_*.csv → 自動雙檔案模式
  - 使用者說「更新預算 App」、「產生預算查詢 App」、「上傳新的預算 Excel/CSV」、「產出 HTML」
  - 使用者說「skill new html」或「重新產生預算 HTML」
  - 使用者說「xcode」、「native app」、「ipa」、「App Store」或「企業簽署部署」→ 同步產生 Xcode ZIP
  - 只要看到 TAIS_budget 相關附件，就應主動觸發此 skill

  輸出：
  1. 單一 HTML 檔案（PWA，可加入 iPhone 主畫面）
  2. 自動推送 index.html 至 GitHub Pages（https://argus911.github.io/BudgetApp/）
  3. （選用）Xcode 原生 iOS 專案 zip（BudgetApp_Xcode_115_04.zip）
     SwiftUI App + WKWebView 包裝，含 AppIcon，Xcode 15+ 開啟設定 Team 即可建置

  觸發補充：
  - 使用者說「更新視覺化圖表」、「加圖表分析」、「新增 Charts Tab」→ 套用 v8 圖表分頁方案
  - 使用者說「以附檔替代」並上傳現有 HTML → 以該檔案為基底，加入圖表分析後推送
---

# 預算管理 App 產生器 v8

## 概述

讀取使用者上傳的預算管理 **CSV（TAIS/AS400 帳務匯出）** 或 **Excel（彰化營運處標準格式）**，
將所有資料嵌入一份自給自足的 HTML 檔案，並**自動推送至 GitHub Pages**。

> ⚠️ **重要修正（v5）**：`本月餘額` = TAIS 累計帳務餘額（CSV 的「本月餘額」欄位 / Excel 的「累計動支數」欄位），
> **絕非** 本月預算數－本月動支數。

> ✅ **v6 新增功能**：
> - 雙檔案模式：同時接受 `TAIS_budget_*.csv`（主預算）+ `TAIS_report_budget_*.csv`（科室對照）
> - 預算主管單位 = 真實科室別（行銷科、供應科、企業客戶科…），來自 TAIS_report CSV
> - 無對應科室的明細帳 `預算主管單位` 設為空字串，**絕不用費用分類名稱 fallback**
> - App 新增「預算主管單位」篩選 Chips（獨立於費用分類，只顯示真實科室）
> - 費用摘要 Tab 新增「各科室動支率」橫條圖
> - 高用率預警卡片顯示科室標籤


> ✅ **v8 新增功能（2026-05-01）**：
> - **「📈 圖表」第五分頁**：從現有 HTML 附檔修改，不從 CSV 重新產生，保留原始資料
> - 圖表 1：**KPI 卡片**（本年度預算 / 累計動支 / 整體動支率，三格警示色）
> - 圖表 2：**甜甜圈圖**（費用分類預算分配比例，Chart.js 4.4.1 CDN）
> - 圖表 3：**費用分類橫條圖**（年度動支率，紅≥90%/橙≥70%/綠警示色）
> - 圖表 4：**科室橫條圖**（各科室動支率由高到低，同色系警示）
> - 圖表 5：**堆疊橫條圖**（費用分類「已動支」vs「剩餘可動支」萬元對比）
> - Chart.js 以動態 CDN 方式載入（首次切換圖表 Tab 時載入，之後不重複繪製）
> - 推送 commit message 格式：`feat: 新增「圖表分析」分頁（...）v7-chart`

> ✅ **v9 圖表跑版修正（2026-05-29）**：
> - **甜甜圈圖渲染問題根本修正**：Chart.js `maintainAspectRatio: false` 時，canvas 必須有父容器的明確高度才能正確渲染
> - **解決方案**：`chart-canvas-wrap` wrapper div 設定 `position:relative` + `height` + canvas 設 `width/height:100%`，取代直接在 canvas 設 `height` 屬性
> - **CSS 規則**：`.chart-canvas-wrap{position:relative;width:100%}` `.chart-canvas-wrap canvas{width:100%!important;height:100%!important;display:block}`
> - **HTML 結構**（所有圖表統一）：`<div class="chart-canvas-wrap" style="height:280px"><canvas id="chartDonut"></canvas></div>`
> - **科室圖動態高度**：`document.getElementById('unitChartWrap').style.height = unitH+'px'`（每科室 28px，最小 260px）
> - **不再用** `<canvas height="220">` 屬性，改用容器 `style="height:220px"` 控制

> ✅ **v7 除錯修正（2026-04-22）**：
> - **字型**：`ipag.ttf` 在此容器**不存在**；正確字型為 `DroidSansFallbackFull.ttf`（CJK）+ `IBMPlexMono-Bold.ttf`（數字）複合渲染
> - **iOS 圖示**：`apple-touch-icon` 只讀取 HTML 內 base64，`icon.png` 對 iOS 無效；每次更新 icon 必須重新嵌入 HTML
> - **JS 語法陷阱**：style 字串拼接中的 ternary expression 後若緊接 `;` 會造成全頁 SyntaxError，詳見 Step 3C-3
> - **CSV 欄位**：115年4月起 TAIS_budget 欄位名稱有更動，詳見 Step 1B 對照表
> - **推送規則**：日常 CSV 更新只推 `index.html`（icon 已內嵌），`icon.png` 不再變動

---

## GitHub 推送設定

```
GITHUB_TOKEN=<stored_in_env_or_config>
GITHUB_REPO=argus911/BudgetApp
GITHUB_BRANCH=main
GITHUB_PAGES_URL=https://argus911.github.io/BudgetApp/
```

---

## 執行步驟

### Step 0：安裝相依套件

```bash
pip install openpyxl Pillow --break-system-packages -q
```

---

### Step 1：解析來源檔案

#### 1A：雙 CSV 模式（v6 標準流程）

同時上傳兩份 TAIS 匯出 CSV：

| 檔案 | 命名特徵 | 用途 |
|---|---|---|
| `TAIS_budget_*.csv` | 含 明細帳/本月差異/本月餘額/分類代碼 | 主預算數據 |
| `TAIS_report_budget_*.csv` | 含 科目代號/預算主管單位 | 科室對照表 |

**TAIS_report_budget 欄位**（115年4月確認）：
`科目代號, 科目名稱, 累計動支數, 至本月預算數, 累計動支率%, 年度預算數, 年度動支率%, 剩餘可動支, 預算主管單位`

```python
import csv, json

# ── 讀取科室對照表 ──────────────────────────────────────────
# 排除 '9999'（系統預設值）與空白
unit_map = {}
with open('TAIS_report_budget路徑', encoding='utf-8-sig') as f:
    for row in csv.DictReader(f):
        acc  = str(row.get('科目代號','')).strip()
        unit = str(row.get('預算主管單位','')).strip()
        if acc and unit and unit not in ('', '9999'):
            unit_map[acc] = unit

# ── 讀取主預算 CSV ─────────────────────────────────────────
with open('TAIS_budget路徑', encoding='utf-8-sig') as f:
    csv_rows = list(csv.DictReader(f))

cat_labels = {'A':'人事費','B':'業務外包','C':'業務成本','D':'專案建置成本','E':'設備及折舊','F':'管銷費用'}

def fnum(v):
    try:
        f = float(str(v).strip())
        return int(f) if f == int(f) else round(f,4)
    except: return str(v).strip() if v else ''

data = []
for row in csv_rows:
    subacc  = str(row.get('明細帳','')).strip()
    fen_lei = str(row.get('分類代碼','')).strip()
    cat_key = fen_lei[0] if fen_lei else ''
    cat_name = cat_labels.get(cat_key, '其他')
    # ★★★ 嚴格規則：只從 unit_map 取真實科室，無對應一律空字串
    # ★★★ 絕對禁止用費用分類名稱作為 fallback（會污染科室篩選）
    unit = unit_map.get(subacc, '')
    data.append({
        '明細帳':           subacc,
        '會計項目':         str(row.get('會計項目','')).strip(),
        '本月動支數':       fnum(row.get('本月差異','')),    # 本月差異 = 淨月度支出
        '本月餘額':         fnum(row.get('本月餘額','')),    # ★直接取CSV欄位，勿計算★
        '本月預算數':       fnum(row.get('本月預算數','')),
        '至本月預算數累計': fnum(row.get('至本月預算數累計','')),
        '累計動支率':       fnum(row.get('累計動支率%','')),
        '本年度預算':       fnum(row.get('本年度預算','')),
        '年度動支率':       fnum(row.get('年度動支率%','')),
        '剩餘可動支數':     fnum(row.get('剩餘可動支','')),
        '預算主管單位':     unit,      # '' = 無對應，不顯示科室徽章，不進篩選 chips
        '費用分類':         cat_name,
        '分類代碼':         fen_lei,
    })

meta_year  = str(csv_rows[0].get('年度','—') if csv_rows else '—')
meta_month = str(csv_rows[0].get('月','—') if csv_rows else '—')
json_data  = json.dumps(data, ensure_ascii=False, separators=(',',':'))
```

> ⚠️ **驗證步驟（必做）**：產生 JSON 後確認科室清單不含費用分類名稱
> ```python
> CAT_NAMES = {'人事費','業務外包','業務成本','專案建置成本','設備及折舊','管銷費用','其他'}
> units = set(d['預算主管單位'] for d in data if d['預算主管單位'])
> bad = units & CAT_NAMES
> assert not bad, f'科室污染：{bad}'  # 若有值則代表 fallback 未清除
> ```

#### 1B：單 CSV 模式（僅上傳 TAIS_budget，無 TAIS_report）

`預算主管單位` 全部設為空字串，App 不顯示科室篩選 Chips（或顯示「無科室資料」說明）。

最新 TAIS_budget 匯出欄位（115年4月實際確認）：
列帳機構, 交易機構, 年度, **月份**, 總帳科目, **明細帳**, **科目名稱**, 去年同期, 上月累計,
DAMTTM, CAMTTM, **本月動支增減**, **累計動支數**, **本月預算數**, **至本月預算數**,
**累計動支率%**, **年度預算數**, **年度動支率%**, **剩餘可動支**, 類別, **項目代號**, **預算主管單位**

> ⚠️ **115年4月欄位對照（舊→新）**：
> - `月` → `月份`
> - `會計項目` → `科目名稱`
> - `本月差異` → `本月動支增減`
> - `本月餘額` → `累計動支數`（★TAIS 累計帳務餘額★）
> - `至本月預算數累計` → `至本月預算數`
> - `本年度預算` → `年度預算數`
> - `分類代碼` → `項目代號`
> - ★ CSV 已內含 `預算主管單位` 欄位，無須另外讀取 TAIS_report CSV
> - `預算主管單位` 值為 `9999` 時視同空字串

```python
# 115年4月 單 CSV 模式讀取範例（欄位已更名）
with open('TAIS_budget路徑', encoding='utf-8-sig') as f:
    csv_rows = list(csv.DictReader(f))

meta_year  = str(csv_rows[0].get('年度', '115')).strip()
meta_month = str(csv_rows[0].get('月份', '4')).strip()   # ★ 舊版是「月」

for row in csv_rows:
    raw_unit = str(row.get('預算主管單位', '')).strip()
    unit = raw_unit if raw_unit and raw_unit != '9999' else ''
    data.append({
        '明細帳':           str(row.get('明細帳', '')).strip(),
        '會計項目':         str(row.get('科目名稱', '')).strip(),      # ★ 舊：會計項目
        '本月動支數':       fnum(row.get('本月動支增減', '')),          # ★ 舊：本月差異
        '本月餘額':         fnum(row.get('累計動支數', '')),            # ★ 舊：本月餘額
        '本月預算數':       fnum(row.get('本月預算數', '')),
        '至本月預算數累計': fnum(row.get('至本月預算數', '')),           # ★ 舊：至本月預算數累計
        '累計動支率':       fnum(row.get('累計動支率%', '')),
        '本年度預算':       fnum(row.get('年度預算數', '')),             # ★ 舊：本年度預算
        '年度動支率':       fnum(row.get('年度動支率%', '')),
        '剩餘可動支數':     fnum(row.get('剩餘可動支', '')),
        '預算主管單位':     unit,
        '費用分類':         cat_labels.get(str(row.get('項目代號','')).strip()[:1], '其他'),  # ★ 舊：分類代碼
        '分類代碼':         str(row.get('項目代號', '')).strip(),        # ★ 舊：分類代碼
    })
```

---

### Step 2：產生 iOS App Icon

> ✅ **v7 已驗證字型方案**（複合字型）：
> - **繁體中文**：`/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf` ← 容器確認存在
> - **ASCII 數字**：`/sessions/*/mnt/.claude/skills/canvas-design/canvas-fonts/IBMPlexMono-Bold.ttf`
> - ❌ `ipag.ttf`（`/usr/share/fonts/opentype/ipafont-gothic/`）在此容器**不存在**，勿使用
> - ❌ `DroidSansFallbackFull.ttf` 不含 ASCII 字型，數字須另用 IBMPlexMono 渲染

```python
from PIL import Image, ImageDraw, ImageFont
import base64, os, glob

FONT_CJK = '/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf'
# IBMPlexMono：動態找路徑（session ID 每次不同）
_skill_base = glob.glob('/sessions/*/mnt/.claude/skills/canvas-design/canvas-fonts/IBMPlexMono-Bold.ttf')
FONT_NUM = _skill_base[0] if _skill_base else FONT_CJK  # fallback 到 CJK（數字會顯示為方塊）

os.makedirs('/tmp/icons', exist_ok=True)

def generate_icon(year_str='115', out_path='/tmp/icons/icon.png', SZ=512):
    img  = Image.new('RGBA', (SZ, SZ), (0,0,0,0))
    draw = ImageDraw.Draw(img)
    # 背景漸層（深綠 → 翠綠）
    for y in range(SZ):
        t = y / SZ
        draw.line([(0,y),(SZ,y)], fill=(int(12+t*(8-12)), int(105+t*(150-105)), int(68+t*(48-68)), 255))
    # 白色圓角矩形面板
    pw, ph, px, py = 400, 300, 56, 101
    draw.rounded_rectangle([px, py, px+pw, py+ph], radius=32, fill=(255,255,255,245))
    # 頂部綠色標題列
    bar_h = 62
    draw.rounded_rectangle([px, py, px+pw, py+bar_h], radius=32, fill=(18,128,72,255))
    draw.rectangle([px, py+32, px+pw, py+bar_h], fill=(18,128,72,255))
    # 字型（中文 CJK，數字 IBMPlexMono）
    f_title   = ImageFont.truetype(FONT_CJK, 34)
    f_main    = ImageFont.truetype(FONT_CJK, 112)
    f_sub_cn  = ImageFont.truetype(FONT_CJK, 32)   # 「年度」用中文字型
    f_sub_num = ImageFont.truetype(FONT_NUM, 32)   # 年份數字用 IBMPlexMono
    cx = SZ // 2
    DARK  = (15, 78, 42, 255)
    WHITE = (255, 255, 255, 235)
    draw.text((cx, py+30), '彰化營運處', font=f_title, fill=WHITE, anchor='mm')
    draw.text((cx, py+bar_h+88), '預算', font=f_main, fill=DARK, anchor='mm')
    draw.line([(px+50, py+bar_h+138),(px+pw-50, py+bar_h+138)], fill=(18,128,72,180), width=3)
    draw.text((cx, py+bar_h+210), '管理', font=f_main, fill=DARK, anchor='mm')
    # ★ 年份與「年度」分開渲染（數字 + 中文複合）
    num_w = f_sub_num.getbbox(year_str)[2] - f_sub_num.getbbox(year_str)[0]
    cn_w  = f_sub_cn.getbbox('年度')[2]   - f_sub_cn.getbbox('年度')[0]
    start_x = cx - (num_w + cn_w + 4) // 2
    sub_y   = py + ph + 34
    draw.text((start_x, sub_y),              year_str, font=f_sub_num, fill=WHITE, anchor='lm')
    draw.text((start_x + num_w + 4, sub_y), '年度',   font=f_sub_cn,  fill=WHITE, anchor='lm')
    img.save(out_path, 'PNG')
    return out_path

icon_path = generate_icon(year_str=meta_year)
with open(icon_path, 'rb') as f:
    icon_b64 = base64.b64encode(f.read()).decode()
icon_data_uri = f'data:image/png;base64,{icon_b64}'
```

---

### Step 3：HTML 關鍵設計（卡片式 UI + JS 安全規則）

> ✅ **UI 風格**：卡片式（Card-based）直覺易讀設計，對應 iOS Safari PWA 使用體驗。
> ⚠️ **JS 安全規則**：絕對禁止在 innerHTML 字串插值中使用 inline onclick（引號逸出 → SyntaxError）。
> ✅ 動態 UI 一律用 `element.dataset.xxx` + `addEventListener('click', ...)` 模式。

#### 3A：整體佈局結構

```
Header（sticky，深綠漸層）
  └─ 💰 預算管理 | 中華電信 彰化營運處 | [N筆] badge

Top Tab Bar（sticky，5個分頁）
  └─ 預算查詢 / 費用摘要 / 高用率預警 / 資料資訊 / 📈 圖表

【預算查詢 Tab】
  ├─ 篩選卡片（filter-card）
  │   ├─ 關鍵字搜尋框（明細帳 / 會計項目）
  │   ├─ 費用分類 Chips（全部/人事費/業務外包/業務成本/專案建置成本/設備及折舊/管銷費用）
  │   └─ 預算主管單位 Chips（全部 + 動態科室，★僅從 TAIS_report 真實科室，空值不列入）
  ├─ 已套用篩選條件 Pills（綠/藍/橘色，三條件同時可見）
  ├─ 黃色 notice 警示條（本月餘額說明）
  ├─ 2×2 統計卡片（本月餘額累計／本月預算數／本年度預算／剩餘可動支數）
  ├─ 結果數（共 N 筆）
  ├─ 明細卡片列表（每頁20筆，點擊展開底部 Sheet）
  └─ 分頁按鈕

【費用摘要 Tab】
  ├─ 整體預算概況卡片
  ├─ 各費用分類動支率橫條圖（含累計餘額/年度預算金額）
  └─ 各科室動支率橫條圖（★v6新增，各科室顏色獨立）

【高用率預警 Tab】
  └─ 年度動支率 ≥ 70% 清單（含科室標籤，橘/紅色邊框）

【圖表分析 Tab】（★v8 新增）
  ├─ 📌 KPI 卡片（本年度預算、累計動支、整體動支率）
  ├─ 🍩 甜甜圈圖（費用分類年度預算分配）
  ├─ 📊 費用分類橫條圖（年度動支率，紅/橙/綠警示）
  ├─ 🏢 科室橫條圖（年度動支率由高到低）
  └─ 📦 堆疊橫條圖（已動支 vs 剩餘可動支，萬元）

Bottom Tab Bar（fixed，同 Top Tab，iOS 慣用雙導覽）
```

#### 3B：明細卡片設計

每筆明細顯示為獨立圓角卡片（border-radius: 16px），包含：

```
┌─────────────────────────────────────────┐
│ [A201]  市話接續費－市話  [業務成本]     │  ← 代碼 + 名稱 + 費用分類 badge
│                           [服務中心]     │  ← 科室 badge（★有值才顯示，無值不顯示）
├─────────────────────────────────────────┤
│ 本月餘額（累計）  │  累計動支率          │
│   59,357（藍）   │   30.6%（綠）        │
├─────────────────────────────────────────┤
│ 本年度預算        │  剩餘可動支數        │
│   590,000        │  530,643（綠）       │
├─────────────────────────────────────────┤
│ 年度動支率  10.06%  ████░░░░░░░░       │  ← 進度條
└─────────────────────────────────────────┘
```

顏色規則：
- 本月餘額 → 藍色 `#1565c0`
- 剩餘可動支數 → 綠色（負數變紅）
- 動支率 < 70% → 綠色 `#128048`，≥ 70% → 橘色 `#e07b00`，≥ 90% → 紅色 `#c62828`
- 費用分類 badge → 各分類固定配色（CAT_COLORS）
- 科室 badge → 各科室固定配色（UNIT_PALETTE，半透明背景）
- **科室 badge 為空字串時完全不 render**（不顯示任何 badge）

#### 3C：JS 安全規則

```js
// ❌ 錯誤寫法（引號逸出 → SyntaxError）
el.innerHTML += '<div onclick="fn(\''+key+'\')">...</div>';

// ✅ 正確寫法（data-* + addEventListener）
var div = document.createElement('div');
div.dataset.acc = row['明細帳'];
div.addEventListener('click', function() {
    openSheet(this.dataset.acc);
});
el.appendChild(div);

// ✅ innerHTML 字串插值內只能做純展示，互動邏輯用 querySelectorAll 補綁
wrap.innerHTML = html;
wrap.querySelectorAll('[data-acc]').forEach(function(el) {
    el.addEventListener('click', function() { openSheet(this.dataset.acc); });
});
```

#### 3C-3：JS innerHTML style 字串拼接陷阱（★v7 新增）

> ⚠️ **此錯誤會導致整個 `<script>` 區塊靜默失敗（SyntaxError），頁面結構正常但資料完全空白**

```js
// ❌ 錯誤：ternary 後的分號「;」提前終止 JS 語句，後面的 font-weight:700 是非法 token
'<span style="color:'+(yr>=90?'#c62828':'#e07b00');font-weight:700">'+val+'</span>'
//                                                ↑ 這個分號是 JS 語句終止符，不是 CSS 分隔符

// ✅ 正確：分號必須加入字串拼接的引號內
'<span style="color:'+(yr>=90?'#c62828':'#e07b00')+';font-weight:700">'+val+'</span>'
//                                                 ↑ 正確：';font-weight:700' 是獨立字串片段

// ✅ 更安全的寫法：先計算顏色，再組裝 style
var color = yr>=90 ? '#c62828' : yr>=70 ? '#e07b00' : '#128048';
'<span style="color:'+color+';font-weight:700">'+val+'</span>'
```

> 🔍 **症狀識別**：頁面載入後篩選 chips、統計卡片、資料列全部空白，header badge 顯示初始值（如「— 筆」）。

#### 3C-2：科室 Chips 建立規則（★v6 關鍵）

```js
// ★★★ 嚴格過濾：只有 預算主管單位 非空字串才列入 unitSet
// ★★★ 不做任何額外排除邏輯，因為資料源頭已保證不含費用分類名稱
var unitSet = {};
RAW.forEach(function(r) {
    if (r['預算主管單位']) unitSet[r['預算主管單位']] = true;
});
var UNITS = ['all'].concat(Object.keys(unitSet).sort());

// 科室 badge 渲染：只在有值時才 render
var unitBadgeHtml = r['預算主管單位']
    ? '<span class="unit-badge" style="background:' + uc + '1a;color:' + uc + '">' + r['預算主管單位'] + '</span>'
    : '';  // 空字串 → 不顯示任何 badge
```

#### 3D：底部 Sheet 彈窗（詳情）

點擊卡片後從底部滑出，分「本月數據」/ 「年度數據」/ 「年度動支進度」三區塊：

```js
function openSheet(acc) {
    const r = RAW.find(x => x['明細帳'] === acc);
    // 填入 sheet-body 後設定 overlay.className = 'overlay open'
}
document.getElementById('overlay').addEventListener('click', function(e) {
    if (e.target === this) this.className = 'overlay';  // 點背景關閉
});
```

#### 3E：PWA / apple-touch-icon

> ★★★ **iOS 圖示關鍵規則（v7 修正）** ★★★
> - iOS「加入主畫面」只讀取 HTML `<link rel="apple-touch-icon">` 標籤的 **href 內容**
> - GitHub 上的 `icon.png` 檔案對 iOS PWA **完全無效**
> - 圖示**必須以 base64 data URI 直接內嵌**在 `index.html` 的 `<link>` 標籤中
> - 更新圖示後，必須重新產生 icon base64 並**重新產生整份 index.html**（不能只推 icon.png）
> - 舊圖示存在主畫面時，需先刪除再重新加入，才能顯示新圖示

```html
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
<meta name="apple-mobile-web-app-title" content="預算管理">
<link rel="apple-touch-icon" href="{icon_data_uri}">  <!-- ← base64 內嵌，非外部URL -->
<link rel="icon" type="image/png" href="{icon_data_uri}">
```

#### 3F：黃色 notice 警示條（必要元素）

```html
<div class="notice">
  ⚠️ <strong>本月餘額（累計）</strong>為 TAIS 帳務系統之<strong>累計帳務餘額</strong>，非本月預算減本月動支。
</div>
```

#### 3G：HTML 輸出

```python
import os, shutil

os.makedirs('/tmp/budget_out', exist_ok=True)
with open('/tmp/budget_out/index.html', 'w', encoding='utf-8') as f:
    f.write(html_final)

# 版本備份（ASCII 檔名，避免 macOS FUSE 掛載中文問題）
# v6 起版本號從對話最新版本 +1
ver_file = f'/tmp/budget_out/BudgetApp_{meta_year}_{int(meta_month):02d}_v8.html'
shutil.copy('/tmp/budget_out/index.html', ver_file)
```

#### 3H：圖表分析分頁實作（★v8 新增）

> **使用時機**：使用者說「加圖表」、「更新視覺化圖表」、「加圖表分析分頁」，
> 或上傳現有 HTML 附檔並要求加入圖表功能。
> **工作流程**：以上傳的 HTML 附檔為基礎，用 Python 字串替換插入，不重新產生整份 HTML。

```python
# Step A：讀取附檔
with open('/mnt/user-data/uploads/上傳檔案.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Step B：找到現有 tab 名稱（可能是 query/summary/warning/info 或 search/summary/alert/info）
# 查找：grep -n 'data-tab' 確認現有 tab ID 命名

# Step C：在 top tab bar 加入圖表按鈕（找 ℹ️ 資訊 那個按鈕後面插入）
html = html.replace(
    '<button ... data-tab="info">ℹ️ 資訊</button>
</div>

<div class="tab-content',
    '<button ... data-tab="info">ℹ️ 資訊</button>
  <button class="tab-btn" data-tab="charts">📈 圖表</button>
</div>

<div class="tab-content',
    1  # 只替換第一個（top bar）
)

# Step D：在 bottom nav 也加入圖表按鈕（找 <!-- Bottom Sheet --> 前的那組）
# Step E：在 <!-- Bottom Sheet --> 前插入 tab-charts div
CHARTS_TAB = """
<div class="tab-content" id="tab-charts">
  <div id="chartsRoot"></div>
</div>
"""

# Step F：在 switchTab() 加入 renderCharts 呼叫
html = html.replace(
    "if(tabName === 'summary') renderSummary();",
    "if(tabName === 'summary') renderSummary();
  if(tabName === 'charts') renderCharts();"
)

# Step G：在 </script> 前注入 renderCharts() 函式（見下方範本）
```

**renderCharts() 函式關鍵架構**：

```js
var _chartsReady = false;

function renderCharts(){
  if(_chartsReady) return;  // 避免重複繪製
  _chartsReady = true;
  var root = document.getElementById('chartsRoot');

  // 1. 先渲染 KPI 卡片（不需 Chart.js）
  // 2. 動態載入 Chart.js CDN
  if(typeof Chart === 'undefined'){
    var s = document.createElement('script');
    s.src = 'https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.1/chart.umd.min.js';
    s.onload = function(){ drawAll(); };
    document.head.appendChild(s);
  } else {
    drawAll();
  }

  function drawAll(){
    // 圖表 1：甜甜圈（費用分類預算分配）
    // 圖表 2：費用分類橫條（動支率，警示色）
    // 圖表 3：科室橫條（動支率，由高到低）
    // 圖表 4：堆疊橫條（已動支 vs 剩餘）
  }
}
```

**注意事項**：
- **⚠️ 重要（v9修正）**：`maintainAspectRatio: false` 必須搭配 **父容器明確高度** 才能生效
- ❌ 錯誤寫法：`<canvas id="chartDonut" height="220">` + `maintainAspectRatio: false`（父容器無高度，canvas 高度為 0）
- ✅ 正確寫法：`<div class="chart-canvas-wrap" style="height:280px"><canvas id="chartDonut"></canvas></div>`
- CSS：`.chart-canvas-wrap{position:relative;width:100%}` + `.chart-canvas-wrap canvas{width:100%!important;height:100%!important;display:block}`
- 科室橫條圖高度依科室數量動態計算：`Math.max(260, unitKeys.length * 28)` 並用 JS 設定父容器高度
- 所有金額以「萬元」顯示（`(v/10000).toFixed(0)+'萬'`），避免數字過長
- 警示色標準：動支率 ≥ 90% → `#c62828`（紅），≥ 70% → `#e07b00`（橙），其餘 → `#2e7d32`（綠）


---

### Step 4：推送至 GitHub Pages

```python
import subprocess, shutil, os, time

GITHUB_TOKEN  = "<your_token>"  # 實際 token 請自行填入
GITHUB_REPO   = "argus911/BudgetApp"
GITHUB_BRANCH = "main"

# ⚠️ 永遠用時間戳路徑，避免前次 session 殘留權限問題
WORK_DIR = f'/tmp/BA_{int(time.time())}'
idx      = '/tmp/budget_out/index.html'
icon     = '/tmp/icons/icon.png'

repo_url = f"https://{GITHUB_TOKEN}@github.com/{GITHUB_REPO}.git"
subprocess.run(["git","clone","--depth=1","--branch",GITHUB_BRANCH,repo_url,WORK_DIR], check=True, capture_output=True)
shutil.copy(idx, f"{WORK_DIR}/index.html")
# ★★★ 日常 CSV 更新不推 icon.png（icon 已 base64 內嵌在 index.html）
# ★★★ 只有首次建立或主動更換圖示時才需要另外 copy icon.png
os.chdir(WORK_DIR)
subprocess.run(["git","config","user.email","argus911@gmail.com"], check=True)
subprocess.run(["git","config","user.name","ArgusH"], check=True)
subprocess.run(["git","add","index.html"], check=True)   # ★ icon 已內嵌 HTML，不需另外推 icon.png
r = subprocess.run(["git","commit","-m",
    f"預算管理App {meta_year}年{meta_month}月更新（卡片式UI + 圖表分析）\n\nCo-Authored-By: Claude Sonnet 4.6 <noreply@anthropic.com>"],
    capture_output=True, text=True)
if "nothing to commit" not in r.stdout:
    subprocess.run(["git","push","origin",GITHUB_BRANCH], check=True)
print(f"✅ 已推送至 https://argus911.github.io/BudgetApp/")
```

---

### Step 5（選用）：產生 Xcode 原生 iOS 專案 ZIP

> 觸發時機：使用者說「xcode」、「native app」、「ipa」、「App Store」或「企業簽署部署」。
> 輸出：`BudgetApp_Xcode_115_04.zip`，解壓後用 Xcode 15+ 開啟即可建置。
> 架構：SwiftUI App + WKWebView 包裝 index.html，App Icon 使用 budget_icon_v5.png。

```python
import os, zipfile, base64, json, shutil

def generate_xcode_zip(html_path, icon_path, out_zip, meta_year='115', meta_month='04'):
    """
    產生 Xcode 原生 iOS 專案 ZIP。
    html_path : 已產生的 index.html 路徑
    icon_path : budget_icon_v5.png 路徑
    out_zip   : 輸出 zip 路徑
    """
    tmp = '/tmp/xcode_project'
    shutil.rmtree(tmp, ignore_errors=True)

    APP   = 'BudgetApp'
    BUNDLE_ID = 'com.cht.changhua.budgetapp'
    DEPLOY    = '16.0'

    # ── 目錄結構 ──────────────────────────────────────────
    src_dir  = os.path.join(tmp, APP)           # BudgetApp/
    xcproj   = os.path.join(tmp, f'{APP}.xcodeproj')
    assets   = os.path.join(src_dir, 'Assets.xcassets')
    icon_set = os.path.join(assets, 'AppIcon.appiconset')
    for d in [src_dir, xcproj, icon_set]:
        os.makedirs(d, exist_ok=True)

    # ── App.swift ─────────────────────────────────────────
    open(os.path.join(src_dir,'App.swift'),'w').write(f"""\
import SwiftUI

@main
struct {APP}: App {{
    var body: some Scene {{
        WindowGroup {{
            ContentView()
                .preferredColorScheme(.light)
        }}
    }}
}}
""")

    # ── ContentView.swift ─────────────────────────────────
    open(os.path.join(src_dir,'ContentView.swift'),'w').write(f"""\
import SwiftUI

struct ContentView: View {{
    var body: some View {{
        BudgetWebView()
            .ignoresSafeArea()
            .navigationBarHidden(true)
    }}
}}
""")

    # ── BudgetWebView.swift（WKWebView 包裝）──────────────
    open(os.path.join(src_dir,'BudgetWebView.swift'),'w').write(f"""\
import SwiftUI
import WebKit

struct BudgetWebView: UIViewRepresentable {{
    func makeUIView(context: Context) -> WKWebView {{
        let config = WKWebViewConfiguration()
        config.preferences.javaScriptEnabled = true
        config.allowsInlineMediaPlayback   = true
        let wv = WKWebView(frame: .zero, configuration: config)
        wv.scrollView.bounces   = false
        wv.isOpaque             = false
        wv.backgroundColor      = .clear
        if let url = Bundle.main.url(forResource: "index", withExtension: "html") {{
            wv.loadFileURL(url, allowingReadAccessTo: url.deletingLastPathComponent())
        }}
        return wv
    }}
    func updateUIView(_ uiView: WKWebView, context: Context) {{}}
}}
""")

    # ── index.html（預算資料 HTML）─────────────────────────
    shutil.copy(html_path, os.path.join(src_dir, 'index.html'))

    # ── Info.plist ────────────────────────────────────────
    open(os.path.join(src_dir,'Info.plist'),'w').write(f"""\
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN"
  "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0"><dict>
  <key>CFBundleDisplayName</key><string>預算管理</string>
  <key>CFBundleIdentifier</key><string>{BUNDLE_ID}</string>
  <key>CFBundleName</key><string>{APP}</string>
  <key>CFBundleShortVersionString</key><string>1.{meta_year}.{meta_month}</string>
  <key>CFBundleVersion</key><string>1</string>
  <key>UILaunchStoryboardName</key><string>LaunchScreen</string>
  <key>UISupportedInterfaceOrientations</key>
  <array>
    <string>UIInterfaceOrientationPortrait</string>
    <string>UIInterfaceOrientationLandscapeLeft</string>
    <string>UIInterfaceOrientationLandscapeRight</string>
  </array>
  <key>UIRequiresFullScreen</key><true/>
  <key>NSAppTransportSecurity</key>
  <dict><key>NSAllowsLocalNetworking</key><true/></dict>
</dict></plist>
""")

    # ── Assets.xcassets/Contents.json ─────────────────────
    open(os.path.join(assets,'Contents.json'),'w').write(
        json.dumps({"info":{"author":"xcode","version":1}}, indent=2))

    # ── AppIcon.appiconset/Contents.json ──────────────────
    shutil.copy(icon_path, os.path.join(icon_set, 'icon_1024.png'))
    open(os.path.join(icon_set,'Contents.json'),'w').write(json.dumps({
        "images":[
            {"idiom":"universal","platform":"ios","size":"1024x1024",
             "scale":"1x","filename":"icon_1024.png"}
        ],
        "info":{"author":"xcode","version":1}
    }, indent=2))

    # ── project.pbxproj ───────────────────────────────────
    # UUID 常數（固定值，保持專案可重現）
    P = {
        'ROOT':   'AA000001000000000000000A',
        'MAIN_GROUP': 'AA000001000000000000000B',
        'SRC_GROUP':  'AA000001000000000000000C',
        'ASSETS_GRP': 'AA000001000000000000000D',
        'HTML_GRP':   'AA000001000000000000000E',
        'TARGET':     'AA000001000000000000000F',
        'NATIVE_TGT': 'AA000001000000000000000G'.replace('G','1'),
        'BUILD_CFG_LIST_PRJ': 'AA00000200000000000000AA',
        'BUILD_CFG_LIST_TGT': 'AA00000200000000000000AB',
        'DEBUG_PRJ':  'AA00000200000000000000BA',
        'RELEASE_PRJ':'AA00000200000000000000BB',
        'DEBUG_TGT':  'AA00000200000000000000CA',
        'RELEASE_TGT':'AA00000200000000000000CB',
        'SOURCES':    'AA00000300000000000000AA',
        'RESOURCES':  'AA00000300000000000000AB',
        'APP_SWIFT':  'AA00000400000000000000AA',
        'CV_SWIFT':   'AA00000400000000000000AB',
        'WV_SWIFT':   'AA00000400000000000000AC',
        'PLIST':      'AA00000400000000000000AD',
        'ASSETS':     'AA00000400000000000000AE',
        'INDEX_HTML': 'AA00000400000000000000AF',
        'PRODUCT':    'AA00000500000000000000AA',
        'APP_SWIFT_B':'AA00000600000000000000AA',
        'CV_SWIFT_B': 'AA00000600000000000000AB',
        'WV_SWIFT_B': 'AA00000600000000000000AC',
        'ASSETS_B':   'AA00000600000000000000AD',
        'HTML_B':     'AA00000600000000000000AE',
    }
    open(os.path.join(xcproj,'project.pbxproj'),'w').write(f"""\
// !$*UTF8*$!
{{
archiveVersion = 1;
classes = {{}};
objectVersion = 56;
objects = {{

/* Begin PBXBuildFile section */
{P['APP_SWIFT_B']} /* App.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {P['APP_SWIFT']}; }};
{P['CV_SWIFT_B']} /* ContentView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {P['CV_SWIFT']}; }};
{P['WV_SWIFT_B']} /* BudgetWebView.swift in Sources */ = {{isa = PBXBuildFile; fileRef = {P['WV_SWIFT']}; }};
{P['ASSETS_B']} /* Assets.xcassets in Resources */ = {{isa = PBXBuildFile; fileRef = {P['ASSETS']}; }};
{P['HTML_B']} /* index.html in Resources */ = {{isa = PBXBuildFile; fileRef = {P['INDEX_HTML']}; }};
/* End PBXBuildFile section */

/* Begin PBXFileReference section */
{P['PRODUCT']} /* {APP}.app */ = {{isa = PBXFileReference; explicitFileType = wrapper.application; includeInIndex = 0; path = {APP}.app; sourceTree = BUILT_PRODUCTS_DIR; }};
{P['APP_SWIFT']} /* App.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = App.swift; sourceTree = "<group>"; }};
{P['CV_SWIFT']} /* ContentView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = ContentView.swift; sourceTree = "<group>"; }};
{P['WV_SWIFT']} /* BudgetWebView.swift */ = {{isa = PBXFileReference; lastKnownFileType = sourcecode.swift; path = BudgetWebView.swift; sourceTree = "<group>"; }};
{P['PLIST']} /* Info.plist */ = {{isa = PBXFileReference; lastKnownFileType = text.plist.xml; path = Info.plist; sourceTree = "<group>"; }};
{P['ASSETS']} /* Assets.xcassets */ = {{isa = PBXFileReference; lastKnownFileType = folder.assetcatalog; path = Assets.xcassets; sourceTree = "<group>"; }};
{P['INDEX_HTML']} /* index.html */ = {{isa = PBXFileReference; lastKnownFileType = text.html; path = index.html; sourceTree = "<group>"; }};
/* End PBXFileReference section */

/* Begin PBXGroup section */
{P['MAIN_GROUP']} = {{isa = PBXGroup; children = ({P['SRC_GROUP']}, {P['PRODUCT']},); sourceTree = "<group>"; }};
{P['SRC_GROUP']} /* {APP} */ = {{isa = PBXGroup; children = ({P['APP_SWIFT']}, {P['CV_SWIFT']}, {P['WV_SWIFT']}, {P['INDEX_HTML']}, {P['ASSETS']}, {P['PLIST']},); path = {APP}; sourceTree = "<group>"; }};
/* End PBXGroup section */

/* Begin PBXNativeTarget section */
{P['NATIVE_TGT']} /* {APP} */ = {{
    isa = PBXNativeTarget;
    buildConfigurationList = {P['BUILD_CFG_LIST_TGT']};
    buildPhases = ({P['SOURCES']}, {P['RESOURCES']},);
    buildRules = ();
    dependencies = ();
    name = {APP};
    productName = {APP};
    productReference = {P['PRODUCT']};
    productType = "com.apple.product-type.application";
}};
/* End PBXNativeTarget section */

/* Begin PBXProject section */
{P['ROOT']} /* Project object */ = {{
    isa = PBXProject;
    buildConfigurationList = {P['BUILD_CFG_LIST_PRJ']};
    compatibilityVersion = "Xcode 14.0";
    mainGroup = {P['MAIN_GROUP']};
    productRefGroup = {P['MAIN_GROUP']};
    projectDirPath = "";
    projectRoot = "";
    targets = ({P['NATIVE_TGT']},);
}};
/* End PBXProject section */

/* Begin PBXResourcesBuildPhase section */
{P['RESOURCES']} /* Resources */ = {{isa = PBXResourcesBuildPhase; buildActionMask = 2147483647; files = ({P['ASSETS_B']}, {P['HTML_B']},); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXResourcesBuildPhase section */

/* Begin PBXSourcesBuildPhase section */
{P['SOURCES']} /* Sources */ = {{isa = PBXSourcesBuildPhase; buildActionMask = 2147483647; files = ({P['APP_SWIFT_B']}, {P['CV_SWIFT_B']}, {P['WV_SWIFT_B']},); runOnlyForDeploymentPostprocessing = 0; }};
/* End PBXSourcesBuildPhase section */

/* Begin XCBuildConfiguration section */
{P['DEBUG_PRJ']} /* Debug */ = {{isa = XCBuildConfiguration; buildSettings = {{ALWAYS_SEARCH_USER_PATHS = NO; SWIFT_VERSION = 5.0; IPHONEOS_DEPLOYMENT_TARGET = {DEPLOY}; }}; name = Debug; }};
{P['RELEASE_PRJ']} /* Release */ = {{isa = XCBuildConfiguration; buildSettings = {{ALWAYS_SEARCH_USER_PATHS = NO; SWIFT_VERSION = 5.0; IPHONEOS_DEPLOYMENT_TARGET = {DEPLOY}; }}; name = Release; }};
{P['DEBUG_TGT']} /* Debug */ = {{isa = XCBuildConfiguration; buildSettings = {{ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; BUNDLE_IDENTIFIER = {BUNDLE_ID}; INFOPLIST_FILE = {APP}/Info.plist; PRODUCT_NAME = {APP}; SWIFT_VERSION = 5.0; IPHONEOS_DEPLOYMENT_TARGET = {DEPLOY}; }}; name = Debug; }};
{P['RELEASE_TGT']} /* Release */ = {{isa = XCBuildConfiguration; buildSettings = {{ASSETCATALOG_COMPILER_APPICON_NAME = AppIcon; BUNDLE_IDENTIFIER = {BUNDLE_ID}; INFOPLIST_FILE = {APP}/Info.plist; PRODUCT_NAME = {APP}; SWIFT_VERSION = 5.0; IPHONEOS_DEPLOYMENT_TARGET = {DEPLOY}; }}; name = Release; }};
/* End XCBuildConfiguration section */

/* Begin XCConfigurationList section */
{P['BUILD_CFG_LIST_PRJ']} /* Build configuration list for PBXProject "{APP}" */ = {{isa = XCConfigurationList; buildConfigurations = ({P['DEBUG_PRJ']}, {P['RELEASE_PRJ']},); defaultConfigurationName = Release; }};
{P['BUILD_CFG_LIST_TGT']} /* Build configuration list for PBXNativeTarget "{APP}" */ = {{isa = XCConfigurationList; buildConfigurations = ({P['DEBUG_TGT']}, {P['RELEASE_TGT']},); defaultConfigurationName = Release; }};
/* End XCConfigurationList section */

}};
rootObject = {P['ROOT']};
}}
""")

    # ── 打包成 ZIP ────────────────────────────────────────
    with zipfile.ZipFile(out_zip, 'w', zipfile.ZIP_DEFLATED) as zf:
        for root, dirs, files in os.walk(tmp):
            for file in files:
                fp = os.path.join(root, file)
                arcname = os.path.relpath(fp, tmp)
                zf.write(fp, arcname)

    kb = os.path.getsize(out_zip) // 1024
    print(f'✅ Xcode ZIP: {out_zip}  ({kb} KB)')
    print('   解壓後用 Xcode 15+ 開啟 BudgetApp.xcodeproj')
    print('   需設定 Signing → Team 後即可建置到 iPhone')
    return out_zip


# 呼叫範例（在 Step 4 推送完 GitHub Pages 後執行）：
import glob
sessions = glob.glob('/sessions/*/mnt/ios_app_budget')
ws = sessions[0] if sessions else '/tmp'
xcode_zip = os.path.join(ws, f'BudgetApp_Xcode_{meta_year}_{int(meta_month):02d}.zip')
generate_xcode_zip(
    html_path = os.path.join(ws, 'index.html'),
    icon_path = os.path.join(ws, 'budget_icon_v5.png'),
    out_zip   = xcode_zip,
    meta_year = meta_year,
    meta_month= meta_month,
)
```

**Xcode 專案說明**：

| 檔案 | 說明 |
|---|---|
| `App.swift` | SwiftUI @main 入口，強制 light mode |
| `ContentView.swift` | 呼叫 BudgetWebView |
| `BudgetWebView.swift` | UIViewRepresentable 包裝 WKWebView，載入 index.html |
| `index.html` | 預算資料 HTML（含完整資料，離線可用）|
| `Assets.xcassets/AppIcon.appiconset/` | App 圖示（1024×1024）|
| `Info.plist` | Bundle ID、版本、螢幕方向、ATS 設定 |
| `BudgetApp.xcodeproj/project.pbxproj` | Xcode 專案定義 |

**建置步驟**（提示使用者）：
```
1. 解壓縮 BudgetApp_Xcode_115_04.zip
2. 雙擊 BudgetApp.xcodeproj 用 Xcode 15+ 開啟
3. 點選 BudgetApp Target → Signing & Capabilities
4. 選擇你的 Apple 開發者 Team
5. 連接 iPhone → Cmd+R 建置執行
```

---

### Step 6：告知使用者 iOS 加入方式

```
1. 用 Safari 開啟 https://argus911.github.io/BudgetApp/
2. 點下方「分享」按鈕（⬆️）
3. 選擇「加入主畫面」
4. 點右上角「加入」即完成
```

---

## 欄位對照速查表

| App 顯示欄位 | CSV 欄位 | Excel 欄位 | 說明 |
|---|---|---|---|
| 本月動支數 | **本月差異** | 本月動支數 | 月淨支出 |
| **本月餘額** | **本月餘額** | **累計動支數** | ★TAIS累計帳務餘額★ |
| 本月預算數 | 本月預算數 | 本月預算數 | BGTTM |
| 至本月預算數累計 | 至本月預算數累計 | 至本月累計預算數 | BGTTTM |
| 累計動支率 | 累計動支率% | 累計動支率% | PCT_OF_MBUDGET |
| 本年度預算 | 本年度預算 | 本年度預算 | BGTTY |
| 年度動支率 | 年度動支率% | 本年度動支率% | PCT_OF_BUDGET |
| 剩餘可動支數 | 剩餘可動支 | 本年度預算-累計動支數 | 年度剩餘 |
| 預算主管單位 | Excel lookup | 預算主管 | CATEGORY |

---

## 已知限制

1. **macOS FUSE 掛載**：Cowork 掛載的 macOS 資料夾，Linux 端無法新建繁體中文檔名。改用 ASCII 檔名。
2. **預算主管單位**：來自 `TAIS_report_budget_*.csv` 的 `預算主管單位` 欄位（行銷科、供應科等）。若未上傳 TAIS_report，則所有 `預算主管單位` 為空字串，App 不顯示科室篩選。
3. **無對應科室 14 筆**（115年4月）：R25、183、20194、3320、3321K、929AB/JB/JC/JD、9294I/K/N、92973、9299O 等，`預算主管單位` 為空字串，卡片不顯示科室徽章，不進入科室篩選 Chips。**絕對禁止**用費用分類名稱作 fallback。
4. **CJK 字型**：`ipag.ttf`（IPA Gothic）在此容器**不存在**，勿使用。正確方案為複合字型：繁體中文用 `/usr/share/fonts/truetype/droid/DroidSansFallbackFull.ttf`，ASCII 數字用 `canvas-design/canvas-fonts/IBMPlexMono-Bold.ttf`（DroidSansFallback 不含 ASCII 字符）。
5. **JS 語法安全**：HTML 中所有動態 UI（chip、picker 等）必須用 `document.createElement` + `dataset` + `addEventListener`，禁止 `innerHTML +=` 配合 inline onclick 字串插值。
6. **git clone 路徑衝突**：若 `/tmp/BudgetApp` 由前次 session 建立且無寫入權限，改 clone 至時間戳路徑（`/tmp/BA_{int(time.time())}`）。
7. **JSON 資料驗證**：每次產生 HTML 前必須斷言科室清單不含費用分類名稱（見 Step 1A 驗證步驟）。
8. **iOS apple-touch-icon**：iOS PWA 圖示只讀 HTML 內 base64 `<link>` 標籤，`icon.png` 外部檔對 iOS 無效。更新圖示必須重新產生整份 `index.html`，並請使用者先刪除舊主畫面圖示再重新加入。
9. **JS style 拼接分號陷阱**：在 innerHTML 字串中，ternary expression 後若直接接 `;CSS屬性` 會造成全頁 SyntaxError。症狀：頁面結構正常但資料完全空白。修正方式見 Step 3C-3。
10. **CSV 欄位版本差異**：115年4月起 TAIS_budget 欄位名稱已更動（`月`→`月份`、`會計項目`→`科目名稱`、`本月差異`→`本月動支增減` 等），詳見 Step 1B 對照表。且 CSV 已內含 `預算主管單位`，無須另外 TAIS_report CSV。
11. **圖表分析分頁（v9）**：Chart.js `maintainAspectRatio: false` **必須搭配父容器明確高度**，否則 canvas 高度為 0 導致圖表消失。正確做法：使用 `.chart-canvas-wrap{position:relative;width:100%}` 容器設定 `style=height:NNpx`，canvas 設 `width/height:100%`。❌ 禁止直接在 `<canvas>` 標籤加 `height` 屬性。Chart.js 從 CDN 載入需網路。KPI 卡片離線可用。
