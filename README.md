# grade-import-workflow — 教务系统成绩导入流程

把准备好的成绩 Excel 导入教务系统成绩录入页面的完整操作流程：**登录信息门户 → SSO 进入教务系统 → 成绩录入 → jqGrid 选择班级 → 导入文件 → 保存**。

## 适用场景

- 期末/平时成绩录入：把已算好、已填模板的成绩文件批量导入教务系统
- 与 [grade-management](https://github.com/shuxuexiaoli/grade-management)（成绩计算与模板填写）衔接：那边产出文件，这边负责导入

## 内容说明

- `SKILL.md`：六步导入流程的操作指南（含登录状态检测、SSO 链接提取、jqGrid 选班级等关键细节）
- `references/`：
  - `excel-template-format.md` — 成绩导入 Excel 模板的格式要求
  - `excel-com-fix-template.py` — 模板格式修复脚本
  - `batch-import-pattern.md` — 多班级批量导入的模式
  - `import-cover-mode-and-pitfalls.md` — 覆盖模式与常见坑
  - `import-failure-after-switch.md` — 切换班级后导入失败的排查

## 使用方式

本仓库是一份给 AI 助手加载的技能（skill）：把 `SKILL.md` 与 `references/` 提供给助手，配合已登录的浏览器（CDP）环境，即可按流程执行成绩导入。前置条件：成绩文件已按模板格式准备好。

> 作者为职业院校数学教师，更多教学工具见主页：https://github.com/shuxuexiaoli
