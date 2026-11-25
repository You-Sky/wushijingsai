# 五史决赛精选训练题库

本网站以《五史决赛精选题库1000题(1).docx》为唯一题库来源，在原决赛网址更新为1000题精选版。决赛预测训练并非官方决赛题库；答案、解析及来源定位按 Word 保留，未经逐题外部史实核验。

| 题型 | 题量 |
| --- | ---: |
| 单选题 | 500 |
| 多选题 | 250 |
| 填空题 | 250 |
| 总计 | 1000 |

五大板块每板块200题：党史（1—200）、新中国史（201—400）、改革开放史（401—600）、社会主义发展史（601—800）、中华民族史（801—1000）。难度：简单97题、中等463题、较难440题。

支持顺序刷题、板块/题型/难度/关键词筛选、题号跳转、100题分组答题卡、固定底部操作栏、错题空白重新练习、收藏、随机和限时模拟考试、试卷分析、题库编辑、JSON备份及恢复。填空题以文字输入作答，保守规范化空白、全角字符、书名号及年份末尾的“年”后，与原标准答案比对；不做语义猜测。

学习数据使用独立 IndexedDB `wushi-finals-selected-1000-v1`。由于新版题号和题型均有变化，之前版本的记录不会套用或覆盖，新版单独记录，备份不可跨版本混用。不会上传学习记录。

## 开发与发布

使用 Node.js 22 或更新版本及 pnpm：

```sh
pnpm install
pnpm dev --port 5198
pnpm test
pnpm validate
pnpm build:pages
```

源码位于原仓库的 `finals/` 子目录，发布文件位于仓库的 `docs/finals/`，资源使用相对路径。每次更新后在 `finals/` 中重新执行 `pnpm build:pages`，将生成的 `finals/docs/` 内容同步到仓库的 `docs/finals/` 并提交；初赛发布文件无需修改。

## 题库与资料

题库数据按板块保存在 `src/data/section-1.json` 至 `section-5.json`。每题保留原Word段落和核心史实定位字段。 `src/data/import-report.json` 记录来源、校验和文档提示。配套复习讲义可用于个人复习，不混入题目或更改原答案。

可使用 `python scripts/import_word.py "Word文件路径.docx"` 重新导入，使用 `python scripts/verify_word.py "Word文件路径.docx"` 独立校验原文字段。

[决赛精选1000题](https://you-sky.github.io/wushijingsai/finals/) | [初赛题库](https://you-sky.github.io/wushijingsai/)
