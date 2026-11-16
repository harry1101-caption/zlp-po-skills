# 13 tiêu chí review PRD

Rút ra từ group Teams "[UM] Login/ Register" (28/10–10/11/2026) và 43 bug Jira của Revamp Login/Register (story PCFUM-12557 Android, PCFUM-12685 iOS). Case cụ thể: `login-lessons.md` (mã L-xx).

Mức mặc định khi thiếu: **Cao** = dev đoán sai sẽ ra sai logic / bảo mật / side-effect (gửi OTP, tạo account, bật bio). **TB** = sai copy, data, feedback. **Thấp** = layout.

---

## C1. Rule của từng input field — Cao

Với **mỗi** ô nhập, PRD phải nói:
- Ký tự cho phép; có cho paste không; paste chuỗi có khoảng trắng / dấu `+` / tiền tố thì xử lý thế nào.
- Độ dài min / max; **vượt max thì chặn gõ hay cho gõ rồi báo lỗi** (2 cách này ra 2 UI khác nhau).
- Danh sách **các cách nhập tương đương** phải coi là cùng một giá trị (vd SĐT: `0383…`, `383…`, `84383…`, `840383…`, `+84 84…`).
- Chuẩn hoá do ai làm (FE hay BE) và FE có được tự thêm/bớt ký tự không.
- Hiển thị khi đang gõ: format nhóm số, prefix cố định hay xoá được, chuỗi dài hơn ô thì cuộn/cắt thế nào.
- CTA enable khi nào (rỗng / ≥1 ký tự / đủ độ dài).
- Lỗi hiện **lúc nào** (khi gõ / khi bấm CTA / khi BE trả) và **ẩn lúc nào**.

Red flag: chỉ ghi "validate SĐT hợp lệ"; ghi "max 12" mà không nói chặn hay báo lỗi; ví dụ hợp lệ chỉ có 1 dạng.
Bằng chứng: L-01, L-02, L-03.

## C2. Mọi lối thoát / huỷ / quay lại — Cao

Với **mỗi** màn, tray, popup, PRD phải nói điều gì xảy ra khi: bấm back, bấm X, bấm CTA phụ ("Đóng", "Để sau"), vuốt đóng, kill app / chuyển nền, quay lại bước đó lần nữa.
Mỗi lối thoát phải có: **màn đích**, **state giữ hay xoá** (số đã nhập, PIN đã tạo, OTP đang đếm), **side-effect** (có gửi OTP mới không, account đã tạo chưa, countdown chạy tiếp hay reset), và trong flow nhiều bước: **dừng giữa chừng thì coi như chưa làm gì**?
Red flag: chỉ mô tả happy path; "Ref flow OTP" mà không nói đóng OTP thì về đâu trong flow này.
Bằng chứng: L-04, L-05, L-06, L-07.

## C3. Bảng message: nội dung + chủ sở hữu + hình thức — TB (Cao nếu là lỗi bảo mật/limit)

Một bảng duy nhất: `trường hợp / mã lỗi → hình thức (inline, popup, toast, tray) → title / message / CTA → ai sinh ra (BE trả về hay FE hardcode)`.
- Không để "hiển thị lỗi theo BE" mà không có nội dung BE sẽ trả — dev FE sẽ đẩy sang BE, BE không biết copy, QC không có expected.
- Một thuật ngữ thống nhất (vd "mật khẩu" hay "PIN" — không trộn "Mã Pin", "Password"), một quy tắc dấu chấm cuối câu, đúng brand "Zalopay".
- PRD, Figma, PRD tham chiếu (SMS OTP, Face) **không được ra 3 câu khác nhau** cho cùng một lỗi. Nếu PRD là nguồn chuẩn thì ghi rõ "copy theo PRD, Figma chỉ minh hoạ".
- Title và body của cùng popup không mâu thuẫn nhau.
- Ảnh mockup nhúng trong PRD là **copy thật** (PO xác nhận 12/11/2026) — không yêu cầu chép lại thành bảng message. Chỉ flag trường hợp/màn **không có ảnh** nào thể hiện copy (vd popup lỗi mới thêm ở Edge case).
Bằng chứng: L-08, L-09, L-10.

## C4. Delta so với production: giữ / đổi / bỏ — Cao

PRD revamp một flow đang chạy phải có mục **"Hành vi hiện tại → quyết định"** cho mọi hành vi hiện có: popup, banner, toast, bước phụ, tracking.
- Mỗi dòng: Giữ nguyên / Đổi thành… / Bỏ.
- Phạm vi áp dụng: chỉ flow mới (sau flag) hay cả flow cũ.
Lý do: dev dùng AI đọc PRD — hành vi không được nhắc tới sẽ bị **coi là thừa và xoá**, hoặc được giữ mà không ai biết.
Red flag: PRD chỉ mô tả màn mới; không nhắc flag rollout; Figma thiếu một thành phần đang có trên production.
Bằng chứng: L-11, L-12.

## C5. Phản hồi cho từng kết quả, kể cả khi nhiều kết quả xảy ra cùng lúc — TB

Với mỗi kết quả (thành công, thất bại, bật thêm tính năng, đăng xuất…): có feedback gì (toast / popup / không gì cả), copy, vị trí, thời lượng, hiện trên màn nào (trước hay sau khi chuyển màn).
**Bắt buộc** có rule khi 2 kết quả đến cùng lúc (vd đăng nhập thành công + bật sinh trắc): 2 toast nối nhau hay gộp 1.
Bằng chứng: L-13, L-14.

## C6. Từ điển dữ liệu hiển thị — TB

Mỗi dữ liệu về user hiện trên UI: **nguồn** (API + field), **format** (in hoa / Title Case, nhóm số, mask), **fallback khi rỗng**, và **phải giống nhau ở những màn nào**.
Red flag: "hiển thị tên user" mà không nói tên nào (eKYC / profile / Zalo); không nói user chưa có tên thì hiện gì.
Bằng chứng: L-15, L-16, L-17.

## C7. Bảng quyết định cho UI có điều kiện — Cao

Khi UI phụ thuộc ≥2 điều kiện (đã bật Smart OTP? đã bật bio? máy hỗ trợ bio? flag BE? K-level? device mới?): PRD phải có **bảng đủ tổ hợp** → hiện gì, ở **từng màn** (Login PIN, Welcome back, Confirm PIN có thể khác nhau). Thứ tự ưu tiên chung chung ("Smart OTP → Bio") là chưa đủ: cần nói áp dụng ở màn nào, điều kiện bật flag, copy cho từng biến thể.
Bằng chứng: L-18.

## C8. Thứ tự bước khớp với hợp đồng API — Cao

Sequence diagram / bảng bước phải khớp với API thật: field nào quyết định bước tiếp theo (vd `need_verify_phone`), token nào sinh ở bước nào, TTL bao lâu, đảo thứ tự bước thì token có hết hạn giữa chừng không, API lỗi / timeout ở mỗi bước thì về đâu.
Red flag: PRD đổi thứ tự bước mà không nhắc BE; không có mục lỗi API / timeout.
Bằng chứng: L-19.

## C9. Bảng limit một nguồn duy nhất — Cao

Mọi limit (rate limit, số lần sai, countdown, khoá tạm): **con số, cửa sổ thời gian, cách đếm, lúc reset, message, hình thức hiển thị**, và nguồn config. Khi limit đổi theo yêu cầu (sếp / risk) thì PRD phải cập nhật cùng lúc — CS và QC đọc PRD.
Red flag: PRD này nói "5 lần/15 phút", PRD tham chiếu nói "còn {n} lần thử", Figma nói khác.
Bằng chứng: L-20, L-21.

## C10. Trạng thái component & vệ sinh Figma — TB

- Mỗi component tương tác (ô PIN, CTA chính/phụ, ô OTP): trạng thái default / focus / đã nhập / lỗi / disabled / loading — hoặc trỏ tới component dùng chung ("giống Reset PIN v2").
- Quy tắc CTA chính / phụ (màu, vị trí) theo design system.
- Figma chỉ còn frame đúng phiên bản; frame cũ/thừa phải xoá hoặc đánh dấu — dev dùng AI đọc Figma sẽ code theo frame thừa.
Bằng chứng: L-22, L-23.

## C11. Cùng một hành vi cho iOS và Android — TB

Mọi rule phải viết dạng nền tảng-trung lập; chỗ nào cố ý khác nhau thì ghi rõ. Khi QC thấy 2 nền tảng làm khác nhau mà PRD không chốt, sẽ thành một vòng hỏi PO.
Bằng chứng: L-24.

## C12. Ràng buộc layout ở trường hợp biên — Thấp

Message dài 2 dòng, bàn phím mở/đóng, tray/bottom sheet thay đổi chiều cao, màn hẹp (320pt), cỡ chữ hệ thống lớn, toast đè nội dung/bàn phím. PRD/Figma nên nói: tối đa mấy dòng, phần nào được đẩy/che, tray giữ chiều cao cố định hay co giãn.
Bằng chứng: L-25.

## C13. Phạm vi & rollout — TB

Màn nào trong scope, màn nào thuộc team khác (chỉ load lên), tính năng nào để sprint sau; flag / version / % rollout; flow cũ còn chạy song song bao lâu. Thiếu phần này QC sẽ log bug cho màn ngoài scope và test nhầm flow cũ.
Bằng chứng: L-26.
