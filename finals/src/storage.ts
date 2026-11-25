import { BANK_ID, initialState, type State } from './core';
const DB=BANK_ID;
let dbPromise:Promise<IDBDatabase>|null=null;
function db(){return dbPromise??=new Promise((resolve,reject)=>{const req=indexedDB.open(DB,1);req.onupgradeneeded=()=>req.result.createObjectStore('learning');req.onsuccess=()=>resolve(req.result);req.onerror=()=>reject(req.error)})}
export async function loadState():Promise<State>{const database=await db();return new Promise((resolve,reject)=>{const tx=database.transaction('learning','readonly');const req=tx.objectStore('learning').get('state');req.onsuccess=()=>resolve(req.result??initialState());req.onerror=()=>reject(req.error)})}
let queue=Promise.resolve();
export function saveState(state:State):Promise<void>{const snapshot=structuredClone(state);const job=queue.catch(()=>{}).then(async()=>{const database=await db();await new Promise<void>((resolve,reject)=>{const tx=database.transaction('learning','readwrite');tx.objectStore('learning').put(snapshot,'state');tx.oncomplete=()=>resolve();tx.onerror=()=>reject(tx.error);tx.onabort=()=>reject(tx.error)})});queue=job;return job}
