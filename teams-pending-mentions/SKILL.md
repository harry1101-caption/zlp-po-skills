---
name: teams-pending-mentions
description: Quét toàn bộ chat 1:1, group chat và channel Teams để tìm tin có tag/cc mình mà mình CHƯA react và CHƯA trả lời, rồi phân loại việc cần làm và soạn sẵn câu trả lời. Dùng khi người dùng nói "ai tag mình mà mình chưa rep", "tin nào cc mình còn sót", "check Teams xem còn nợ ai", "pending mentions", "messages I haven't answered", "what did people cc me on".
---

# Tin Teams tag mình mà chưa xử lý

Mục tiêu: một danh sách **việc cần làm** từ những tin đồng nghiệp tag/cc mình mà mình chưa react, chưa trả lời — không phải bản dump tin nhắn.

## Bước 1 — Quét

```
teams_chat_mentions(days=7, kind="all")          # mặc định: chỉ pending + spoke_after
```

- Người dùng nói "hôm nay"/"hôm qua" → `days=1`/`2`; "tuần này" → `7`; không nói → `7`.
- Muốn tính cả @everyone/@channel → `include_group_mentions=true` (mặc định tắt vì rất nhiễu).
- Có `note` chạm trần hội thoại → gọi lại với `max_conversations` lớn hơn.
- Lỗi hết phiên → `zp_login site="teamschat"` rồi gọi lại (không cần hỏi). HTTP 429 → đợi một lúc rồi thử lại.
- Tool chưa có trong danh sách → MCP `zalopay` chưa nạp bản mới: bảo người dùng `/mcp` → reconnect `zalopay`.

`status` trong kết quả:

| status | nghĩa | xử lý |
|---|---|---|
| `pending` | chưa react, chưa nhắn gì sau đó | **chắc chắn còn nợ** |
| `spoke_after` | group chat: mình có nhắn sau nhưng không quote tin đó | đọc `my_next_message` — nếu nó trả lời đúng ý tin tag thì bỏ; không rõ thì `teams_chat_messages(conversation=<id>, since_days=…)` đọc đoạn quanh đó |
| `reacted` / `replied` | đã xử lý | chỉ có khi `pending_only=false` |

## Bước 2 — Lọc và phân loại

Bỏ khỏi danh sách:
- `spoke_after` mà tin kế của mình rõ ràng đã trả lời / đã nhận việc.
- Tin chỉ cc để biết (FYI, "cc anh X", thông báo đã xong) không hỏi gì, không nhờ gì — gom vào mục "FYI" một dòng, không tính là việc.
- Tin mà người khác trong group đã trả lời thay và người hỏi đã OK (đọc ngữ cảnh khi nghi ngờ).

Phân loại phần còn lại:
- **🔴 Cần trả lời / quyết định** — câu hỏi trực tiếp, xin confirm, chờ mình approve/rollout/deploy.
- **🟡 Việc được nhờ** — nhờ check log, review, tạo ticket, gửi file… (ghi rõ việc cụ thể).
- **⚪ FYI** — chỉ cần react 👍 cho người gửi biết đã đọc.

Ưu tiên trong mỗi nhóm: cũ nhất trước (`age_hours` lớn), 1:1 trước group.

## Bước 3 — Trình bày

Bảng gọn, mỗi việc một dòng — không chép nguyên tin:

| # | Ưu tiên | Ở đâu | Ai | Khi nào | Họ cần gì | Đề xuất |
|---|---|---|---|---|---|---|
| 1 | 🔴 | [UM] Face Auth | Tên A. Nguyễn (8) | 19/11 17:00 (~1 ngày) | file .so production TrueID — hỏi có dùng ngay không | Trả lời: … |

- "Họ cần gì" ≤ 1 câu, tự tóm ý, giữ nguyên issue key / uid / link.
- "Đề xuất": câu trả lời nháp ngắn (theo văn phong Teams của người dùng — skill `teams-writing-style` nếu có) hoặc việc cần làm trước (vd "check log rồi rep").
- Cuối bảng: một dòng tổng — `N việc cần xử lý · M FYI · đã quét K hội thoại / D ngày`.
- Đây là nội dung hội thoại riêng: chỉ đưa phần cần cho việc, không dán cả đoạn chat.

## Bước 4 — Hành động (chỉ khi người dùng chọn)

Không tự gửi gì. Người dùng chọn "rep #1, #3" → làm theo skill `send-teams-message` (nếu có):
- Gửi **vào đúng hội thoại** `conversation_id` của tin đó (channel: trả lời trong thread `thread_root_id`).
- In nội dung + tên hội thoại, **chờ xác nhận** rồi mới `teams_chat_send`; giữ footer `✨ (tin nhắn này do AI gửi)`.
- Việc cần tra cứu (log, Jira, CS Tool…) → làm xong rồi mới soạn câu trả lời có kết quả.
- Việc cần tạo ticket → skill [create-jira-task](../create-jira-task/SKILL.md).

## Giới hạn cần biết

- "Đã trả lời" trong group chat chỉ chắc khi mình **quote** tin đó; nhắn trả lời không quote sẽ ra `spoke_after` → phải tự xét.
- Chỉ quét hội thoại có hoạt động trong cửa sổ `days` (tối đa 30 ngày) và tối đa `max_conversations` (≤120).
- Tag qua tên nhóm/tag Teams (`@UM-BE`) chỉ tính khi `include_group_mentions=true`.
