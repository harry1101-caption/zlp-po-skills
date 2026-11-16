# Case gốc — Revamp Login/Register ZPA (10–11/2026)

Nguồn: Teams group "[UM] Login/ Register", bug Jira của PCFUM-12557 (Android) / PCFUM-12685 (iOS), PRD `[UM][Main-flow][ZPA] Login` và `[UM][Main-flow] Register`.
Mỗi case: PRD thiếu gì → ai hỏi → PO chốt gì. Dùng cột "PO chốt" làm **đề xuất mặc định** khi gặp lại câu hỏi tương tự ở PRD khác.

| Mã | Tiêu chí | PRD thiếu / mơ hồ | Ai raise · ở đâu | PO chốt |
|---|---|---|---|---|
| L-01 | C1 | CTA "Tiếp tục" enable khi nào: PRD cũ "đủ 10 số", sau đổi "≥1 chữ số" nhưng Android vẫn làm theo bản cũ | Dev 28/10 (chat); QC PCFUM-12964 | Enable khi có ≥1 chữ số; BE validate khi bấm |
| L-02 | C1 | Các cách nhập SĐT tương đương: thiếu dạng `84399…` / `840…`; dev: "define kĩ đi bro, đừng có nghĩ" — user copy-paste đầu 84 là bình thường | Dev 28/10, 02/11 (chat); PCFUM-12807, 12799 | Ô hiển thị đúng như user gõ (có +84 cố định); BE chấp nhận `0…`, `…`, `84…`, `840…` và chuẩn hoá |
| L-03 | C1, C11 | Max length: PRD ghi "quá 12 số thì báo lỗi" nhưng không nói chặn gõ hay không → iOS không giới hạn, Android chặn cứng 10/11 | QC PCFUM-13008 | Max 12 ký tự, chặn gõ thêm, hiện lỗi + hiệu ứng rung |
| L-04 | C2 | Register: tạo PIN → xác nhận → OTP → user huỷ popup OTP thì về đâu, account đã tạo chưa? | Dev 05/11 (chat), PCFUM-12538 | Huỷ ⇒ về màn nhập SĐT; chưa xong flow = chưa tạo account |
| L-05 | C2 | Đóng tray OTP rồi vào lại trong 60s: gửi OTP mới hay chạy tiếp countdown? iOS hiện popup chặn, Android gửi OTP mới | QC PCFUM-12994, PCFUM-13005 | Đang chốt là đếm lại 60s mỗi lần vào (QC 10/11); popup iOS do BE |
| L-06 | C2 | Đăng xuất thì về Welcome back hay màn nhập SĐT | QC PCFUM-13050 | (mở) |
| L-07 | C2 | Back ở Welcome back | PRD v45 đã thêm: confirm dialog Đồng ý → nhập SĐT / Để sau → tắt popup | — |
| L-08 | C3 | Message PIN yếu: PRD 1 câu, Figma 1 câu, BE trả 1 câu — dev FE đẩy "BE driven, out scope", QC không có expected | PCFUM-12803, 12808, 13023, 13026#7 | Login: "Mật khẩu không đúng. Vui lòng thử lại"; Confirm: "Mật khẩu xác nhận không khớp"; Create: "Để tăng độ bảo mật cho mật khẩu, tránh sử dụng các số lặp (ví dụ: 999999)" |
| L-09 | C3, C9 | OTP sai & quá giới hạn: PRD SMS OTP v7 "Mã xác thực chưa đúng. Bạn còn {n} lần thử", Figma "…Vui lòng thử lại.", BE "…Vui lòng thực hiện lại." | PCFUM-12810, 12817, 13026#2 | "Mã xác thực OTP không đúng" (BE sửa) |
| L-10 | C3 | Popup "Không gửi được mã OTP" — body nói "đang được gửi" (tự mâu thuẫn); brand "ZaloPay" sai | PCFUM-13005, 12965 | BE sửa copy |
| L-11 | C4 | Banner sinh trắc ở màn Xác nhận PIN (register) có trên prod nhưng không có trong Figma/PRD → QC log bug; dev: bỏ thì user mới không bao giờ được mời bật Face ID | PCFUM-12805, 12809 | Giữ banner |
| L-12 | C4 | Popup "Bật xác thực sinh trắc" sau onboarding: PRD v2 không nhắc → "AI đang hiểu là dư, cần xoá"; toggle OFF có hiện popup không; áp dụng cho flow cũ không | Dev 04/11 (chat), PCFUM-12971, 13000 | Toggle OFF ⇒ không popup; chỉ áp dụng flow v2 |
| L-13 | C5 | Login PIN + toggle bio ON: toast "Đăng nhập thành công" và "Kích hoạt sinh trắc học thành công" — 1 hay 2? | PCFUM-13020, 13026#4, 13032 | Gộp: "Đăng nhập thành công. / Đã kích hoạt sinh trắc học" (2 dòng) |
| L-14 | C5, C12 | Toast "Đã đăng xuất thành công" đè bàn phím; toast đăng nhập đè link trên màn PIN (iOS) | PCFUM-13019, 13007 | Bỏ toast đăng xuất (UI đã thể hiện) |
| L-15 | C6 | Tên ở Login PIN vs Welcome back vs tab Tài khoản: tên eKYC / profile / Zalo; in hoa hay không | PCFUM-12820, 13006, 13025, chat 02/11 (PCFUM-12191) | Login PIN & WBS cùng format (Title Case từ tên eKYC — DB vẫn lưu in hoa vì đối tác cần khớp CCCD); tab Tài khoản làm ticket riêng |
| L-16 | C6 | Hint card khi account không có tên → SĐT hiện 2 lần | PCFUM-13021 | Closed as design |
| L-17 | C6 | Mask SĐT: tray OTP mask nhưng ô nhập phía sau vẫn hiện đủ số | Chat 05/11 | Chấp nhận (số do user tự gõ) |
| L-18 | C7 | Banner Smart OTP vs Bio: PRD chỉ ghi "ưu tiên Smart OTP → Face/Touch", không nói theo màn, không nói cờ `smart_otp_toogle`, không có copy banner Smart OTP | PCFUM-13010, 13011 | Ưu tiên Smart OTP → Bio (12/11); iOS đang để WBS bio trước, Confirm PIN chỉ bio — cần PO xác nhận theo màn |
| L-19 | C8 | Register đổi thứ tự Create PIN → Confirm → OTP, nhưng BE vẫn trả `need_verify_phone` ⇒ client đi OTP trước; TTL `send_otp_token` khi user mất thời gian tạo PIN chưa ai trả lời | PCFUM-13001, 13002 | Create PIN → Confirm → OTP |
| L-20 | C9 | Giới hạn nhập sai OTP: 17 lần liên tiếp không bị chặn; message limit hiện popup thay vì trong tray | PCFUM-12817 | (BE đang làm) |
| L-21 | C9 | Rate limit nhập SĐT đổi thành 5 lần/device/giờ & 20 lần/device/ngày theo yêu cầu, PRD chưa cập nhật → CS hỏi | Chat 09/11, PCFUM-12976 | PRD v45 đã cập nhật bảng Rate Limit |
| L-22 | C10 | Ô PIN sau lỗi: QC iOS expect "ô 1 focus, còn lại xám", QC Android expect "cả 6 viền xanh" — PRD không có rule | PCFUM-12808, 13022, chat 05/11 | Mặc định viền xanh như Reset PIN v2 |
| L-23 | C10 | Màu CTA popup "Dừng xác thực OTP?" (chính xanh / phụ xám); Figma còn frame thừa — dev dùng AI đọc Figma làm sai | Chat 05/11, 10/11; PCFUM-13026#1 | "Đóng" nền xanh, CTA đặt dưới đáy popup, giữ chiều cao; design dọn Figma |
| L-24 | C11 | iOS/Android khác nhau: max length, vị trí toast, gửi lại OTP, popup bio | PCFUM-13008, 13007, 12994/13005 | Chốt từng case |
| L-25 | C12 | Lỗi 2 dòng làm cắt banner / box "Lưu ý"; tray OTP nhảy khi bàn phím đóng mở; số bị cắt khi cỡ chữ hệ thống lớn; nút bị bàn phím che sau khi quay lại từ trang điều khoản | PCFUM-12802, 12804, 13018, 12999, 13009, 13026#1 | Lỗi OTP sai che SĐT: bỏ qua |
| L-26 | C13 | Form "Cung cấp chứng từ" (team khác), tab Tài khoản — QC log bug nhưng ngoài scope; fix chỉ áp dụng login v3 (`onboarding_ui = 2`) — QC test nhầm flow cũ | PCFUM-13024, 13025, 12971 | Closed as design / out of scope |

## Con số

- 43 bug Jira Login/Register tạo từ 01/10/2026; ~28 bug (khoảng 2/3) có nguyên nhân gốc là PRD/Figma chưa nói rõ hoặc mâu thuẫn — không phải dev code sai. Mỗi bug tốn ≥1 vòng hỏi PO + retest.
- Chat group 28/10–10/11: khoảng 12 lần dev/QC phải hỏi PO chốt rule.
