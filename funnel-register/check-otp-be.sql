-- Đối chiếu bước OTP của funnel với log BE gửi SMS OTP (database_id=70, schema um_encrypt)
-- Lưu ý: cột phone_number không giải mã được — chạm vào là hỏng query, đừng SELECT.
-- source_id='register' = đăng ký app; 'h5register' = đăng ký web H5 (device_id rỗng, không đếm theo device được).
SELECT ymd, source_id, otp_method, count(*) req, count(distinct device_id) devs
FROM um_send_sms
WHERE ym='<YM>' AND ymd='<D>' AND source_id IN ('register','h5register')
GROUP BY 1,2,3 ORDER BY 1,2,3
