---
name: create-jira-task
description: Tạo ticket Jira cho team PCF-UM đúng Change Request Template của công ty (Context / Requirement / Acceptance Criteria) và đúng convention custom field. Dùng khi người dùng nói "tạo task cho <tên người>", "vào tạo ticket cho <tên> ở sprint này", "tạo ticket ở sprint sau", hoặc yêu cầu sửa mô tả một ticket cho đúng template.
---

# Tạo ticket PCF-UM đúng template

Người dùng nói "tạo task cho <tên>" là muốn **một issue Jira hoàn chỉnh**: đúng project, đúng người, đúng sprint, đúng epic, đủ custom field, và **mô tả viết theo Change Request Template**. Không phải một dòng summary rồi để trống description.

## Template bắt buộc

Nguồn: trang **Change Request Template** trên Confluence (space `ZTM`) — tìm bằng `confluence_search` và đọc lại nếu nghi ngờ; nó có thể đổi.

Mô tả gồm đúng **3 heading**, dùng markup Jira `h2.`:

```
h2. Context
Vì sao cần change: vấn đề hiện tại, mục tiêu business/product, hoặc pain point. 1-3 câu.
Kèm link ticket CS / PRD / ticket liên quan nếu có.

h2. Requirement (<CHỌN 1: Product | Back-end & Front-end Technical | Configuration>)
<nội dung theo loại đã chọn — xem bảng dưới>

h2. Acceptance Criteria
h3. AC1 — <tên kịch bản ngắn>
* *Given:* <trạng thái/điều kiện ban đầu>
* *When:* <hành động của user/hệ thống>
* *Then:* <kết quả mong đợi>

h3. AC2 — ...
```

### Acceptance Criteria = Given/When/Then — bắt buộc

Mỗi kịch bản là một block `h3. ACn — <title>` gồm đúng 3 bullet `*Given:*` / `*When:*` / `*Then:*` (mẫu: PCFUM-12618). **Không** viết AC dạng bullet phẳng — PO đã reject format này (PCFUM-12978/12922/12923, 09/11/2026). Môi trường deploy, tracking/logging, rollout/feature flag nếu cần thì đưa thành một AC riêng cũng theo Given/When/Then.

### User journey — ticket có flow user

Ticket có flow user nhìn thấy (login, popup, eKYC…) thì mục Requirement **mở đầu bằng `h3. User journey`** (ngay sau link Figma nếu có): list đánh số `#`, mỗi bước 1 dòng — entry → hành động → hệ thống quyết định → từng nhánh (chặn / đi tiếp). Sau đó mới tới `h3. Rule` (bảng) và `h3. Ghi chú`.
- Chủ yếu cho ticket client (iOS/Android/ZMP); ticket BE chỉ thêm khi được yêu cầu. Ticket thuần log/config không cần.
- Khi sửa format theo luật này, **chỉ sửa ticket người dùng nêu tên** — không tự ý sửa ticket khác trong cùng bộ.

### Ticket tạo từ doc có sẵn → Requirement chỉ link doc

Ticket dựa trên page Confluence/PRD đã có: `h2. Requirement` chỉ ghi `Implement theo [<title>|<url>]` (+ ghi chú riêng của platform nếu có). **Không chép lại** bảng/chi tiết của page — page là nguồn duy nhất, PO sửa page thì ticket không bị lệch. Context 1–2 câu, AC Given/When/Then vẫn viết đủ.
- **Bẫy markup:** tên page có ngoặc vuông (vd `[UM][Use Case] ...`) làm hỏng link Jira `[text|url]`. Alias phải bỏ ngoặc: `[UM Use Case - Unbind ...|url]`.

**Chỉ chọn 1 trong 3 loại Requirement**, theo phần chiếm phần lớn scope:

| Loại | Chọn khi | Cần nêu |
|---|---|---|
| **Product** | Change đụng tới trải nghiệm user cuối (UI, flow, hành vi) | Affected users (và các state: đã/chưa KYC, có/không liên kết…), entry point (màn, CTA, deeplink), UI đổi gì, các state phải handle, user làm được gì, hệ thống phản hồi ra sao, edge case, event tracking, link Figma nếu có |
| **Back-end & Front-end Technical** | Change ở tầng kỹ thuật user không thấy (API, DB, service) | Đổi cái gì (1 câu rõ ràng), thay đổi DB, cấu trúc request/response, service nào liên quan, config nào đổi, diagram nếu cần |
| **Configuration** | Chỉ đổi config (feature flag, tham số, routing rule), không đụng code | Config nào, nằm ở đâu (Tool/File/DB/Redis/CMDB), apply thế nào, có phải restart service không |

Vừa có UI vừa có BE thì vẫn chọn 1 loại theo phần lớn scope, phần còn lại mô tả trong cùng mục — hoặc tách ticket con.

## Luật viết

### Ngắn nhất có thể mà vẫn đủ nghĩa — luật số 1

Mô tả càng ngắn càng tốt, miễn là dev đọc xong **grooming được ngay, không phải hỏi lại**. Đó là ngưỡng "đủ nghĩa"; dài hơn ngưỡng đó là thừa.

**Cắt chữ, không cắt dữ kiện.** Luôn giữ nguyên: tên field, enum, công thức, con số, tên màn/CTA, issue key, link. Cắt sạch: câu mở bài, câu chuyển tiếp, phần kể lể quá trình, chữ đệm ("hiện tại thì", "như đã biết", "nhằm mục đích"), và mọi câu lặp lại ý đã có ở mục trên.

**Bắt buộc trước khi submit** — chạy đủ 3 bước trên bản nháp, không được bỏ:

1. *Quét trùng Context ↔ Requirement.* Mỗi ý kỹ thuật chỉ được xuất hiện **một lần**. Context nói triệu chứng và vì sao cần làm; Requirement nói làm gì. Viết lý do ở Context rồi chép lại vào bảng Requirement là lỗi hay gặp nhất.
2. *Xoá từng câu* và hỏi "thiếu câu này dev có hỏi lại không?". Không hỏi lại thì xoá luôn.
3. *Đếm ký tự.* Description điển hình ≤ 1200 ký tự. Dài hơn thì quay lại bước 1, đừng tự nhủ "ca này phức tạp nên phải dài".

| Thừa | Đủ |
|---|---|
| "Hiện tại, App Android đang áp dụng giới hạn độ tuổi và không hỗ trợ người dùng dưới 14 tuổi thực hiện eKYC. Do đó, người dùng trong trường hợp này không thể tiếp tục thao tác chọn ngày cấp." | "Android chặn user dưới 14 tuổi đi eKYC → không chọn được ngày cấp ở step OCR." |
| "Cần rà soát và cập nhật lại logic kiểm tra độ tuổi cho phù hợp với loại giấy tờ mới" | "id_type = 6: bỏ `today - dob < 14`, thay bằng `today - dob >= 0`." |

Bảng ngắn hơn đoạn văn khi có từ 3 hạng mục. Một ý một dòng. Không viết lại thông tin đã nằm trong summary hoặc trong link đã dẫn.

### Các luật còn lại

- **Cụ thể ở mức *việc gì*, không phải mức *sửa thế nào*.** "update API" là sai; "thêm field `user_status` vào response của `GET /users/{id}`" là đúng. Nhưng **đừng** liệt kê file nào đổi dòng nào, danh sách lib phải rà, từng JVM flag — template đã định hình sẵn cái dev cần, ghi thêm chỉ gây rối. Nêu việc + repo mẫu để copy là hết; chỉ giữ chi tiết mà thiếu nó dev sẽ đi sai hướng (cái bẫy, ràng buộc không được đổi).
- **Solution chưa chốt thì nói thẳng là chưa chốt.** Khi hướng xử lý do mình hoặc AI nghĩ ra mà chưa ai review: ghi "Các hướng dưới đây *do AI đề xuất, chưa chốt*. Nhờ `[~<assignee>]` đánh giá và suy nghĩ thêm solution cho phù hợp hơn", rồi liệt kê mỗi hướng 1 dòng, không kèm cột lý do. Không đưa solution chưa chốt vào summary. AC chỉ đo **mục tiêu** (latency, hết lỗi 500), không đo cơ chế — đổi solution thì AC vẫn dùng được.
- **Mục nào N/A thì bỏ luôn**, không viết "không có".
- Nếu PRD đã có sẵn: **nói rõ phần nào PRD đã chốt, phần nào còn thiếu**, đừng viết như một requirement mới.
- Nếu việc này **đã từng làm rồi mà vẫn lỗi**, Context phải nói thẳng đó là regression hoặc implement thiếu, link ticket cũ, và nêu **giả thuyết chỗ nào bị sót** (đối chiếu requirement gốc với comment QC của ticket cũ — rule nào không có case test là chỗ đáng nghi nhất). Viết như requirement mới sẽ khiến dev implement lại thay vì đi tìm chỗ regress.
- PRD tự mâu thuẫn thì nêu ra trong ticket và ghi rõ làm theo mục nào — đừng để dev tự đoán.

## Custom field và toạ độ

| Thứ | Giá trị |
|---|---|
| Project | `PCFUM` |
| Board | `568` |
| Issue type | `Story` (mặc định). Task trace/fix bug tạo từ ticket CS/production issue → **`Task`**, không dùng `Bug` |
| `customfield_10100` | sprint id (số) |
| `customfield_10101` | epic key |
| `customfield_13710` | `{"id": "20176"}` — User Platform - User Management |
| `customfield_13711` | `{"id": "20265"}` — User Identification (riêng A05 dùng `20264` User authentication) |
| `customfield_12404` | **Chỉ issue type `Task`, bắt buộc** (thiếu là 400): `{"id": "16896"}` Tech Debt (fix bug), `17200` Tech Initiative, `27731` Product Initiative, `16897` Deployment |

**Summary (title) — bắt buộc** (người dùng yêu cầu 11/11/2026): `[<Function>][<Platform>] <Title in English>`
- Viết **tiếng Anh** toàn bộ, kể cả khi description tiếng Việt. Ví dụ: `[eKYC][iOS] Attach uid to reset-PIN out-app VNeID flow`.
- `<Function>` = tên chức năng/feature (eKYC, NFC, VNeID, Login, OTP, Profile…).
- `<Platform>` lấy theo **vai trò của người được assign** (cột *Platform trong title* ở `team.local.md`) — không tự chọn: `iOS` / `Android` / `ZMP` / `BE` / `Web`.

Epic hay dùng: `PCFUM-11791` (eKYC & NFC General Improvements), `PCFUM-11804` (VNeID), `PCFUM-11856` (Automate eKYC/NFC), `PCFUM-12084` (Improve UM system), `PCFUM-11846` (Profile Tab), `PCFUM-12161` (Compliance Tool A05).

## Map tên người → account Jira

Người dùng gọi tên thân mật, không khớp username. Bảng map nằm ở **`team.local.md`** cùng thư mục skill (file local, không commit — tạo từ `team.local.example.md`). Đọc file đó trước; chưa có file thì tra như dưới rồi đề nghị người dùng lưu kết quả vào đó.

Tên chưa có trong bảng: `/rest/api/2/user/search?username=<prefix>` rồi kiểm chéo bằng JQL `project = PCFUM AND assignee = <user> AND created > -60d` — prefix `[iOS]`/`[Android]`/`[ZMP]` trong summary cho biết vai trò. Có nhiều account trùng tên, đừng chọn bừa.

Mention trong description dùng `[~username]`, không gõ tên hiển thị.

## Sprint

```
/rest/agile/1.0/board/568/sprint?state=active,future
```

Sprint đặt tên `PCF-UM <yy>.<mm>.<A|B|C>` — **mỗi tháng có thể có tới 3 sprint**, nên "sprint sau" của `26.09.B` là `26.09.C`, không phải `26.10.A`. Luôn gọi API lấy id, đừng suy từ tên.

## Các bước

1. **Đọc nguồn yêu cầu** — tin nhắn Teams, ticket CS, lời người dùng. Lấy đủ: vấn đề gì, ai gặp, ở đâu, platform nào.
2. **Search Confluence/Jira xem đã có PRD hoặc ticket cũ chưa.** Bước này hay bị bỏ qua và dẫn tới tạo ticket trùng hoặc viết lại requirement đã chốt. Search **theo cụm từ trong requirement, không theo tên feature** — ví dụ `project = PCFUM AND summary ~ "year validation"`. Một đợt việc cũ thường có **1 ticket mỗi platform** (Android/iOS/ZMP/BE); tìm thấy ticket BE không có nghĩa client chưa làm, phải tra đủ bộ trước khi viết Context.
3. **Map tên người → username, lấy sprint id, xác định epic.**
4. **Viết description theo 3 heading**, chọn đúng 1 loại Requirement.
5. `jira_create_issue` với đủ custom field ở bảng trên.
6. **Verify**: `jira_search` với `fields=["summary","assignee","customfield_10100","customfield_10101","issuetype"]` để chắc sprint/epic/assignee đã vào đúng — `jira_create_issue` không báo lỗi khi custom field bị drop.
7. Báo lại cho người dùng: bảng key + assignee + platform, kèm 1 dòng tóm tắt nội dung.

## Liên kết ticket (QC yêu cầu 11/11/2026)

QC muốn mở 1 ticket là thấy được các ticket liên quan, không phải mở epic.

1. **Story liên quan → cùng 1 epic.** `customfield_10101` là **bắt buộc**; không có epic hợp thì hỏi người dùng, không để trống.
2. **Cùng 1 việc, nhiều platform → link chéo từng cặp bằng `Relates`** (không dùng `Cloners`, vì "clones" nghĩa là copy). Tạo xong cả bộ (iOS/Android/ZMP/BE) thì:
   ```
   POST /rest/api/2/issueLink
   {"type":{"name":"Relates"},"inwardIssue":{"key":"PCFUM-A"},"outwardIssue":{"key":"PCFUM-B"}}
   ```
   Chỉ tạo thêm 1 platform cho việc đã có ticket → bước 2 (search) tìm ticket các platform kia rồi link vào. Phần title sau `[Function][Platform]` giữ giống nhau giữa các platform.
3. **Epic → Initiative.** PCFUM không có issue type Initiative; Initiative/Feature nằm ở project **ZPBO** (ZLP Business Outcome), nối với epic bằng link type **`Agile Hive Link`** (epic *Child of* Initiative). Ví dụ duy nhất đang có: PCFUM-10613 Child of ZPBO-12741. Initiative UM 2026 đặt tên `[UM][2026] …` (vd ZPBO-13067 Revamp Profile Tab, ZPBO-13068 Remove Zalo dependency in Login, ZPBO-13066 Optimize SMS Cost, ZPBO-13069 Off Guest Mode, ZPBO-13382/13383 Login Extension).
   - Tạo/sửa epic: tìm Initiative bằng `project = ZPBO AND issuetype in (Initiative, Feature) AND summary ~ "UM" AND status not in (DONE, Cancelled)`, hỏi người dùng chọn cái nào rồi link `{"type":{"name":"Agile Hive Link"},"inwardIssue":{"key":"<ZPBO key>"},"outwardIssue":{"key":"<epic>"}}` (inward = "Parent of"). Kiểm lại trên UI lần đầu vì đây là link của plugin.
   - Không có Initiative phù hợp → link các epic liên quan với nhau bằng `Relates`.
4. **Verify** thêm field `issuelinks` ở bước 6.

Sửa mô tả ticket đã có thì `PUT /rest/api/2/issue/<key>` với `{"fields": {"description": "..."}}` — trả về `204` là thành công.

## Bẫy

- **Đừng tạo nhiều ticket cho một đợt việc.** Mặc định gom theo **vai trò**: 1 ticket mỗi platform/vai trò, không phải 1 ticket mỗi tính năng nhỏ. Hỏi lại nếu định tạo quá 2-3 ticket.
- `customfield_10100` nhận **số**, không phải tên sprint.
- **Đừng đổi issue type bằng `PUT fields.issuetype`.** Bug và Task khác workflow; PUT đổi type nhưng giữ workflow cũ ⇒ issue mất hết transition, không kéo được trên board (PCFUM-12698, 06/10/2026). Tạo đúng type ngay từ đầu; lỡ sai thì đổi qua màn Move của Jira (`/secure/MoveIssue!default.jspa?id=<issue id>`), có bước map status.
- Description dùng **markup Jira** (`h2.`, `*bold*`, `{{code}}`, `[text|url]`), không phải Markdown.
- Người dùng nhờ "mention bạn X" nghĩa là thêm `[~x]` vào description, không phải assign cho X.
