# zlp-po-skills

Bộ Claude Code skill dùng chung cho Product Owner tại ZaloPay.

## Danh sách skill

| Skill | Dùng khi |
|---|---|
| [review-prd](review-prd/SKILL.md) | Review PRD (Confluence) trước khi giao dev/QC — chấm 13 tiêu chí C1–C13, xuất câu hỏi PO cần chốt |
| [create-jira-task](create-jira-task/SKILL.md) | Tạo/sửa ticket Jira PCFUM theo Change Request Template: title `[Function][Platform]`, User journey, AC Given/When/Then, custom field, sprint/epic, link ticket |

## Cài đặt

```bash
git clone https://github.com/harry1101-caption/zlp-po-skills.git ~/zlp-po-skills
cd ~/zlp-po-skills && ./install.sh
```

`install.sh` tạo symlink từng skill vào `~/.claude/skills/`. Cập nhật: `cd ~/zlp-po-skills && git pull` (skill mới thì chạy lại `./install.sh`).

## Cấu hình riêng

`create-jira-task` cần bảng map tên → Jira username của team: `cp create-jira-task/team.local.example.md create-jira-task/team.local.md` rồi điền (file này gitignore, không bị commit).

## Yêu cầu

- MCP `zalopay` đã đăng nhập Confluence/Jira.

## Thêm skill mới

Mỗi skill là một thư mục ở gốc repo, có `SKILL.md` (frontmatter `name`, `description`). Thêm dòng vào bảng trên rồi mở PR.
