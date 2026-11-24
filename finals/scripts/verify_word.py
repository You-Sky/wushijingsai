"""Independent fidelity check against the supplied OOXML source."""
from zipfile import ZipFile
from pathlib import Path
import xml.etree.ElementTree as ET
import re,json,sys
p=Path(sys.argv[1]);base=Path(__file__).resolve().parents[1]
ns={'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(p) as z:root=ET.fromstring(z.read('word/document.xml'))
paras=[]
for para in root.findall('.//w:body//w:p',ns):
    text=''
    for n in para.iter():
        if n.tag.endswith('}t'):text+=n.text or ''
        elif n.tag.endswith('}tab'):text+='\t'
        elif n.tag.endswith('}br') or n.tag.endswith('}cr'):text+='\n'
    paras.append(text)
qs=[q for i in range(1,6) for q in json.loads((base/f'src/data/section-{i}.json').read_text(encoding='utf-8'))]
assert [q['id'] for q in qs] == list(range(1,2001))
norm=lambda s:re.sub(r'\s+','',s)
for q in qs:
    start=q['sourceParagraph']-1
    for offset,raw in enumerate(q['rawParagraphs']):assert raw==paras[start+offset],f"raw text mismatch {q['id']}"
    reconstructed=f"{q['id']}. {q['stem']} 【难度：{q['difficulty']}】"+' '.join(f"{o['key']}. {o['text']}" for o in q['options'])+f"答案：{q['answerText']} 解析：{q['explanation']}"
    assert norm(reconstructed)==norm('\n'.join(q['rawParagraphs'])),f"field mismatch {q['id']}"
print('PASS: all 2000 original paragraph groups match Word exactly; extracted fields reconstruct all source characters (ignoring layout whitespace).')
