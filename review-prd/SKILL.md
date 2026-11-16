---
name: review-prd
description: Review một PRD (Confluence) của team UM trước khi đưa cho dev/QC — dựng inventory màn hình / input / popup / message / data / điều kiện / limit, chấm theo 13 tiêu chí rút ra từ các case QC & dev phải hỏi lại PO ở dự án Revamp Login/Register, rồi trả về scorecard + danh sách câu hỏi PO cần chốt (kèm vị trí trong PRD và đề xuất mặc định). Dùng khi người dùng nói "review PRD này", "đánh giá PRD X", "PRD này còn thiếu case gì", "check PRD trước khi grooming", "soát PRD để QC/dev đỡ hỏi lại".
---

# Review PRD trước khi giao dev/QC

Mục tiêu: tìm **trước** những chỗ mà dev (đặc biệt dev dùng AI đọc PRD + Figma) và QC sẽ phải hỏi lại PO. Dev giờ code theo PRD bằng AI — chỗ nào PRD im lặng, AI sẽ **tự đoán** (ví dụ: không nhắc tới popup sinh trắc cũ ⇒ AI hiểu là xoá). Mỗi chỗ im lặng = một vòng bug → hỏi PO → sửa → retest.

Tiêu chí chi tiết + bằng chứng: [references/criteria.md](references/criteria.md).
Case gốc từ dự án Login: [references/login-lessons.md](references/login-lessons.md).

## Input

- Link / page id Confluence của PRD (bắt buộc). Đọc bằng `mcp__zalopay__confluence_get_page` — lấy `format: "storage"` khi cần đọc đúng bảng, `text` để đọc nhanh. Đọc cả page con (`confluence_get_children`) nếu PRD tách UC ra page riêng.
- Tuỳ chọn: link Figma, epic/story Jira, PRD liên quan mà PRD này "Ref" tới (SMS OTP, Face Authen, Reset PIN…). PRD tham chiếu tới PRD khác thì đọc luôn phần được tham chiếu — gap hay nằm ở chỗ nối giữa 2 PRD.
- Nếu là bản revamp của flow đang chạy: hỏi / tìm PRD bản cũ hoặc hành vi production hiện tại để làm tiêu chí C4 (delta).

## Quy trình

1. **Đọc PRD, ghi version + người sửa cuối.** PO hay sửa song song — kết quả review phải gắn với version đã đọc.
2. **Dựng inventory** (bảng nội bộ, không cần in hết ra):
   - Màn hình / tray / popup / toast, theo từng UC.
   - Input field (SĐT, PIN, OTP, text…).
   - CTA (chính / phụ / back / X / link).
   - Message (inline lỗi, popup, toast) — kèm ai sinh ra (FE hay BE).
   - Data hiển thị về user (tên, SĐT, avatar, trạng thái…).
   - Điều kiện rẽ nhánh (flag, K-level, device mới, có bio/Smart OTP…).
   - Limit / rate limit / countdown / TTL.
   - API được gọi ở mỗi bước.
3. **Chấm từng tiêu chí C1–C13** trong `criteria.md` trên inventory. Với mỗi phần tử, hỏi đúng các câu kiểm tra của tiêu chí. Kết luận mỗi tiêu chí: **Đủ / Mơ hồ / Thiếu / Không áp dụng**.
4. **Viết câu hỏi cho PO** cho mỗi chỗ Mơ hồ/Thiếu. Mỗi câu hỏi:
   - Vị trí trong PRD (UC / dòng bảng / màn).
   - Câu hỏi cụ thể, trả lời được bằng 1 quyết định (không hỏi chung chung "còn thiếu case không?").
   - **Đề xuất mặc định** — PO chỉ cần gật hoặc sửa. Lấy đề xuất từ: hành vi production hiện tại, flow anh em đã chốt (vd "giống Reset PIN v2"), quyết định PO đã chốt ở Login (xem `login-lessons.md`).
   - Mức ảnh hưởng: **Cao** (sai logic / bảo mật / tạo account sai / gửi OTP thừa), **TB** (copy, data hiển thị, feedback), **Thấp** (layout).
5. **Soát chéo trước khi trả kết quả** (bài học từ PRD Unbind 12/11/2026 — vòng đầu bỏ sót 3 điểm có sẵn từ đầu):
   - Với mỗi limit / bộ đếm / TTL của PRD tham chiếu (vd Reset PIN v2 "3 lần/ngày"): flow mới có làm user tiêu tốn lượt không?
   - Với mỗi bộ đếm / timer trong PRD: bắt đầu khi nào, reset khi nào, hết hạn giữa chừng thì sao?
   - Với mỗi nhánh thất bại: user đứng ở màn nào (màn của PRD này hay result page của PRD cha)?
   - Với mỗi nền tảng trong scope: hành động có phá chính môi trường đang chạy không (vd gỡ liên kết Zalo trong ZMP)?
6. **Khi PO chốt từng điểm** (vòng sửa PRD): sau mỗi lượt cập nhật, kiểm lại quyết định mới với các edge case / quyết định đã có — một quyết định thường sinh 1 câu hỏi mới ở chỗ giao nhau (vd thêm TTL → hết hạn giữa chừng thì sao). Báo ngay trong lượt đó, đừng dồn tới lúc tổng hợp.
7. **Tự kiểm**: mỗi câu hỏi có trỏ đúng chỗ trong PRD không; có câu nào PRD thực ra đã trả lời (tìm lại bằng từ khoá) thì bỏ. Không bịa hành vi production — không chắc thì ghi "cần PO/dev xác nhận hành vi hiện tại".

## Output

Trả lời bằng tiếng Việt, theo thứ tự:

1. **Tóm tắt 2–3 dòng**: PRD nào, version mấy, mức sẵn sàng (Sẵn sàng / Cần chốt N điểm trước grooming / Chưa sẵn sàng), số câu hỏi theo mức Cao/TB/Thấp.
2. **Scorecard** — bảng: `Tiêu chí | Kết quả | Số điểm cần chốt | Ví dụ nặng nhất`.
3. **Câu hỏi cần PO chốt** — bảng, sắp theo mức ảnh hưởng: `# | Mức | Vị trí PRD | Câu hỏi | Đề xuất mặc định | Tiêu chí`.
4. (Nếu có) **Mâu thuẫn** giữa PRD ↔ Figma ↔ PRD tham chiếu ↔ AC trong Jira — liệt kê riêng, vì đây là nguồn bug "QC theo PRD, dev theo Figma".

Không in lại nội dung PRD. Không liệt kê phần đã đủ (scorecard đã thể hiện).

## Ranh giới

- Chỉ đọc. **Không** sửa Confluence, không comment lên page, không tạo Jira, không nhắn Teams — trừ khi người dùng bảo rõ. Nếu được bảo cập nhật PRD: đọc lại version mới nhất ngay trước khi ghi (PO sửa song song) và chỉ sửa đoạn liên quan.
- PRD rất dài / nhiều page con: có thể giao worker (tài khoản 2, xem CLAUDE.md) đọc và trích inventory, nhưng phần chấm tiêu chí và viết câu hỏi do boss làm và phải đối chiếu lại PRD.
- Khi một PRD mới phát sinh thêm loại câu hỏi QC/dev chưa có trong `criteria.md`, đề xuất với người dùng bổ sung tiêu chí (kèm case làm bằng chứng) — bộ tiêu chí phải lớn dần theo thực tế.
