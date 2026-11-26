import section1 from './data/section-1.json';
import section2 from './data/section-2.json';
import section3 from './data/section-3.json';
import section4 from './data/section-4.json';
import section5 from './data/section-5.json';
export const sections = ['党史','新中国史','改革开放史','社会主义发展史','中华民族史'];
export const types = ['单选题','多选题','填空题'];
export const difficulties = ['未标注','简单','中等','较难'];
export type Question = { id:number; section:string; type:string; difficulty:string; stem:string; options:{key:string;text:string}[]; answer:string[]; answerText:string; explanation:string; rawParagraphs:string[]; sourceParagraph:number; sourceAnswerParagraph?:number; sourceReference?:string };
export const bank = [...section1,...section2,...section3,...section4,...section5] as Question[];
export const BANK_ID = 'wushi-finals-final-20261126-v1';
export const TOTAL = bank.length;
export type Attempt = {id:string; questionId:number; answer:string[]; correct:boolean; at:number; mode:'practice'|'exam'; examId?:string};
export type Wrong = {count:number; status:'pending'|'mastered'|'removed'; lastWrongAt:number; lastWrongAnswer:string[]};
export type Exam = {id:string; questions:Question[]; answers:Record<number,string[]>; startedAt:number; deadline:number|null; submittedAt?:number; elapsed?:number; score?:number; correctCount?:number; title:string};
export type State = {version:1; bankId:typeof BANK_ID; attempts:Attempt[]; wrongs:Record<number,Wrong>; favorites:number[]; cursor:number; drafts:Record<number,string[]>; exams:Exam[]; activeExam:Exam|null; overrides:Record<number,Question>};
export function initialState():State {return {version:1,bankId:BANK_ID,attempts:[],wrongs:{},favorites:[],cursor:1,drafts:{},exams:[],activeExam:null,overrides:{}}}
export function beginPractice(state:State,ids:number[]|null,start?:number,fresh=false):State {
 const cursor=start??ids?.[0]??state.cursor;
 if(!fresh||!ids?.length)return cursor===state.cursor?state:{...state,cursor};
 const drafts={...state.drafts};for(const id of ids)drafts[id]=[];
 return {...state,cursor,drafts};
}
export function equalAnswer(a:string[],b:string[]) {return a.length>0&&new Set(a).size===a.length&&[...a].sort().join('|')===[...b].sort().join('|')}
export function normalizeFill(value:string){return value.normalize('NFKC').replace(/[\s《》〈〉“”]/g,'').replace(/[,，]/g,'、')}
export function isCorrect(q:Question,answer:string[]){
 if(q.type!=='填空题')return equalAnswer(answer,q.answer);
 if(answer.length!==1||q.answer.length!==1)return false;
 let actual=normalizeFill(answer[0]),expected=normalizeFill(q.answer[0]);
 if(/^(?:公元前|公元)?\d+年$/.test(expected)){actual=actual.replace(/年$/,'');expected=expected.slice(0,-1)}
 return actual.length>0&&actual===expected;
}
export function uid(){return crypto.randomUUID()}
export function recordAnswer(state:State,q:Question,answer:string[],mode:'practice'|'exam'='practice',examId?:string,at=Date.now()):State {
 const correct=isCorrect(q,answer); const wrongs={...state.wrongs};
 if(!correct){const old=wrongs[q.id]; wrongs[q.id]={count:(old?.count??0)+1,status:'pending',lastWrongAt:at,lastWrongAnswer:[...answer]}}
 else if(wrongs[q.id]) wrongs[q.id]={...wrongs[q.id],status:'mastered'};
 const drafts={...state.drafts}; if(mode==='practice')delete drafts[q.id];
 return {...state,wrongs,drafts,cursor:mode==='practice'?q.id:state.cursor,attempts:[...state.attempts,{id:uid(),questionId:q.id,answer:[...answer],correct,at,mode,...(examId?{examId}:{})}]};
}
export function sampleQuestions(pool:Question[],count:number,random=Math.random):Question[]{
 if(!Number.isInteger(count)||count<1||count>pool.length)throw Error(`题量须为 1—${pool.length} 之间的整数`);
 const arr=[...pool]; for(let i=arr.length-1;i>0;i--){const j=Math.floor(random()*(i+1));[arr[i],arr[j]]=[arr[j],arr[i]]} return arr.slice(0,count);
}
export function finishExam(state:State,now=Date.now()):State {
 const exam=state.activeExam;if(!exam)return state;
 const end=exam.deadline?Math.min(now,exam.deadline):now;
 const correctCount=exam.questions.filter(q=>isCorrect(q,exam.answers[q.id]??[])).length;
 const done={...exam,submittedAt:end,elapsed:Math.max(0,end-exam.startedAt),score:Math.round(correctCount/exam.questions.length*10000)/100,correctCount};
 let next:State={...state,activeExam:null,exams:[done,...state.exams]};
 for(const q of exam.questions) next=recordAnswer(next,q,exam.answers[q.id]??[],'exam',exam.id,end);
 return next;
}
export function validateQuestion(q:Question):string[]{
 const e:string[]=[];
 if(!q||!Number.isInteger(q.id)||q.id<1||q.id>TOTAL)return [`题号必须为1—${TOTAL}`];
 if(!sections.includes(q.section)||!types.includes(q.type)||!difficulties.includes(q.difficulty)) e.push('板块、题型或难度不合法');
 if(typeof q.stem!=='string'||!q.stem.trim()||typeof q.explanation!=='string'||!q.explanation.trim())e.push('题干与解析不能为空');
 if(!Array.isArray(q.answer)||!q.answer.length||new Set(q.answer).size!==q.answer.length)e.push('答案不能为空或重复');
 if(!Array.isArray(q.options))return [...e,'选项格式不合法'];
 if(q.type==='填空题'){if(q.options.length||q.answer?.length!==1||typeof q.answer[0]!=='string'||!normalizeFill(q.answer[0]))e.push('填空题须有一个非空文本答案，且不得包含选项')}
 else {const keys=q.options.map(o=>o.key);if(keys.length<2||new Set(keys).size!==keys.length||keys.some(k=>!(/^[A-H]$/).test(k))||q.options.some(o=>!o.text?.trim()))e.push('选项需有唯一字母与非空文本');if(q.answer?.some(a=>!keys.includes(a)))e.push('答案不在选项中');if(q.type==='单选题'&&q.answer?.length!==1)e.push('单选题须恰好一个答案');if(q.type==='多选题'&&q.answer?.length<2)e.push('多选题至少两个答案')}
 return e;
}
export function validateBackup(v:unknown):State {
 const s=v as State;
 if(!s||s.version!==1||!Array.isArray(s.attempts)||!Array.isArray(s.exams)||!Array.isArray(s.favorites)||!s.wrongs||typeof s.wrongs!=='object'||!s.overrides||typeof s.overrides!=='object'||!s.drafts||typeof s.drafts!=='object')throw Error('备份结构无效，请选择本系统导出的JSON文件');
 if(s.bankId!==BANK_ID)throw Error('此备份不是决赛终稿1000题库的学习记录，无法导入。');
 const id=(n:number)=>Number.isInteger(n)&&n>=1&&n<=TOTAL;
 const arr=(a:unknown):a is string[]=>Array.isArray(a)&&a.every(v=>typeof v==='string');
 if(!id(s.cursor)||s.favorites.some(n=>!id(n))||s.attempts.some(a=>!a||!id(a.questionId)||!arr(a.answer)||typeof a.correct!=='boolean'||!Number.isFinite(a.at)||typeof a.id!=='string'||!['practice','exam'].includes(a.mode)))throw Error('备份中的答题记录格式错误');
 for(const [key,q] of Object.entries(s.overrides))if(+key!==q.id||validateQuestion(q).length)throw Error('备份中的题库编辑数据格式错误');
 for(const [key,w] of Object.entries(s.wrongs))if(!id(+key)||!w||!Number.isInteger(w.count)||w.count<1||!['pending','mastered','removed'].includes(w.status)||!Number.isFinite(w.lastWrongAt)||!arr(w.lastWrongAnswer))throw Error('备份中的错题记录格式错误');
 for(const [key,a] of Object.entries(s.drafts))if(!id(+key)||!arr(a))throw Error('练习草稿格式错误');
 for(const e of [...s.exams,...(s.activeExam?[s.activeExam]:[])]){
  if(!e||typeof e.id!=='string'||!Array.isArray(e.questions)||!e.questions.length||new Set(e.questions.map(q=>q.id)).size!==e.questions.length||e.questions.some(q=>validateQuestion(q).length)||!e.answers||typeof e.answers!=='object'||Object.entries(e.answers).some(([key,a])=>!id(+key)||!arr(a))||!Number.isFinite(e.startedAt)||(e.deadline!==null&&(!Number.isFinite(e.deadline)||e.deadline<e.startedAt)))throw Error('备份中的考试记录格式错误');
 }
 if(s.exams.some(e=>!Number.isFinite(e.score)||!Number.isFinite(e.submittedAt)||!Number.isFinite(e.elapsed)))throw Error('考试成绩格式错误');
 return s;
}
export function download(name:string,data:unknown){const url=URL.createObjectURL(new Blob([JSON.stringify(data,null,2)],{type:'application/json'}));const a=document.createElement('a');a.href=url;a.download=name;a.click();setTimeout(()=>URL.revokeObjectURL(url),1000)}
export function percent(n:number,d:number){return d?Math.round(n/d*100):0}
