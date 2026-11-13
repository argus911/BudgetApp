# -*- coding: utf-8 -*-
"""
GitHub Pages 上線前檢查  v1.1
==========================================================
在 GitHub Actions 上執行（也可以在本機執行：python tools/check_pages.py）。
任何一項「錯誤」→ 結束碼 1 → 部署工作不會執行，網站維持上一版。
「警告」只顯示、不擋。

檢查規則寫在同資料夾的 pages_rules.json：
  pages        要檢查的網頁：最小檔案大小、必須出現／不可出現的文字
  kpi          KPI 內嵌資料 DATA 的欄位名稱與筆數（scores／group_rank，禁用 kpis／groupRank）
  csv          資料檔（例 budget.csv）的必要欄位與資料筆數範圍
  embedded     網頁內嵌資料陣列（例 var RAW = [...]）的筆數範圍、必要欄位、數字欄位（v1.1）
所有網頁的 <script> 都會用 node --check 做語法檢查（有 node 才檢查）。
"""
import csv, io, json, os, re, shutil, subprocess, sys, tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RULES = json.loads((Path(__file__).resolve().parent / "pages_rules.json").read_text(encoding="utf-8"))
errors, warnings = [], []


def err(where, msg):
    errors.append(f"✘ [{where}] {msg}")


def warn(where, msg):
    warnings.append(f"⚠ [{where}] {msg}")


def read(rel):
    return (ROOT / rel).read_text(encoding="utf-8-sig", errors="replace")


# ── 一、網頁基本檢查 ─────────────────────────────────────────
SCRIPT_RE = re.compile(r"<script(?P<attr>[^>]*)>(?P<body>.*?)</script>", re.S | re.I)


def check_js(rel, html):
    node = shutil.which("node")
    if not node:
        warn(rel, "找不到 node，略過 JavaScript 語法檢查")
        return
    for n, m in enumerate(SCRIPT_RE.finditer(html), 1):
        attr, body = m.group("attr").lower(), m.group("body")
        if "src=" in attr or not body.strip():
            continue
        if "application/json" in attr or "application/ld+json" in attr:
            try:
                json.loads(body)
            except ValueError as e:
                err(rel, f"第 {n} 段 JSON 資料無法解析：{e}")
            continue
        ext = ".mjs" if "module" in attr else ".js"
        with tempfile.NamedTemporaryFile("w", suffix=ext, delete=False, encoding="utf-8") as f:
            f.write(body)
        try:
            r = subprocess.run([node, "--check", f.name], capture_output=True, text=True, timeout=60)
            if r.returncode != 0:
                line = next((x for x in r.stderr.splitlines() if "Error" in x), r.stderr.strip()[:200])
                where = re.search(r":(\d+)\n", r.stderr)
                err(rel, f"第 {n} 段 <script> 語法錯誤（段內第 {where.group(1) if where else '?'} 行）：{line}")
        finally:
            os.unlink(f.name)


def check_pages():
    for rel, rule in RULES.get("pages", {}).items():
        p = ROOT / rel
        if not p.exists():
            err(rel, "檔案不存在")
            continue
        size = p.stat().st_size
        if size < rule.get("min_bytes", 1000):
            err(rel, f"檔案只有 {size:,} bytes，小於下限 {rule.get('min_bytes', 1000):,}（可能產生失敗或被截斷）")
        html = read(rel)
        if "</html>" not in html.lower():
            err(rel, "找不到 </html> 結尾，檔案可能被截斷")
        if "<title>" not in html.lower():
            warn(rel, "沒有 <title>")
        for s in rule.get("must_contain", []):
            if s not in html:
                err(rel, f"必須包含「{s}」但找不到")
        for s in rule.get("must_not_contain", []) + RULES.get("global_must_not_contain", []):
            if s in html:
                err(rel, f"不可出現「{s}」（第 {html[:html.index(s)].count(chr(10)) + 1} 行）")
        check_js(rel, html)


# ── 二、KPI 內嵌資料 ─────────────────────────────────────────
def grab_const(html, name):
    m = re.search(r"\bconst\s+%s\s*=\s*" % re.escape(name), html)
    if not m:
        return None
    obj, _ = json.JSONDecoder().raw_decode(html[m.end():])
    return obj


def check_records(where, recs, ids, rule, label):
    if not isinstance(recs, list):
        err(where, f"{label}.records 不是陣列")
        return
    lo, hi = rule.get("records_min", 1), rule.get("records_max", 999)
    if not lo <= len(recs) <= hi:
        err(where, f"{label} 有 {len(recs)} 筆，應介於 {lo}～{hi} 筆")
    need = set(rule.get("record_keys", []))
    bad = set(rule.get("forbidden_keys", []))
    offices = []
    for i, r in enumerate(recs):
        if not isinstance(r, dict):
            err(where, f"{label}.records[{i}] 不是物件")
            continue
        miss, wrong = need - set(r), bad & set(r)
        tag = f"{label}.records[{i}]（{r.get('office', '?')}）"
        if wrong:
            err(where, f"{tag} 使用了錯誤欄位名稱 {sorted(wrong)}（應為 scores／group_rank）")
        if miss:
            err(where, f"{tag} 缺少欄位 {sorted(miss)}")
        sc = r.get("scores")
        if isinstance(sc, dict) and ids:
            if set(sc) != set(ids):
                err(where, f"{tag} scores 的指標代號與 kpi 清單不一致：多 {sorted(set(sc) - set(ids))}、少 {sorted(set(ids) - set(sc))}")
            for k, v in sc.items():
                if v is not None and not isinstance(v, (int, float)):
                    err(where, f"{tag} scores.{k} 不是數字：{v!r}")
        offices.append(r.get("office"))
    dup = sorted({o for o in offices if offices.count(o) > 1})
    if dup:
        err(where, f"{label} 營運處重複：{dup}")


def check_kpi():
    for rel, rule in RULES.get("kpi", {}).items():
        if not (ROOT / rel).exists():
            err(rel, "檔案不存在")
            continue
        n0 = len(errors)
        text = read(rel)
        try:
            data = json.loads(text) if rel.endswith(".json") else grab_const(text, rule.get("const", "DATA"))
        except ValueError as e:
            err(rel, f"內嵌資料無法解析成 JSON：{e}")
            continue
        if data is None:
            err(rel, f"找不到 const {rule.get('const', 'DATA')} = …")
            continue
        for k in rule.get("top_keys", []):
            if k not in data:
                err(rel, f"缺少最上層欄位「{k}」")
        ids = [k.get("id") for k in data.get("kpi", [])] if isinstance(data.get("kpi"), list) else rule.get("kpi_ids", [])
        if rule.get("kpi_ids") and ids and set(ids) != set(rule["kpi_ids"]):
            warn(rel, f"kpi 指標清單與規則不同：{ids}")
        ids = ids or rule.get("kpi_ids", [])
        hist = data.get("history", data) if not rel.endswith(".json") else data
        months = hist.get("months") if isinstance(hist, dict) else None
        if not isinstance(months, list) or not months:
            err(rel, "history.months 沒有資料")
            continue
        periods = [m.get("period") for m in months]
        if len(set(periods)) != len(periods):
            err(rel, f"history.months 有重複月份：{periods}")
        nums = [m.get("month") for m in months]
        if nums != sorted(nums):
            err(rel, f"history.months 月份沒有依序排列：{nums}")
        for m in months:
            check_records(rel, m.get("records"), ids, rule, f"history[{m.get('period')}]")
        if hist.get("current_month") != months[-1].get("month"):
            err(rel, f"history.current_month={hist.get('current_month')} 與最後一個月份 {months[-1].get('month')} 不一致")
        act = data.get("actual")
        if isinstance(act, dict):
            check_records(rel, act.get("records"), ids, rule, f"actual[{act.get('period')}]")
            if act.get("period") != hist.get("current_period"):
                err(rel, f"actual.period「{act.get('period')}」與 history.current_period「{hist.get('current_period')}」不一致")
        same = rule.get("same_period_as")
        if same and (ROOT / same).exists():
            other = json.loads(read(same))
            if other.get("current_period") != hist.get("current_period"):
                err(rel, f"資料期間「{hist.get('current_period')}」與 {same} 的「{other.get('current_period')}」不一致")
        print(f"  {'✔' if len(errors) == n0 else '✘'} {rel}：{len(months)} 個月份，最新 {hist.get('current_period')}，每月 {len(months[-1].get('records') or [])} 筆")


# ── 三、CSV 資料檔 ───────────────────────────────────────────
def check_csv():
    for rel, rule in RULES.get("csv", {}).items():
        if not (ROOT / rel).exists():
            err(rel, "檔案不存在")
            continue
        n0 = len(errors)
        rows = list(csv.DictReader(io.StringIO(read(rel))))
        cols = list(rows[0].keys()) if rows else []
        miss = [c for c in rule.get("required_columns", []) if c not in cols]
        if miss:
            err(rel, f"缺少欄位 {miss}")
        lo, hi = rule.get("rows_min", 1), rule.get("rows_max", 10 ** 7)
        if not lo <= len(rows) <= hi:
            err(rel, f"資料 {len(rows)} 筆，應介於 {lo}～{hi} 筆")
        for c in rule.get("single_value_columns", []):
            vals = sorted({(r.get(c) or "").strip() for r in rows})
            if len(vals) > 1:
                err(rel, f"欄位「{c}」應該只有一個值，實際有 {vals[:5]}")
        for c in rule.get("numeric_columns", []):
            bad = [i + 2 for i, r in enumerate(rows) if (r.get(c) or "").strip() not in ("",) and
                   not re.fullmatch(r"-?[\d,]+(\.\d+)?", (r.get(c) or "").strip())]
            if bad:
                err(rel, f"欄位「{c}」有非數字資料，第 {bad[:5]} 列")
        print(f"  {'✔' if len(errors) == n0 else '✘'} {rel}：{len(rows)} 筆，{len(cols)} 欄")


# ── 四、網頁內嵌資料陣列（v1.1）────────────────────────────────
def check_embedded():
    for rel, rule in RULES.get("embedded", {}).items():
        if not (ROOT / rel).exists():
            err(rel, "檔案不存在")
            continue
        n0 = len(errors)
        html = read(rel)
        var = rule.get("var", "RAW")
        m = re.search(r"\b(?:var|let|const)\s+%s\s*=\s*" % re.escape(var), html)
        if not m:
            err(rel, f"找不到內嵌資料 {var} = [...]")
            continue
        try:
            rows, _ = json.JSONDecoder().raw_decode(html[m.end():])
        except ValueError as e:
            err(rel, f"{var} 無法解析成 JSON：{e}")
            continue
        if not isinstance(rows, list):
            err(rel, f"{var} 不是陣列")
            continue
        lo, hi = rule.get("rows_min", 1), rule.get("rows_max", 10 ** 7)
        if not lo <= len(rows) <= hi:
            err(rel, f"{var} 有 {len(rows)} 筆，應介於 {lo}～{hi} 筆")
        for k in rule.get("required_keys", []):
            lack = [i for i, r in enumerate(rows) if not isinstance(r, dict) or k not in r]
            if lack:
                err(rel, f"{var} 有 {len(lack)} 筆缺少欄位「{k}」（第 {lack[:5]} 筆；欄位名稱可能被改掉）")
        for k in rule.get("numeric_keys", []):
            bad = [i for i, r in enumerate(rows) if isinstance(r, dict) and r.get(k) not in (None, "")
                   and not isinstance(r.get(k), (int, float))
                   and not re.fullmatch(r"-?[\d,]+(\.\d+)?", str(r.get(k)).strip())]
            if bad:
                err(rel, f"{var} 欄位「{k}」有非數字資料，第 {bad[:5]} 筆")
        print(f"  {'✔' if len(errors) == n0 else '✘'} {rel}：{var} {len(rows)} 筆")


def main():
    print(f"檢查資料夾：{ROOT}")
    check_pages()
    check_kpi()
    check_csv()
    check_embedded()
    print(f"  網頁 {len(RULES.get('pages', {}))} 個已檢查")
    for w in warnings:
        print(w)
    for e in errors:
        print(e)
    if errors:
        print(f"\n共 {len(errors)} 項錯誤 → 擋下部署，網站維持上一版。")
        sys.exit(1)
    print(f"\n全部通過（警告 {len(warnings)} 項）。")


if __name__ == "__main__":
    main()
