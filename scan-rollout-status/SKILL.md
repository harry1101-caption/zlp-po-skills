---
name: scan-rollout-status
description: Quét group Teams "[UM] Rollout status" tìm các lần mở / tăng / rollback % rollout feature UM (iOS / Android / ZPI / ZMP / H5), đối chiếu với page Confluence "[UM][Data] Rollout" và ticket tracking trong epic rollout, rồi cập nhật dòng của từng feature trên Confluence (Rollout hiện tại, Cần follow, status, Đề xuất action) + comment timeline vào ticket. Dùng khi người dùng nói "scan rollout", "update rollout status", "cập nhật page rollout", "rollout hôm nay có gì mới", "sync rollout Teams lên Confluence".
---

# Scan rollout status → update Confluence

Mục tiêu: page Confluence luôn khớp với những gì **đã thực sự mở** trong Teams. Ticket tracking chỉ để nắm timeline + status, không phải requirement.

## Cấu hình
Mọi ID nằm trong `rollout.local.json` (gitignore) cùng thư mục — `cp rollout.local.example.json rollout.local.json` rồi điền. **Đọc file này đầu tiên** để lấy giá trị.

| | Ở đâu |
|---|---|
| Teams | group **[UM] Rollout status** — `teams_chat_messages` với `teams_chat_id` (tìm theo tên thường không ra, luôn dùng id) |
| Confluence | **[UM][Data] Rollout** — `page_id`. Bảng chính là bảng có header `Jira / Flag \| Scope \| PIC \| Rollout hiện tại \| Cần follow \| Đề xuất action` |
| Jira | epic `epic_key` — JQL `"Epic Link" = <epic_key>`; mỗi feature 1 Story, assignee `assignee` |
| Script | `rollout_page.py` (cùng thư mục): `fetch` / `rows` / `patch` / `put` — chỉ sửa đúng dòng được match, kiểm số dòng, kiểm version trước khi PUT |

## Quy trình

### 1. Đọc trạng thái hiện tại
- `confluence_get_page` page `page_id` format `storage` — ghi lại **version**, và từ cột "Cần follow" lấy mốc thời gian mới nhất đã ghi cho từng feature.
- Jira: `jira_search` epic `epic_key` (summary, status) để biết feature nào đã có ticket tracking.

### 2. Quét Teams
- `teams_chat_messages` `teams_chat_id`, `since_days` = từ mốc mới nhất trên page tới nay (mặc định 7, tối đa 60), `limit` 200.
- Giờ trong tool là UTC → **cộng 7h** ra giờ VN, ghi dạng `dd/MM HH:mm`.
- Tin dạng reply có trích tin gốc ở đầu body (tên người + nội dung cũ rồi mới tới câu trả lời) → phần sau cùng là nội dung mới.
- Phân loại từng tin:
  | Loại | Dấu hiệu | Ghi lên page? |
  |---|---|---|
  | **Confirm mở/tăng** | người mở config: "đã mở X%", "rollout … X%", "đã lên 50%", "ok a" trả lời request | Có — đây là số thật |
  | **Rollback / giảm / off** | "rollback", "off", "tắt", "về 0%" | Có |
  | **Request** | PO/QC: "nhờ mở…", "giúp em rollout…" | Có, ghi "X request …"; % hiện tại KHÔNG đổi tới khi có confirm |
  | **Prod deploy / fix bug / whitelist-blacklist** | "đã lên Prod…", "xoá blacklist…", "remove whitelist…" | Có (timeline), không đổi % |
  | Hỏi đáp, cảm ơn, test STG | | Không (chỉ dùng làm ngữ cảnh) |
- Mỗi sự kiện rút ra: ngày giờ VN, feature, ticket (link jira trong tin hoặc tin được reply), platform (iOS/Android/ZPA = iOS+Android, ZPI, ZMP, H5), %, ai làm, ghi chú (app version, điều kiện).

### 3. Map sự kiện → dòng trên page
- Ưu tiên theo **Jira key** (ticket tracking hoặc ticket feature trong tin); không có thì theo tên feature ↔ cột Scope.
- Feature chưa có dòng → đề xuất **dòng mới**.
- Không chắc map vào dòng nào → hỏi người dùng, đừng đoán.
- Dòng khác trên page lệch với Teams (vd % cũ hơn) → **báo người dùng**, không tự sửa dòng không có sự kiện mới.

### 4. Cho người dùng xem trước (1 bảng)
`Feature | Sự kiện mới (giờ VN, ai, platform, %) | Rollout hiện tại: cũ → mới | Status | Jira`
kèm danh sách: dòng mới, feature chưa có ticket tracking, chỗ lệch. Người dùng đã nói "scan rồi update" thì cứ ghi Confluence luôn sau bảng này; tạo ticket Jira mới thì **hỏi trước**.

### 5. Ghi Confluence (chỉ dòng có thay đổi)
- Page dài (~25k+ ký tự) → dùng script + curl, không gõ lại cả body. **Xin phép người dùng** rồi mới gọi `zp_cookie_header` site `confluence`; ghi cookie ra file tạm trong scratchpad, **xoá ngay sau khi PUT**.
  ```bash
  P=<thư mục skill>/rollout_page.py
  python3 $P fetch <cookie> page.json        # in version
  python3 $P rows page.json                  # xem idx | jira | status | scope | rollout | follow cuối
  python3 $P patch page.json changes.json new.json
  python3 $P put <cookie> new.json <version> "Scan rollout dd/MM"
  ```
  Không có quyền cookie → fallback `confluence_update_page` với body = nội dung `new.json` (fetch lại ngay trước khi ghi, version phải như cũ).
- `changes.json` (xem docstring script; `match` = Jira key hoặc đoạn text cột Scope):
  - `rollout_html`: thay cả ô, dạng `<ul><li>iOS/Android: <strong>10%</strong></li><li>ZPI: 0%</li></ul>` — liệt kê đủ mọi platform trong scope.
  - `follow_append`: thêm bullet timeline `<strong>dd/MM HH:mm</strong>: <ai> <làm gì> (<platform> <x%>)`; giữ nguyên bullet cũ.
  - `status`: `IN PROGRESS` khi còn platform trong scope < 100%; `DONE` khi 100% mọi platform trong scope (hoặc flag đã remove); `ROLLBACK` (đỏ) khi vừa rollback.
  - `action_html`: chỉ sửa khi sự kiện mới làm đổi việc cần làm (vd vừa lên 50% → "Monitor SR sau 50% rồi lên 100%").
  - Dòng mới: `{"new": true, "jira": "<ticket tracking hoặc ticket feature>", "scope": ..., "rollout_html": ..., "follow_append": [...], "action_html": ...}`.
- Script báo `match ra N dòng` / `version khác` → dừng, fetch lại, không ép ghi.
- Sau khi ghi: `rows` trên bản mới fetch về, đối chiếu mọi dòng khác **y nguyên** như trước.

### 6. Jira (ticket tracking)
- Feature có ticket trong epic → `jira_add_comment` bảng wiki:
  ```
  ||Ngày||Platform||%||Ghi chú||
  |dd/MM HH:mm|iOS + Android|5%|<người mở> mở, <người request> request HH:mm|
  Hiện tại: iOS/Android 5% • ZMP/H5 chưa live
  ```
- Feature chưa có ticket → hỏi người dùng có tạo không. Tạo thì: Story trong sprint đang active, epic `epic_key`, assignee `assignee`, title `[<Feature>][BE] Rollout <tên>`, description 3–4 dòng (mục đích tracking, link ticket feature/config, nguồn Teams), link **Relates** tới ticket feature. KHÔNG dùng Change Request Template / Requirement / AC. Tạo xong cập nhật cột Jira trên page sang macro ticket tracking.

### 7. Báo lại
Ngắn: số feature đã cập nhật, version page mới, comment Jira đã thêm, việc còn treo (request chưa có confirm, feature chưa có ticket, dòng lệch).

## Lưu ý
- Page có nhiều người sửa: luôn fetch ngay trước khi ghi; version nhảy > 1 sau khi ghi → diff với bản trước, khôi phục phần người khác vừa sửa nếu bị đè.
- Không gửi tin Teams trong skill này (chỉ đọc Teams).
- Platform: "ZPA" = app iOS + Android; ZPI/ZMP/H5 là web — ghi riêng.
