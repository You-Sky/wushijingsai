import { bank, validateQuestion, sections, types } from '../src/core';
import assert from 'node:assert/strict';
assert.equal(bank.length,1000);
assert.deepEqual(bank.map(q=>q.id),Array.from({length:1000},(_,i)=>i+1));
for(const q of bank)assert.deepEqual(validateQuestion(q),[],`第${q.id}题`);
for(const section of sections)for(const [i,type] of types.entries())assert.equal(bank.filter(q=>q.section===section&&q.type===type).length,i===0?100:50);
console.log('PASS: 1000道题，连续编号，5个板块，每板块100单选/50多选/50填空，全部字段与答案格式通过。');
