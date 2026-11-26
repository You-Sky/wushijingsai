"""Parse the final Word bank: question blocks and separately numbered answer blocks."""
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import json, re, sys, hashlib
from pathlib import Path
from collections import Counter, defaultdict

source = Path(sys.argv[1]); base = Path(__file__).resolve().parents[1]
ns = {'w': 'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(source) as z: root = ET.fromstring(z.read('word/document.xml'))
paragraphs = []
for p in root.findall('.//w:body//w:p', ns):
    s = ''
    for e in p.iter():
        if e.tag == f"{{{ns['w']}}}t": s += e.text or ''
        elif e.tag == f"{{{ns['w']}}}tab": s += '\t'
        elif e.tag in [f"{{{ns['w']}}}br", f"{{{ns['w']}}}cr"]: s += '\n'
    paragraphs.append(s)

sections = ['党史', '新中国史', '改革开放史', '社会主义发展史', '中华民族史']
types = ['单选题', '多选题', '填空题']
heading_types = {'单项选择题': types[0], '多项选择题': types[1], '填空题': types[2]}
answer_types = {'单选答案与解析': types[0], '多选答案与解析': types[1], '填空答案与回查': types[2]}
questions = {}; answers = {}; section = kind = current = None; mode = 'intro'; source_notes = []
for i, text in enumerate(paragraphs, 1):
    if not text.strip(): continue
    m = re.fullmatch(r'第[一二三四五]编\s+(.+)', text)
    if m:
        section = m[1].strip(); assert section in sections; mode = 'questions'; current = kind = None; continue
    m = re.fullmatch(r'[一二三]、(单项选择题|多项选择题|填空题)（\d+题）', text)
    if m:
        assert mode == 'questions'; kind = heading_types[m[1]]; current = None; continue
    if section and text == f'{section} · 参考答案与回查':
        mode = 'answers'; current = kind = None; continue
    if text in answer_types:
        assert mode == 'answers'; kind = answer_types[text]; continue
    if mode == 'intro': source_notes.append(text); continue
    m = re.fullmatch(r'(\d+)\.\s*(.+)', text, re.S)
    if m:
        qid = int(m[1]); assert kind and section
        if mode == 'questions':
            assert qid not in questions, f'重复题号 {qid}'
            current = {'id': qid, 'section': section, 'type': kind, 'stem': m[2], 'difficulty': '未标注', 'options': [], 'sourceParagraph': i, 'rawParagraphs': [text]}
            questions[qid] = current
        else:
            assert qid not in answers, f'重复答案号 {qid}'
            assert qid in questions and questions[qid]['section'] == section and questions[qid]['type'] == kind, f'答案编号与题型不匹配 {qid}'
            parts = m[2].split('\u3000', 1)
            assert len(parts) == 2 and all(part.strip() for part in parts), f'答案或回查缺失 {qid}'
            answers[qid] = (parts[0], parts[1], text, i)
    elif mode == 'questions' and current:
        opt = re.fullmatch(r'([A-H])\.\s*(.+)', text, re.S)
        assert opt, f'无法识别第{current["id"]}题的段落 {i}: {text}'
        current['options'].append({'key': opt[1], 'text': opt[2]}); current['rawParagraphs'].append(text)
    else:
        raise ValueError(f'未识别段落 {i}: {text}')

assert list(questions) == list(range(1,1001)), '题号不连续'
assert list(answers) == list(range(1,1001)), '答案编号不连续'
for qid, q in questions.items():
    answer, detail, raw_answer, answer_para = answers[qid]
    q['answerText'] = answer; q['answer'] = [answer] if q['type'] == '填空题' else list(answer)
    q['explanation'] = detail
    q['sourceAnswerParagraph'] = answer_para
    q['rawParagraphs'].append(raw_answer)
    pos = (qid - 1) % 200
    assert q['section'] == sections[(qid - 1) // 200]
    assert q['type'] == (types[0] if pos < 100 else types[1] if pos < 150 else types[2])
    assert q['stem'] and q['explanation'] and q['answerText']
    if q['type'] == '填空题':
        assert not q['options'] and len(q['answer']) == 1
    else:
        keys = [o['key'] for o in q['options']]
        assert keys == ['A','B','C','D'] and set(q['answer']) <= set(keys) and len(set(q['answer'])) == len(q['answer']), f'选择题答案异常 {qid}'
        assert len(q['answer']) == 1 if q['type'] == types[0] else 2 <= len(q['answer']) <= 4

qs = list(questions.values()); same = defaultdict(list)
for q in qs: same[q['stem']].append(q['id'])
summary = [{'section': s, 'total': sum(q['section'] == s for q in qs), **dict(Counter(q['type'] for q in qs if q['section'] == s))} for s in sections]
report = {'source': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'paragraphCount': len(paragraphs), 'total': len(qs), 'summary': summary, 'difficulty': {'未标注': len(qs)}, 'errors': [], 'warnings': ['终稿没有逐题难度标签，全部显示未标注；填空题原文只提供答案与回查，不补写解析。'], 'repeatedStemGroups': sum(len(g) > 1 for g in same.values()), 'sourceNotes': source_notes[3:6], 'notes': ['仅校验文档提取结构与答案格式，未对史实进行外部核验。', '完整保存1000题题干、选项、集中答案与解析/回查。', 'sourceParagraph与sourceAnswerParagraph分别记录题目和答案在Word的起始段落。']}
for i, section in enumerate(sections, 1):
    (base / f'src/data/section-{i}.json').write_text(json.dumps([q for q in qs if q['section']==section],ensure_ascii=False,indent=2),encoding='utf-8')
(base/'src/data/import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
