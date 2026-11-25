"""Independent exact source-paragraph and reconstructed-field fidelity check."""
from zipfile import ZipFile
from pathlib import Path
import xml.etree.ElementTree as ET
import re, json, sys
p=Path(sys.argv[1]); base=Path(__file__).resolve().parents[1]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(p) as z: root=ET.fromstring(z.read('word/document.xml'))
paras=[]
for para in root.findall('.//w:body//w:p',ns):
    text=''
    for n in para.iter():
        if n.tag.endswith('}t'): text+=n.text or ''
        elif n.tag.endswith('}tab'): text+='\t'
        elif n.tag.endswith('}br') or n.tag.endswith('}cr'): text+='\n'
    paras.append(text)
qs=[q for i in range(1,6) for q in json.loads((base/f'src/data/section-{i}.json').read_text(encoding='utf-8'))]
assert [q['id'] for q in qs] == list(range(1,1001))
assert len([p for p in paras if re.match(r'^\d+\.\s+',p)]) == 1000
norm=lambda s:re.sub(r'\s+','',s)
for q in qs:
    start=q['sourceParagraph']-1
    assert [*q['rawParagraphs']] == paras[start:start+len(q['rawParagraphs'])], f"原始段落不匹配 {q['id']}"
    reconstructed=f"{q['id']}. {q['stem']} 【{q['difficulty']}】"+' '.join(f"{o['key']}. {o['text']}" for o in q['options'])+f"答案：{q['answerText']} 解析：{q['explanation']} 原题库核心史实定位：{q['sourceReference']}"
    assert norm(reconstructed)==norm('\n'.join(q['rawParagraphs'])),f"字段不匹配 {q['id']}"
print('PASS: all 1000 question groups match source paragraphs exactly; all non-layout characters reconstruct from extracted fields.')
