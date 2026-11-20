---
name: funnel-register
description: Funnel đăng ký tài khoản ZaloPay trên app (ZPA iOS/Android) kèm bước popup consent — đếm theo device_id/ngày, tuần tự từ chọn luồng đăng ký → load consent → accept consent → OTP → tạo PIN → xác nhận PIN → thành công, trên Superset. Dùng khi người dùng nói "lấy số funnel register", "funnel đăng ký", "SR register", "consent khi đăng ký ra sao", "popup consent đã rollout bao nhiêu".
---

# Funnel Register + Consent (ZPA)

Mục tiêu: theo dõi SR đăng ký mới trên app và tác động của popup consent (hiện sau khi hệ thống xác định SĐT là đăng ký mới, trước màn OTP).

## Nguồn
- Superset SQL Lab (MCP `zalopay`, tool `superset_sql`), database mặc định 28, schema `client_encrypt`, bảng `zpa_eventlog`, `screen_id='10'`.
- Đối chiếu bước OTP với BE: `check-otp-be.sql` (database_id=70, schema `um_encrypt`).

## Bước (device_id/ngày, tuần tự `ts >= bước trước`)
| | Event | Điều kiện | % so với |
|---|---|---|---|
| s1 | 01.1019.036 | `user_flow='registration'` | — |
| s2 | 01.1019.051 | load popup consent | s1 (= coverage popup) |
| s3 | 01.1019.056 | `$.CTA` IN ('agree_all','confirm') — chỉ tính accept, bỏ X | s2 |
| b4 | 01.1012.000 | `user_flow='registration by phone'` | s1 |
| b5 | 01.1012.043 | pass OTP | b4 |
| b6 | 01.1013.000 | tạo PIN | b5 |
| b7 | 01.1014.000 | xác nhận PIN | b6 |
| b8 | 01.1014.002 | `error` rỗng = đăng ký thành công | b7 |

SR = b8 / s1. `b*` không bắt buộc đi qua consent (user bản app cũ không có popup) nên so được trước/sau rollout. `s4..s8` trong SQL là nhánh **bắt buộc** qua accept consent — dùng khi consent đã rollout để so nhánh có popup vs không (`b8 − s8` trên `s1 − s3`).

## Vì sao đếm theo device_id
- Lúc đăng ký chưa có `zalopay_id`.
- iOS: `firebase_app_instance_id` / `appsflyer_id` chỉ có ở một phần nhỏ event screen 10 → ghép theo đó làm tụt số iOS.
- Không đếm theo SĐT (`phone_number` chỉ có ở 1019.032, các bước sau vẫn phải ghép qua device) hay theo lượt (user retry OTP làm méo SR). Đếm theo lượt chỉ dùng khi đào riêng bước OTP.

## Chạy
1. `funnel-register.sql`: thay `<YM>` (vd `202611`), `<D>` (vd `20261119`). **1 ngày / query** (~2 phút); không chạy khoảng nhiều ngày một lần (timeout). Tối đa 2 query song song.
2. Query > 120s sẽ bị đẩy xuống nền — chờ notification, đừng gửi lại.
3. Ngày hôm nay chưa đủ partition → ghi rõ "tới ~HHh", không so với ngày đủ.

## Khuôn report ("lấy số funnel register")
Mặc định 3 ngày gần nhất, **mỗi ngày 1 bảng** cột `iOS | Android | Tổng`, ô = `số device · % so bước tham chiếu`, dòng SR cuối (đậm). **Luôn hiện 2 dòng consent (Load / Accept) kể cả khi = 0.**

| Bước | iOS | Android | Tổng |
|---|---|---|---|
| Bắt đầu đăng ký | … | … | … |
| Load popup consent | … · x% | | |
| Accept consent | … · x% | | |
| Vào màn OTP | … · x% | | |
| Qua OTP | | | |
| Tạo PIN | | | |
| Xác nhận PIN | | | |
| Đăng ký thành công | | | |
| **SR** | | | |

Sau bảng: 2–3 ý nhận xét (bước rơi nhiều nhất, thay đổi so với hôm trước, coverage consent). Khi consent đã rollout: thêm bảng nhánh qua consent vs không, tỉ lệ agree_all vs confirm.

## Ghi chú log thật
- Log flush theo lô vài giây → nhiều event trùng timestamp; luôn so `>=`, không `>`.
- Key CTA viết hoa: `$.CTA` (giá trị `agree_all` / `confirm` / `X`).
- 1019.053 thực tế ra `consent_type='marketing'` (doc ghi `comercial_promotion`), `action='check'`.
- Android 1012.000 có `flow='onboarding'`, iOS `flow` null — không lọc theo `flow`.
- 1012.043 không có `user_flow` — chỉ ghép theo device + thứ tự.
- Web (zpi_actionlog) không dùng 02.1019/1012/1013/1014; đăng ký web là luồng K0→K1 riêng, không nằm trong funnel này.
- Đối chiếu BE: số device vào màn OTP ở funnel ≈ số `device_id` distinct của `um_send_sms` source `register` (lệch < 1%); số lượt SMS > số device do gửi lại/thử lại. Bảng BE chỉ có `otp_method='sms'`.
