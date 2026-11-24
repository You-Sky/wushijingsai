import { bank, validateQuestion, sections, types } from '../src/core';
import assert from 'node:assert/strict';
assert.equal(bank.length,2000);
assert.deepEqual(bank.map(q=>q.id),Array.from({length:2000},(_,i)=>i+1));
for(const q of bank)assert.deepEqual(validateQuestion(q),[],`第${q.id}题`);
for(const section of sections)for(const [i,type] of types.entries())assert.equal(bank.filter(q=>q.section===section&&q.type===type).length,i===0?200:100);
console.log('PASS: 2000道题，连续编号，5个板块，每板块200单选/100多选/100判断，全部字段与答案格式通过。');
