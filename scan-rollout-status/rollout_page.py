#!/usr/bin/env python3
"""Đọc / sửa bảng rollout trên page Confluence theo dõi rollout, ở dạng storage.
Cấu hình (base_url, page_id, jira_server_id) đọc từ rollout.local.json cùng thư mục.

  fetch <cookie_file> <out.json>          GET page (body.storage + version) → out.json
  rows  <page.json>                       in các dòng: idx | jira | status | scope | rollout | follow cuối
  patch <page.json> <changes.json> <out.json>   áp thay đổi, chỉ đụng dòng được match; in diff tóm tắt
  put   <cookie_file> <out.json> <expect_version> [comment]   PUT nếu version trên server == expect_version

changes.json = mảng:
  {"match": "PROJ-123" | "<đoạn text trong cột Scope>",
   "rollout_html": "<ul><li>iOS/Android: <strong>10%</strong></li></ul>",   (tuỳ chọn, thay cả ô)
   "follow_append": ["<strong>21/11 10:20</strong>: <người mở> mở 10% iOS/Android"],  (tuỳ chọn, thêm bullet)
   "action_html": "...",                      (tuỳ chọn, thay cả ô)
   "status": "IN PROGRESS" | "DONE"}          (tuỳ chọn)
  {"new": true, "jira": "PROJ-456", "status": "IN PROGRESS", "scope": "...", "rollout_html": "...",
   "follow_append": [...], "action_html": "..."}   → thêm dòng cuối bảng
"""
import json, re, sys, html, urllib.request, uuid

import os
_CFG_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "rollout.local.json")
try:
    _CFG = json.load(open(_CFG_PATH))
except FileNotFoundError:
    sys.exit(f"thiếu {_CFG_PATH} — copy rollout.local.example.json rồi điền")
BASE = _CFG["confluence_base_url"].rstrip("/")
PAGE = str(_CFG["page_id"])
SERVER_ID = _CFG["jira_server_id"]
COLOUR = {"DONE": "Green", "IN PROGRESS": "Blue", "ON HOLD": "Yellow", "ROLLBACK": "Red"}


def req(cookie_file, method, url, data=None):
    cookie = open(cookie_file).read().strip()
    r = urllib.request.Request(url, method=method, data=data,
        headers={"Cookie": cookie, "Content-Type": "application/json", "X-Atlassian-Token": "no-check"})
    with urllib.request.urlopen(r, timeout=60) as f:
        return json.loads(f.read())


def fetch(cookie_file, out):
    j = req(cookie_file, "GET", f"{BASE}/rest/api/content/{PAGE}?expand=body.storage,version")
    json.dump({"title": j["title"], "version": j["version"]["number"], "body": j["body"]["storage"]["value"]},
              open(out, "w"), ensure_ascii=False)
    print(f"version {j['version']['number']}, {len(j['body']['storage']['value'])} ký tự")


def main_table(body):
    # bảng rollout = bảng cuối có header "Jira / Flag"
    i = body.rfind("<th>Jira / Flag</th>")
    if i < 0: sys.exit("không thấy bảng 'Jira / Flag'")
    tb0 = body.index("<tbody>", i) + len("<tbody>")
    tb1 = body.index("</tbody>", tb0)
    return tb0, tb1


def split_rows(body):
    tb0, tb1 = main_table(body)
    inner = body[tb0:tb1]
    rows, pos = [], 0
    for m in re.finditer(r"<tr>(.*?)</tr>", inner, re.S):
        rows.append((tb0 + m.start(), tb0 + m.end(), m.group(1)))
    return rows


def cells(tr_inner):
    return re.findall(r"<td[^>]*>(.*?)</td>", tr_inner, re.S)


def text(s):
    s = re.sub(r"<li>", " • ", s)
    s = re.sub(r"<[^>]+>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(s)).strip()


def jira_key(c0):
    m = re.search(r'ac:name="key">([A-Z]+-\d+)<', c0) or re.search(r"([A-Z]+-\d+)", text(c0))
    return m.group(1) if m else "—"


def status_of(c0):
    m = re.search(r'ac:name="title">([^<]+)</ac:parameter></ac:structured-macro>', c0)
    return m.group(1) if m else ""


def rows_cmd(page):
    body = json.load(open(page))["body"]
    for i, (_, _, tr) in enumerate(split_rows(body)):
        c = cells(tr)
        if len(c) < 6: print(i, "?? dòng lạ", text(tr)[:80]); continue
        last = re.findall(r"<li>(.*?)</li>", c[4], re.S)
        print(f"{i:2} | {jira_key(c[0])} | {status_of(c[0]) or '-'} | {text(c[1])[:45]} | {text(c[3])[:50]} | {text(last[-1] if last else c[4])[:70]}")


def status_macro(title):
    return (f'<ac:structured-macro ac:name="status" ac:schema-version="1" ac:macro-id="{uuid.uuid4()}">'
            f'<ac:parameter ac:name="colour">{COLOUR.get(title, "Grey")}</ac:parameter>'
            f'<ac:parameter ac:name="title">{title}</ac:parameter></ac:structured-macro>')


def jira_macro(key):
    return (f'<ac:structured-macro ac:name="jira" ac:schema-version="1" ac:macro-id="{uuid.uuid4()}">'
            f'<ac:parameter ac:name="server">Jira</ac:parameter><ac:parameter ac:name="serverId">{SERVER_ID}</ac:parameter>'
            f'<ac:parameter ac:name="key">{key}</ac:parameter></ac:structured-macro>')


def set_status(c0, title):
    pat = r'<ac:structured-macro ac:name="status".*?</ac:structured-macro>'
    if re.search(pat, c0, re.S):
        return re.sub(pat, status_macro(title), c0, count=1, flags=re.S)
    if "</div>" in c0:
        return c0.replace("</div>", f"<p>{status_macro(title)}</p></div>", 1)
    return f'<div class="content-wrapper"><p>{c0}</p><p>{status_macro(title)}</p></div>'


def append_follow(c4, items):
    lis = "".join(f"<li>{x}</li>" for x in items)
    if "</ul>" in c4:
        k = c4.rfind("</ul>")
        return c4[:k] + lis + c4[k:]
    old = c4.strip()
    if old in ("", "<br />"):
        return f'<div class="content-wrapper"><ul>{lis}</ul></div>'
    if old.endswith("</div>"):
        return old[:-6] + f"<ul>{lis}</ul></div>"
    return f'<div class="content-wrapper"><p>{old}</p><ul>{lis}</ul></div>'


def patch_cmd(page, changes, out):
    pj = json.load(open(page)); body = pj["body"]
    rows = split_rows(body)
    edits = []  # (start, end, new_tr)
    new_rows = []
    for ch in json.load(open(changes)):
        if ch.get("new"):
            c0 = f'<div class="content-wrapper"><p>{jira_macro(ch["jira"]) if ch.get("jira") else "&mdash;"}</p><p>{status_macro(ch.get("status", "IN PROGRESS"))}</p></div>'
            c4 = append_follow("", ch.get("follow_append", []))
            new_rows.append(f'<tr><td>{c0}</td><td>{ch["scope"]}</td><td><br /></td><td>{ch.get("rollout_html", "")}</td><td>{c4}</td><td>{ch.get("action_html", "")}</td></tr>')
            print(f"+ dòng mới: {ch.get('jira', '—')} | {text(ch['scope'])}")
            continue
        m = ch["match"]
        hits = [r for r in rows if (jira_key(cells(r[2])[0]) == m) or (m.lower() in text(cells(r[2])[1]).lower())]
        if len(hits) != 1:
            sys.exit(f"match '{m}' ra {len(hits)} dòng — cần đúng 1. Dừng, chưa ghi gì.")
        s, e, tr = hits[0]
        tds = re.findall(r"(<td[^>]*>)(.*?)(</td>)", tr, re.S)
        c = [list(t) for t in tds]
        if "status" in ch: c[0][1] = set_status(c[0][1], ch["status"])
        if "rollout_html" in ch: c[3][1] = ch["rollout_html"]
        if ch.get("follow_append"): c[4][1] = append_follow(c[4][1], ch["follow_append"])
        if "action_html" in ch: c[5][1] = ch["action_html"]
        edits.append((s, e, "<tr>" + "".join("".join(t) for t in c) + "</tr>"))
        print(f"~ {m}: " + ", ".join(k for k in ("status", "rollout_html", "follow_append", "action_html") if k in ch))
    for s, e, new in sorted(edits, reverse=True):
        body = body[:s] + new + body[e:]
    if new_rows:
        _, tb1 = main_table(body)
        body = body[:tb1] + "".join(new_rows) + body[tb1:]
    before, after = len(split_rows(pj["body"])), len(split_rows(body))
    assert after == before + len(new_rows), "số dòng lệch — dừng"
    pj["body"] = body
    json.dump(pj, open(out, "w"), ensure_ascii=False)
    print(f"OK: {before} → {after} dòng, ghi {out}")


def put_cmd(cookie_file, out, expect, comment="Update rollout status"):
    pj = json.load(open(out))
    cur = req(cookie_file, "GET", f"{BASE}/rest/api/content/{PAGE}?expand=version")["version"]["number"]
    if cur != int(expect):
        sys.exit(f"version trên server là {cur}, khác {expect} — có người vừa sửa. Fetch lại rồi patch lại.")
    data = json.dumps({"id": PAGE, "type": "page", "title": pj["title"],
        "version": {"number": cur + 1, "message": comment},
        "body": {"storage": {"value": pj["body"], "representation": "storage"}}}).encode()
    j = req(cookie_file, "PUT", f"{BASE}/rest/api/content/{PAGE}", data)
    print(f"đã ghi version {j['version']['number']}")


if __name__ == "__main__":
    a = sys.argv
    if len(a) < 2: sys.exit(__doc__)
    {"fetch": lambda: fetch(a[2], a[3]), "rows": lambda: rows_cmd(a[2]),
     "patch": lambda: patch_cmd(a[2], a[3], a[4]),
     "put": lambda: put_cmd(a[2], a[3], a[4], *(a[5:6]))}.get(a[1], lambda: sys.exit(__doc__))()
