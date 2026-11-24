# 五史决赛预测训练题库

决赛专项训练网站，复用初赛网站的学习流程和界面，完整导入《五史决赛预测训练题库2000题(1).docx》。本题库为拓展预测练习，不是官方决赛原题；答案及解析按所提供的 Word 保留，未逐题独立核对史实。

| 组成 | 题量 |
| --- | ---: |
| 单选题 | 1000 |
| 多选题 | 500 |
| 判断题 | 500 |
| 总计 | 2000 |

五大板块每板块400题：党史（1—400）、新中国史（401—800）、改革开放史（801—1200）、社会主义发展史（1201—1600）、中华民族史（1601—2000）。难度：简单500题、中等500题、较难1000题。

支持顺序刷题、板块/题型/难度/关键词筛选、题号跳转、100题分组答题卡、固定底部操作栏、错题空白重新练习、收藏、随机和限时模拟考试、试卷分析、题库编辑、JSON备份及恢复。

学习数据使用独立 IndexedDB `wushi-finals-2000-v1`，与初赛网站数据库不同。决赛备份包含专属题库标识，并拒绝初赛备份，避免题号相同而错配。不会上传学习记录。

## 开发与发布

使用 Node.js 22 或更新版本及 pnpm：

```sh
pnpm install
pnpm dev --port 5173
pnpm test
pnpm validate
pnpm build:pages
```

源码位于原仓库的 `finals/` 子目录，发布文件位于仓库的 `docs/finals/`，资源采用相对路径。每次更新后在 `finals/` 中重新执行 `pnpm build:pages`，将生成的 `finals/docs/` 内容同步到仓库的 `docs/finals/` 并提交；原初赛发布文件无需修改。

## 题库文件

原始数据按板块存放在 `src/data/section-1.json` 至 `section-5.json`，总题数和结构由校验脚本验证。`src/data/import-report.json` 记录来源、校验结果和文档提示。每题保留原Word段落便于对照。

可使用 `python scripts/import_word.py "Word文件路径.docx"` 重新导入，使用 `python scripts/verify_word.py "Word文件路径.docx"` 独立校验原文字段。

初赛站点地址：https://you-sky.github.io/wushijingsai/ 。决赛站点地址：https://you-sky.github.io/wushijingsai/finals/ 。两者共用仓库，分别发布并使用独立数据存储。
