"""Only extracts supplied Word text; never generates or corrects questions."""
from zipfile import ZipFile
import xml.etree.ElementTree as ET
import json, re, sys, hashlib
from pathlib import Path
from collections import Counter, defaultdict

source = Path(sys.argv[1])
base = Path(__file__).resolve().parents[1]
ns = {'w':'http://schemas.openxmlformats.org/wordprocessingml/2006/main'}
with ZipFile(source) as z:
    root = ET.fromstring(z.read('word/document.xml'))
paragraphs=[]
for p in root.findall('.//w:body//w:p', ns):
    s=''
    for e in p.iter():
        if e.tag==f"{{{ns['w']}}}t": s+=e.text or ''
        elif e.tag==f"{{{ns['w']}}}tab": s+='\t'
        elif e.tag in [f"{{{ns['w']}}}br",f"{{{ns['w']}}}cr"]: s+='\n'
    paragraphs.append(s)
sections=['党史','新中国史','改革开放史','社会主义发展史','中华民族发展史']
questions=[]; current=None; section=None; kind=None
for i, text in enumerate(paragraphs):
    if re.match(r'^第[一二三四五]编 ',text):
        section=text.split(' ',1)[1]; continue
    if re.match(r'^[一二三]、(单选题|多选题|判断题)',text):
        kind=text.split('、')[1]; continue
    m=re.match(r'^(\d+)\.\s*(.*)',text,re.S)
    if m:
        current={'id':int(m[1]),'section':section,'type':kind,'rawParagraphs':[text],'sourceParagraph':i+1}
        questions.append(current)
    elif current and text.strip(): current['rawParagraphs'].append(text)
errors=[]; warnings=[]
for q in questions:
    raw=q['rawParagraphs']; first=re.sub(r'^\d+\.\s*','',raw[0])
    difficulty=re.search(r'【难度：([^】]+)】',first)
    q['difficulty']=difficulty[1] if difficulty else ''
    first=re.sub(r'\s*【难度：[^】]+】\s*$', '', first)
    joined='\n'.join([first]+raw[1:])
    am=re.search(r'答案：(.*?)\s+解析：([\s\S]+)$',joined)
    if not am:
        errors.append({'id':q['id'],'message':'答案或解析无法识别'}); continue
    q['answerText']=am[1].strip(); q['explanation']=am[2].strip()
    body=joined[:am.start()].rstrip()
    matches=list(re.finditer(r'(?:^|\s)([A-H])\.\s*',body))
    q['options']=[]
    if matches:
        q['stem']=body[:matches[0].start()].rstrip()
        for j,m in enumerate(matches):
            end=matches[j+1].start() if j+1<len(matches) else len(body)
            q['options'].append({'key':m[1],'text':body[m.end():end].rstrip()})
    else: q['stem']=body
    q['answer']=[q['answerText']] if q['type']=='判断题' else re.findall('[A-H]',q['answerText'])
    if q['type']=='判断题':
        if q['answer'] not in [['正确'],['错误']]: errors.append({'id':q['id'],'message':'判断题答案异常'})
    else:
        keys=[o['key'] for o in q['options']]
        if keys!=['A','B','C','D']: errors.append({'id':q['id'],'message':'选项数量/顺序异常','keys':keys})
        if not set(q['answer'])<=set(keys) or not q['answer']: errors.append({'id':q['id'],'message':'答案与选项不匹配'})
        if q['type']=='单选题' and len(q['answer'])!=1: errors.append({'id':q['id'],'message':'单选答案个数异常'})
        if q['type']=='多选题' and len(q['answer'])<2: errors.append({'id':q['id'],'message':'多选答案个数异常'})
    if not q['stem'] or not q['explanation'] or q['difficulty'] not in ['简单','中等','较难']: errors.append({'id':q['id'],'message':'题干/解析/难度缺失'})
    expected=sections[(q['id']-1)//80]; pos=(q['id']-1)%80
    if q['section']!=expected or q['type']!=('单选题' if pos<40 else '多选题' if pos<60 else '判断题'): errors.append({'id':q['id'],'message':'板块或题型与预期分布不同'})
ids=[q['id'] for q in questions]
if ids!=list(range(1,401)): errors.append({'message':'编号未连续覆盖1—400','ids':ids})
same=defaultdict(list)
for q in questions: same[q['stem']].append(q['id'])
for stem, duplicate_ids in same.items():
    if len(duplicate_ids)>1: warnings.append({'ids':duplicate_ids,'message':'Word原文题干相同，按原编号保留，未去重','stem':stem})
summary=[{'section':s,'total':sum(q['section']==s for q in questions),**dict(Counter(q['type'] for q in questions if q['section']==s))} for s in sections]
report={'source':source.name,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'paragraphCount':len(paragraphs),'total':len(questions),'summary':summary,'difficulty':dict(Counter(q['difficulty'] for q in questions)),'errors':errors,'warnings':warnings,'notes':['仅校验文档提取结构与答案格式，未对史实进行外部核验。','所有原题、答案、解析与难度均保留；重复题干如源文件存在则保留原题号。','rawParagraphs保留每题原始段落，便于对照。']}
(base/'src/data/questions.json').write_text(json.dumps(questions,ensure_ascii=False,indent=2),encoding='utf-8')
(base/'src/data/import-report.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
print(json.dumps(report,ensure_ascii=False,indent=2))
assert not errors, 'Import validation failed'
