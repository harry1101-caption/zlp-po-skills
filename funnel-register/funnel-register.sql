-- Funnel Register (ZPA, screen 10) — theo device_id/ngày, tuần tự (ts >= bước trước; log flush lô ~3s nên hay trùng ts)
-- Thay <YM>, <D>. Chạy 1 ngày/query.
-- s1 1019.036 user_flow=registration
-- s2 1019.051 load popup consent
-- s3 1019.056 CTA in (agree_all, confirm)        -- chỉ quan tâm load -> CTA đồng ý (chốt 20/11/2026)
-- s4 1012.000 user_flow='registration by phone'
-- s5 1012.043 pass OTP
-- s6 1013.000 load tạo PIN
-- s7 1014.000 load xác nhận PIN
-- s8 1014.002 error rỗng = đăng ký thành công
-- b4..b8: cùng các bước nhưng KHÔNG bắt buộc qua consent (để so SR trước/sau go-live)
WITH ev AS (
  SELECT json_extract_scalar(metadata,'$.device_id') dev,
         json_extract_scalar(metadata,'$.os_type') os,
         event_id e, "timestamp" ts,
         json_extract_scalar(metadata,'$.user_flow') uf,
         json_extract_scalar(metadata,'$.CTA') cta,
         json_extract_scalar(metadata,'$.error') err
  FROM zpa_eventlog
  WHERE ym='<YM>' AND ymd='<D>' AND screen_id='10'
    AND event_id IN ('01.1019.036','01.1019.051','01.1019.056','01.1012.000','01.1012.043','01.1013.000','01.1014.000','01.1014.002')
    AND json_extract_scalar(metadata,'$.device_id') IS NOT NULL
), s1 AS (
  SELECT dev, max(os) os, min(ts) t1 FROM ev WHERE e='01.1019.036' AND uf='registration' GROUP BY 1
), x AS (
  SELECT s1.dev, s1.os, s1.t1,
    min(if(e='01.1019.051' AND ts>=t1, ts)) t2,
    array_agg(if(e='01.1019.056' AND cta IN ('agree_all','confirm') AND ts>=t1, ts)) a3,
    array_agg(if(e='01.1012.000' AND uf='registration by phone' AND ts>=t1, ts)) a4,
    array_agg(if(e='01.1012.043' AND ts>=t1, ts)) a5,
    array_agg(if(e='01.1013.000' AND ts>=t1, ts)) a6,
    array_agg(if(e='01.1014.000' AND ts>=t1, ts)) a7,
    array_agg(if(e='01.1014.002' AND coalesce(err,'')='' AND ts>=t1, ts)) a8
  FROM s1 JOIN ev ON ev.dev=s1.dev GROUP BY 1,2,3
), y AS (
  SELECT dev, os, t1, t2,
    array_min(filter(a3, v -> v IS NOT NULL AND t2 IS NOT NULL AND v>=t2)) t3,
    a4,a5,a6,a7,a8 FROM x
), z AS (  -- chuỗi qua consent
  SELECT y.*, array_min(filter(a4, v -> v IS NOT NULL AND t3 IS NOT NULL AND v>=t3)) t4,
         array_min(filter(a4, v -> v IS NOT NULL)) b4 FROM y
), z2 AS (
  SELECT z.*, array_min(filter(a5, v -> v IS NOT NULL AND t4 IS NOT NULL AND v>=t4)) t5,
              array_min(filter(a5, v -> v IS NOT NULL AND b4 IS NOT NULL AND v>=b4)) b5 FROM z
), z3 AS (
  SELECT z2.*, array_min(filter(a6, v -> v IS NOT NULL AND t5 IS NOT NULL AND v>=t5)) t6,
               array_min(filter(a6, v -> v IS NOT NULL AND b5 IS NOT NULL AND v>=b5)) b6 FROM z2
), z4 AS (
  SELECT z3.*, array_min(filter(a7, v -> v IS NOT NULL AND t6 IS NOT NULL AND v>=t6)) t7,
               array_min(filter(a7, v -> v IS NOT NULL AND b6 IS NOT NULL AND v>=b6)) b7 FROM z3
), z5 AS (
  SELECT z4.*, array_min(filter(a8, v -> v IS NOT NULL AND t7 IS NOT NULL AND v>=t7)) t8,
               array_min(filter(a8, v -> v IS NOT NULL AND b7 IS NOT NULL AND v>=b7)) b8 FROM z4
)
SELECT '<D>' ymd, if(os='1','ios',if(os='2','android','other')) os,
  count(*) s1, count(t2) s2, count(t3) s3, count(t4) s4, count(t5) s5, count(t6) s6, count(t7) s7, count(t8) s8,
  count(b4) b4, count(b5) b5, count(b6) b6, count(b7) b7, count(b8) b8
FROM z5 GROUP BY 2 ORDER BY 2
