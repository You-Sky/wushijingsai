"""Independent fidelity check for separately numbered questions and answers."""
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
assert [q['id'] for q in qs]==list(range(1,1001))
numbered=[i+1 for i,t in enumerate(paras) if re.match(r'^\d+\.\s+',t)]
assert len(numbered)==2000
assert sorted([q['sourceParagraph'] for q in qs]+[q['sourceAnswerParagraph'] for q in qs])==numbered
for q in qs:
    raw=q['rawParagraphs']; start=q['sourceParagraph']-1; ans=q['sourceAnswerParagraph']-1
    assert raw[:-1]==paras[start:start+len(raw)-1],f'题目段落不匹配 {q["id"]}'
    assert raw[-1]==paras[ans],f'答案段落不匹配 {q["id"]}'
    expected=[f'{q["id"]}. {q["stem"]}']+[f'{o["key"]}. {o["text"]}' for o in q['options']]
    expected.append(f'{q["id"]}. {q["answerText"]}\u3000{q["explanation"]}')
    assert expected==raw,f'字段重构不匹配 {q["id"]}'
    assert q['answer']==([q['answerText']] if q['type']=='填空题' else list(q['answerText']))
    assert q['difficulty']=='未标注'
print('PASS: all 1000 question and answer paragraphs match Word exactly; 2000 numbered source paragraphs accounted for.')
