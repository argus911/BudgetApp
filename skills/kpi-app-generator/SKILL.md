---
name: kpi-app-generator
description: |
  將中華電信彰化營運處每月的 KPI 累計成績 PDF(由總公司業管處發布,
  類似「營運處累計至 115 年 X 月 KPI 成績」)轉換成可直接部署為 iOS PWA
  的單檔 HTML 指標管理 App,並自動推送至 GitHub Pages
  (https://argus911.github.io/BudgetApp/KPI/)。

  受眾:營運處總經理、副總、單位主管 — 需要的是「速查 + 紅黃綠燈警示
  + 全處比較視覺化 + 月度趨勢」,而非逐字閱讀公文。

  使用時機(符合任一項即立即觸發):
  - 使用者上傳「營運處累計至 115 年 X 月 KPI 成績.pdf」或類似命名 PDF
  - 使用者上傳含 17 個營運處 × 各項 KPI 得分的 PDF/Excel
  - 使用者說「更新 KPI App」、「產生 KPI 字典 App」、「上傳新月份 KPI 實績」
  - 使用者說「推送 KPI HTML」、「重新生成 KPI 指標管理」
  - 使用者說「skill kpi」或「KPI 月報」
  - 使用者同時上傳多個月份的 PDF → 自動合併建構月度趨勢
  - 使用者說「補上 X 月 KPI 資料」、「合併歷史月份」、「月度趨勢」
  - 只要看到 PDF 內含 17 個營運處(台北、新北、基隆、桃園、新竹、苗栗、
    花蓮、宜蘭、台中、彰化、南投、雲林、嘉義、台南、高雄、屏東、台東)
    與 KPI 編號(O1、O2、L1~L4、M1~M7、ESG)的得分矩陣,主動觸發此 skill

  輸出:
  1. 單一 HTML 檔(PWA,可加入 iPhone 主畫面,離線可用)
  2. 自動推送 index.html 至 GitHub Pages:
     https://argus911.github.io/BudgetApp/KPI/
  3. 本地檔案產出至 /mnt/user-data/outputs/KPI_Dict_App_v1.X_115_MM.html
---

# KPI 字典與指標管理 App 產生器 v1.3.5

## 概述

讀取使用者每月上傳的 **KPI 累計成績 PDF**，結合內建的 **115 年度 KPI 字典核定版**，
產出一份自給自足的 HTML 檔案，並**自動推送至 GitHub Pages**。

App 包含 6 個分頁：

| Tab | 內容 |
|---|---|
| 📈 儀表板 | 彰化最新月份得分、排名(總/組內)、紅黃綠燈警示、14 項 KPI 進度條 |
| 📖 字典 | 14 項 KPI + 5 項機構綜合表現完整定義、公式、評分標準、彰化目標、搜尋、類別篩選 |
| 🏆 比較 | Chart.js 三模式：排名橫條(17 處) / A/B/C 組平均 / 彰化雷達 vs B 組 |
| 📉 趨勢 | 彰化月度走勢線 + B 組均對照，含 95 達標基準線、月變化、與起始月差距 |
| 🧮 試算 | 輸入實績/目標即時試算得分，自動處理三種公式(愈大愈好/愈小愈好/成本控制) |
| 📝 筆記 | 主管個人 localStorage 備忘，可掛在特定 KPI 下 |

---

## 版本變更摘要

| 版本 | 變更 | 日期 |
|---|---|---|
| v1.0 | 初版字典 + 試算器 + 筆記 | 2026/05/12 |
| v1.1 | 整合單月實績 + Chart.js 比較分頁 | 2026/05/14 |
| v1.1a | 修正 14 處分組排名抄錄錯誤(改為自動計算) | 2026/05/14 |
| v1.2 | 多月歷史 + 月度趨勢分頁(彰化 vs B 組均 vs 95 達標線) | 2026/05/15 |
| v1.3 | 修復 Excel/PDF 在瀏覽器內上傳解析功能(3 個根本 Bug) | 2026/06/17 |
| v1.3.1 | 修正 script 標籤結構錯誤、mergeUploadedOnLoad 執行時序 | 2026/06/17 |
| v1.3.2 | 修復上傳後比較/儀表板頁籤不更新問題(ACTUAL 同步) | 2026/06/17 |
| v1.3.3 | 新增上傳後自動寫回 HTML 持久化機制(PyQt 環境) | 2026/06/17 |
| v1.3.4 | 修復儀表板 Hero 區塊月份標籤硬編碼問題(heroLabel 動態更新) | 2026/06/17 |
| **v1.3.5** | **修復 history months 欄位格式不一致：kpis→scores、groupRank→group_rank；新增 normalizeMonthRecords() 函數** | **2026/06/22** |

---

## GitHub 資源位置

```
GITHUB_REPO=argus911/BudgetApp
GITHUB_BRANCH=main
GITHUB_TOKEN=ghp_xxxx_請自行填入實際Token_xxxx

# KPI App HTML（每次更新月份後推送）
KPI/index.html          → https://argus911.github.io/BudgetApp/KPI/

# 歷史資料（合併月份後同步推送）
KPI/actual_history.json

# 配套 Python 主程式（含 HtmlViewerPanel 持久化邏輯）
TAIS_綜合管理系統_合併版_v5_37.py
```

---

## Skill 資源檔案

| 檔案 | 用途 |
|---|---|
| `SKILL.md` | 本說明文件 |
| `kpi_dict_115.json` | 115 年度 KPI 字典核定版 — **永久資料，不需每月更新** |
| `build_html.py` | HTML 產生器，讀取字典 JSON + 歷史 JSON 後輸出單檔 PWA |
| `actual_history_sample.json` | 範例歷史檔（實際歷史儲存在 GitHub repo 的 KPI/actual_history.json） |

---

## ★ 關鍵 Bug 修正清單（每次生成/更新 HTML 後必須確認）

### Bug 1：`<script src>` 標籤不可內嵌程式碼

```html
<!-- ✅ 正確：CDN 和程式碼用獨立標籤 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js"></script>
<script>
  function handleKpiFileUpload(e){ ... }
</script>

<!-- ❌ 錯誤：有 src 的 script 內部程式碼會被瀏覽器完全忽略 -->
<script src="https://cdn.jsdelivr.net/npm/chart.js@4.4.1/dist/chart.umd.min.js">
  function handleKpiFileUpload(e){ ... }
</script>
```

### Bug 2：`mergeUploadedOnLoad` 執行時序

`HISTORY` 在檔案底部才定義，頂端不可立即執行 IIFE，須定義為普通函數，
在初始化區塊（`HISTORY` 定義後）呼叫，且函數內須同步更新 `ACTUAL`：

```javascript
// ★ v1.3.5：必須先呼叫 normalizeMonthRecords（見 Bug 7）
mergeUploadedOnLoad();
renderDashboard();
```

### Bug 3：`ACTUAL` 必須是 `let`，上傳後全頁籤同步更新

```javascript
let ACTUAL = DATA.actual;  // ★ 用 let，不用 const

// applyUploadedMonth 結尾：
const validMonths = HISTORY.months.filter(m=>!m.placeholder && m.records && m.records.length>0);
if(validMonths.length>0){
  const latest = validMonths.reduce((a,b)=>(parseInt(b.month)>parseInt(a.month)?b:a));
  ACTUAL = latest;
  DATA.actual = latest;
}
renderDashboard();
if(typeof renderCompareControls==='function') renderCompareControls();
if(typeof renderCompareChart==='function')    renderCompareChart();
if(typeof renderTrendChart==='function')      renderTrendChart();
if(typeof renderTrendControls==='function')   renderTrendControls();
```

### Bug 4：比較頁月份文字不可寫死

```javascript
// ✅ 正確：動態讀取 ACTUAL.period
let opts = `<option value="annual">年度合併得分（${ACTUAL.period||'累計得分'}）</option>`;

// ❌ 錯誤：硬編碼
let opts = '<option value="annual">年度合併得分(累計至 4 月)</option>';
```

### Bug 5：PDF iframe 在 `file://` 環境失效

```javascript
// ✅ 正確：純文字錯誤訊息
msg.innerHTML = `<div class="err">⚠️ PDF 解析失敗：${err.message}<br>建議改用 .xlsx 格式。</div>`;

// ❌ 錯誤：file:// 環境 iframe blob 被瀏覽器安全策略阻擋
msg.innerHTML = `...<iframe src="${URL.createObjectURL(file)}"></iframe>`;
```

### Bug 6：儀表板 Hero 月份標籤硬編碼（v1.3.4 新增）

儀表板 Hero 區塊的「115/4 累計得分」是靜態 HTML 文字，上傳新月份後不會更新。
必須加上 `id="heroLabel"` 並在 `renderDashboard()` 動態更新：

```html
<!-- ✅ 正確：加上 id -->
<div class="lbl" id="heroLabel">115/4 累計得分</div>
```

```javascript
// renderDashboard() 內必須加上：
const _lbl = document.getElementById('heroLabel');
if(_lbl){
  const _pm = (ACTUAL.period||'').match(/(\d+)\s*年\s*(\d+)\s*月/);
  _lbl.textContent = _pm ? `${_pm[1]}/${_pm[2]} 累計得分` : (ACTUAL.period||'累計得分');
}
```

### Bug 7：history months 欄位格式不一致 → B組排名 undefined、KPI 清單空白（v1.3.5 新增）

**根本原因**：用 Python 建立新月份 history record 時，若使用 `kpis`/`groupRank` 欄位名稱，
但 JS `renderDashboard()` 讀的是 `me.scores[k.id]` 與 `me.group_rank`，導致：
- B 組排名顯示 `#undefined`
- 各項 KPI 成績全部空白

**✅ 正確的 history record 欄位格式**（Python 端生成時必須使用）：

```python
rec = {
    "office": "彰化",
    "annual": 73.91,
    "rank": 16,
    "group_rank": 5,      # ★ 用 group_rank，不用 groupRank
    "scores": {           # ★ 用 scores，不用 kpis
        "O1": 93.80, "O2": 99.12, "L1": 93.10, "L2": 101.00,
        "L3": 99.91, "L4": None,  "M1": 97.08, "M2": 97.88,
        "M3": 70.57, "M4": 88.25, "M5": 93.54, "M6": 75.00,
        "M7": 79.40, "E":  None
    }
}
```

**❌ 錯誤格式（禁止使用）**：

```python
rec = {
    "groupRank": 5,   # ❌ 應為 group_rank
    "kpis": {...}     # ❌ 應為 scores
}
```

**✅ JS 端防禦性修正**：在 HTML 中加入 `normalizeMonthRecords()` 函數，
即使 Python 端產生格式錯誤，頁面載入時也能自動修正：

```javascript
function normalizeMonthRecords(month){
  // ★ v1.3.5 統一欄位格式：kpis→scores, groupRank→group_rank
  if(!month || !month.records) return month;
  month.records.forEach(r=>{
    if(r.kpis && !r.scores){ r.scores = r.kpis; delete r.kpis; }
    if(r.groupRank != null && r.group_rank == null){
      r.group_rank = r.groupRank; delete r.groupRank;
    }
  });
  return month;
}
```

此函數須在 **兩處** 呼叫：

```javascript
// 1. mergeUploadedOnLoad() 內：
function mergeUploadedOnLoad(){
  if(typeof HISTORY==='undefined') return;
  const uploaded = loadUploadedMonths();
  if(!uploaded.length) return;
  uploaded.forEach(upMonth=>{
    normalizeMonthRecords(upMonth);  // ★ 呼叫點 1
    const existing = HISTORY.months.find(m=>m.month===upMonth.month && m.year===upMonth.year);
    if(existing && existing.placeholder){
      Object.assign(existing, upMonth, {placeholder:false});
    } else if(!existing){
      HISTORY.months.push(upMonth);
      HISTORY.months.sort((a,b)=>a.month-b.month);
    }
  });
  HISTORY.months.forEach(m=>normalizeMonthRecords(m)); // ★ 正規化所有已嵌入月份
  const valid = HISTORY.months.filter(m=>!m.placeholder && m.records && m.records.length>0);
  if(valid.length>0){
    const latest = valid.reduce((a,b)=>(parseInt(b.month)>parseInt(a.month)?b:a));
    ACTUAL = latest;
    if(typeof DATA!=='undefined') DATA.actual = latest;
  }
}

// 2. applyUploadedMonth() 開頭：
function applyUploadedMonth(newMonth, fileName, msg){
  normalizeMonthRecords(newMonth); // ★ 呼叫點 2
  // ...其餘原有邏輯
}
```

**新月份更新時 Python 端的正確欄位建構範本**（Step 1 替換）：

```python
month_obj = {
    "year": 115,
    "month": 6,           # ← 替換為當月月份
    "period": "115年6月",  # ← 替換
    "placeholder": False,
    "records": []
}
for i, o in enumerate(OFFICES):
    month_obj["records"].append({
        "office": o,
        "annual": ANNUAL[i],
        "rank": RANK[i],
        "group_rank": GROUP_RANK[i],  # ★ 必須用 group_rank
        "scores": {k: SCORES[k][i] for k in SCORES}  # ★ 必須用 scores
    })
```

---

## ★ PyQt 持久化機制（v1.3.3 新增，v5.37 Python 端實作）

**問題**：WebEngine 在 `file://` 模式下 localStorage 存於記憶體 profile，
程式關閉後清空，重開後回到 HTML 內嵌的舊月份資料。

**解法**：上傳成功後自動將最新 HISTORY 寫回 `KPI_Dict.html` 本機檔案。

### 資料流

```
HTML: applyUploadedMonth 成功
  → 偵測 window.__in_pyqt__ 旗標（PyQt 環境才觸發）
  → window.location.href = 'pyqtapp://save_kpi_history'
  → Python: acceptNavigationRequest 攔截
  → Python: runJavaScript('JSON.stringify(HISTORY)') 讀取完整 HISTORY
  → Python: regex 替換 KPI_Dict.html 內 DATA.history
  → Python: 寫回本機 HTML 檔案
  → 結果: 重開程式後直接讀到最新月份
```

### HTML 端必要程式碼（applyUploadedMonth 結尾加入）

```javascript
try{
  if(typeof window.__in_pyqt__ !== 'undefined' && window.__in_pyqt__){
    window.location.href = 'pyqtapp://save_kpi_history';
  }
}catch(e){ /* 非 PyQt 環境略過 */ }
```

### Python 端必要程式碼（HtmlViewerPanel）

**① `_on_load_finished`** — 注入 PyQt 環境旗標：
```python
js_parts.append("window.__in_pyqt__ = true;")
```

**② `acceptNavigationRequest`** — 攔截 save_kpi_history：
```python
elif cmd == 'save_kpi_history':
    QTimer.singleShot(0, self._panel._save_kpi_history_to_html)
```

**③ `_save_kpi_history_to_html`** — 用 runJavaScript 讀取後寫回：
```python
def _save_kpi_history_to_html(self, _=None):
    def _do_write(history_json):
        import json, re, stat, os
        new_history = json.loads(str(history_json))
        # regex 找 DATA 物件邊界 → 更新 history → 寫回 HTML 檔
        ...
    self._web_view.page().runJavaScript(
        "JSON.stringify(typeof HISTORY!=='undefined' ? HISTORY : null)",
        _do_write
    )
```

**④ `init_ui` WebEngine 設定** — 啟用 localStorage：
```python
_s.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)
```

---

## ★ Excel 解析：支援總公司橫排格式

總公司 Excel（`01_115年各營運處KPI年度得分-YYYYMMDD.xlsx`）結構：
- 第 0 行：月份標題（`115年5月`）
- 第 2 行：欄位標題（`KPIs編號、評核項目、權重、目標、台北、新北…`）
- KPI 為**列**，辦事處為**欄**（橫排格式）

**修正**：用 `{header:1}` 取得原始二維陣列，自動掃描含最多辦事處名稱的列作標題列，
支援格式 A（直排，每列一辦事處）和格式 B（橫排，KPI 為列）。

---

## ★ PDF 解析：X/Y 座標位置比對法

舊邏輯「辦事處後面抓數字」在橫排表格完全失效。修正方式：

```
1. 取得所有文字項目的 (str, x, y) 座標
2. 找含最多辦事處名稱的 Y 帶 → 確認標題列
3. 記錄各辦事處 X 座標 officeXMap
4. 掃描各 KPI 列 → 記錄 Y 座標 kpiRowYMap
5. 交叉 getValAtYX(kpiY, officeX)，容忍 X ±20pt、Y ±8pt
```

---

## 執行步驟（生成新月份 HTML）

### Step 0：準備工作目錄

```bash
WORK_DIR=/home/claude/kpi_work_$(date +%s)
mkdir -p $WORK_DIR

TOKEN="ghp_xxxx_請自行填入實際Token_xxxx"
# 下載現有 HTML（作為基底，保留所有 JS 邏輯）
curl -sL -H "Authorization: token $TOKEN" \
  "https://raw.githubusercontent.com/argus911/BudgetApp/main/KPI/index.html" \
  -o $WORK_DIR/existing_index.html

# 下載歷史資料
curl -sL -H "Authorization: token $TOKEN" \
  "https://raw.githubusercontent.com/argus911/BudgetApp/main/KPI/actual_history.json" \
  -o $WORK_DIR/actual_history.json 2>/dev/null

if ! python3 -c "import json; json.load(open('$WORK_DIR/actual_history.json'))" 2>/dev/null; then
  echo "ℹ️ 建立全新歷史檔"
  rm -f $WORK_DIR/actual_history.json
fi
```

### Step 1：解析 PDF 並建立新月份 record（★ 注意欄位格式）

```python
OFFICES = ['台北','新北','基隆','桃園','新竹','苗栗','花蓮','宜蘭',
           '台中','彰化','南投','雲林','嘉義','台南','高雄','屏東','台東']

SCORES = {
    'O1': [...17 個浮點數...],
    'O2': [...],
    'L1': [...], 'L2': [...], 'L3': [...],
    'L4': [None]*17,
    'M1': [...], 'M2': [...], 'M3': [...],
    'M4': [...], 'M5': [...], 'M6': [...], 'M7': [...],
    'E':  [None]*17,   # ESG 年指標，JSON key 用 'E'
}
ANNUAL = [...17 浮點數...]

GROUPS = {
    'A': ['台北','新北','桃園','台中','台南','高雄'],
    'B': ['基隆','新竹','彰化','雲林','嘉義','屏東'],
    'C': ['苗栗','宜蘭','花蓮','南投','台東'],
}
RANK = [0]*17
for r, i in enumerate(sorted(range(17), key=lambda i: -ANNUAL[i])): RANK[i] = r+1
GROUP_RANK = [0]*17
for g, members in GROUPS.items():
    idxs = [OFFICES.index(o) for o in members]
    for r, i in enumerate(sorted(idxs, key=lambda i: -ANNUAL[i])): GROUP_RANK[i] = r+1

# ★★★ month record 欄位必須用 scores + group_rank（不是 kpis / groupRank）★★★
month_obj = {
    "year": 115,
    "month": MM,           # ← 當月月份數字
    "period": "115年MM月", # ← 替換
    "placeholder": False,
    "records": []
}
for i, o in enumerate(OFFICES):
    month_obj["records"].append({
        "office": o,
        "annual": ANNUAL[i],
        "rank": RANK[i],
        "group_rank": GROUP_RANK[i],          # ★ group_rank
        "scores": {k: SCORES[k][i] for k in SCORES}  # ★ scores
    })
```

### Step 2：注入新月份到 actual_history.json

```python
import json

with open('actual_history.json') as f:
    history = json.load(f)

# 移除同月舊資料（避免重複）
history["months"] = [m for m in history["months"]
                     if not (m["month"] == month_obj["month"] and m["year"] == month_obj["year"])]
history["months"].append(month_obj)
history["months"].sort(key=lambda m: m["month"])
history["current_month"] = month_obj["month"]
history["current_period"] = month_obj["period"]

with open('actual_history.json', 'w', encoding='utf-8') as f:
    json.dump(history, f, ensure_ascii=False)
```

### Step 3：將 history 注入現有 HTML（保留所有 JS 邏輯）

```python
import json, re

with open('existing_index.html', 'r', encoding='utf-8') as f:
    html = f.read()

# 替換 DATA 物件內的 history
data_pos = html.find('const DATA =')
hist_in_data = html.find('"history":', data_pos)
val_start = html.find('{', hist_in_data)
depth = 0
i = val_start
while i < len(html):
    if html[i] == '{': depth += 1
    elif html[i] == '}':
        depth -= 1
        if depth == 0:
            val_end = i
            break
    i += 1

new_history_json = json.dumps(history, ensure_ascii=False, separators=(',',':'))
html = html[:val_start] + new_history_json + html[val_end+1:]

# 替換 actual 為最新月份
new_actual = {
    "period": month_obj["period"],
    "year": str(month_obj["year"]),
    "month": month_obj["month"],
    "pub_date": "YYYY-MM-DD",
    "max_score": 79,
    "records": month_obj["records"]  # ★ 已是 scores+group_rank 格式
}
actual_key_pos = html.find('"actual":')
actual_start = html.find('{', actual_key_pos)
depth = 0
i = actual_start
while i < len(html):
    if html[i] == '{': depth += 1
    elif html[i] == '}':
        depth -= 1
        if depth == 0:
            actual_end = i
            break
    i += 1
html = html[:actual_start] + json.dumps(new_actual, ensure_ascii=False, separators=(',',':')) + html[actual_end+1:]

# 更新 heroLabel 月份文字
html = re.sub(r'(\d+)/(\d+) 累計得分', f'115/{month_obj["month"]} 累計得分', html)

with open('index.html', 'w', encoding='utf-8') as f:
    f.write(html)
```

### Step 4：推送 GitHub

```bash
TOKEN="ghp_xxxx_請自行填入實際Token_xxxx"
PUSH_DIR=/tmp/KPI_push_$(date +%s)
git clone "https://${TOKEN}@github.com/argus911/BudgetApp.git" "$PUSH_DIR" --depth=1 --quiet
cp index.html "$PUSH_DIR/KPI/index.html"
cp actual_history.json "$PUSH_DIR/KPI/actual_history.json"
cd "$PUSH_DIR"
git config user.email "argus911@gmail.com"
git config user.name "ArgusH"
git add KPI/index.html KPI/actual_history.json
git commit -m "feat: KPI v1.3.5 — 更新 115 年 ${MONTH} 月累計實績"
git push origin main
echo "✅ https://argus911.github.io/BudgetApp/KPI/"
```

### Step 5：輸出並回報

```bash
cp index.html /mnt/user-data/outputs/KPI_Dict_App_v1.3.5_115_${MONTH_2D}.html
```

回報內容：
1. 線上網址：`https://argus911.github.io/BudgetApp/KPI/`
2. 彰化未達標（<85）與待加強（85~95）KPI 列表
3. 與上月差異（若可知）

---

## 紅黃綠燈邏輯

| 區間 | 顏色 | 標籤 |
|---|---|---|
| ≥ 95 分 | 🟢 綠 | 達標 |
| 85 ~ 94.99 | 🟡 黃 | 待加強 |
| < 85 | 🔴 紅 | 未達標 |
| None | ⚪ 灰 | 年指標 |

---

## 14 項 KPI 速查

| ID | 名稱 | 權重 | JSON key |
|---|---|---|---|
| O1 | 交易機構營收 | 25% | `O1` |
| O2 | 成本費用控制 | 20% | `O2` |
| L1 | 行動營運量 | 4% | `L1` |
| L2 | 寬頻營運量 | 4% | `L2` |
| L3 | 網路品質與韌性 | 5% | `L3` |
| L4 | 資安與個資保護 | 1% | `L4`（年指標） |
| M1 | 加值業務營運量 | 2% | `M1` |
| M2 | 影視營運量 | 2% | `M2` |
| M3 | 重點新興業務營收 | 5% | `M3` |
| M4 | ICT 專標案毛利額 | 5% | `M4` |
| M5 | Order Taking | 4% | `M5` |
| M6 | 5G 企業專網 | 2% | `M6` |
| M7 | 衛星業務營收 | 1% | `M7` |
| ESG | ESG 永續發展 | 5% | **`E`**（年指標，注意 key 是 E 非 ESG） |

合計 85%，另機構綜合表現 15%，由業務執副評定。

---

## 17 個營運處分組

| 組別 | 處別 |
|---|---|
| A 組 | 台北、新北、桃園、台中、台南、高雄 |
| B 組 | 基隆、新竹、**彰化**、雲林、嘉義、屏東 |
| C 組 | 苗栗、宜蘭、花蓮、南投、台東 |

---

## 已知限制

1. **排名禁止手動抄錄**（v1.1a 修正）：PDF 分組排名列順序不等於 OFFICES 順序，直接抄極易錯位。RANK 與 GROUP_RANK 一律程式自動計算。
2. **L4、ESG 為年指標**：平常月份填 `None`，年底才有值。
3. **PyQt 持久化**：需搭配 `TAIS_綜合管理系統_合併版_v5_37.py` 使用，瀏覽器直接開啟時不觸發寫回（但功能正常，下次開啟恢復到 HTML 內嵌資料）。
4. **GitHub Pages 同步延遲**：推送後約 30 秒~2 分鐘才生效。
5. **`file://` 限制**：本機直接雙擊 HTML 時，PDF iframe 預覽無效，但 Excel/PDF 上傳解析正常。
6. **加密 Excel**：總公司加密 Excel 無法解析，改用 PDF 輸入。
7. **history record 欄位格式**：必須用 `scores`/`group_rank`，勿用 `kpis`/`groupRank`（見 Bug 7）。

---

## 觸發短語對照

| 使用者說 | Claude 動作 |
|---|---|
| 上傳「累計至 115 年 X 月 KPI 成績.pdf」 | 立即執行完整流程 |
| 「更新 KPI App」+ 附 PDF/xlsx | 立即執行完整流程 |
| 「skill kpi」+ 附 PDF | 立即執行完整流程 |
| 「重新生成 KPI HTML」 | 用最新 actual JSON 重生 + 推送 |
| 「KPI 月報」 | 同「更新 KPI App」 |
