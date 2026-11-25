"""Import only the supplied 1000-question Word bank, retaining every source question."""
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
questions = []; errors = []; section = kind = current = None
for i, text in enumerate(paragraphs):
    m = re.match(r'^第[一二三四五]编\s+(.+)$', text)
    if m:
        section = m[1].strip(); kind = None; continue
    m = re.match(r'^[一二三]、(单项选择题|多项选择题|填空题)', text)
    if m:
        kind = heading_types[m[1]]; continue
    m = re.match(r'^(\d+)\.\s*(.*)', text, re.S)
    if m:
        if current: raise ValueError(f"第{current['id']}题未包含定位段落")
        current = {'id': int(m[1]), 'section': section, 'type': kind, 'rawParagraphs': [text], 'sourceParagraph': i + 1}
        questions.append(current)
    elif current:
        current['rawParagraphs'].append(text)
        if text.startswith('原题库核心史实定位：'): current = None
assert current is None
assert [q['id'] for q in questions] == list(range(1, 1001))
assert sum(p.startswith('答案：') for p in paragraphs) == len(questions)
assert sum(p.startswith('原题库核心史实定位：') for p in paragraphs) == len(questions)

for q in questions:
    raw = q['rawParagraphs']; first = re.sub(r'^\d+\.\s*', '', raw[0]); m = re.fullmatch(r'(.*?)\s*【(简单|中等|较难)】\s*', first, re.S)
    if not m: raise ValueError(f"第{q['id']}题题干或难度无法识别")
    q['stem'], q['difficulty'] = m[1].rstrip(), m[2]
    q['options'] = []
    for line in raw[1:-2]:
        opt = re.fullmatch(r'([A-H])\.\s*(.+)', line, re.S)
        if not opt: raise ValueError(f"第{q['id']}题选项异常：{line}")
        q['options'].append({'key': opt[1], 'text': opt[2]})
    am = re.fullmatch(r'答案：(.*?)\s+解析：([\s\S]+)', raw[-2])
    ref = re.fullmatch(r'原题库核心史实定位：([\d、]+)', raw[-1])
    if not am or not ref: raise ValueError(f"第{q['id']}题答案、解析或定位异常")
    q['answerText'], q['explanation'], q['sourceReference'] = am[1].strip(), am[2].strip(), ref[1]
    q['answer'] = [q['answerText']] if q['type'] == '填空题' else list(q['answerText'])
    pos = (q['id'] - 1) % 200
    assert q['section'] == sections[(q['id'] - 1) // 200]
    assert q['type'] == (types[0] if pos < 100 else types[1] if pos < 150 else types[2])
    assert q['stem'] and q['explanation'] and q['answerText']
    if q['type'] == '填空题':
        assert not q['options'] and len(q['answer']) == 1
    else:
        keys = [o['key'] for o in q['options']]
        assert keys == ['A', 'B', 'C', 'D'] and set(q['answer']) <= set(keys) and len(q['answer']) == len(set(q['answer']))
        assert len(q['answer']) == 1 if q['type'] == '单选题' else 2 <= len(q['answer']) <= 4

same = defaultdict(list)
for q in questions: same[q['stem']].append(q['id'])
summary = [{'section': s, 'total': sum(q['section'] == s for q in questions), **dict(Counter(q['type'] for q in questions if q['section'] == s))} for s in sections]
report = {'source': source.name, 'sha256': hashlib.sha256(source.read_bytes()).hexdigest(), 'paragraphCount': len(paragraphs), 'total': len(questions), 'summary': summary, 'difficulty': dict(Counter(q['difficulty'] for q in questions)), 'errors': errors, 'warnings': [], 'repeatedStemGroups': sum(len(group) > 1 for group in same.values()), 'sourceNotes': paragraphs[3:7], 'notes': ['仅校验文档提取结构与答案格式，未对史实进行外部核验。', '所有1000题、答案、解析、难度及原题库核心史实定位均保留。', '原始Word的复习提要不计为题目。']}
for i, section in enumerate(sections, 1):
    (base / f'src/data/section-{i}.json').write_text(json.dumps([q for q in questions if q['section'] == section], ensure_ascii=False, indent=2), encoding='utf-8')
(base / 'src/data/import-report.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps(report, ensure_ascii=False, indent=2))
