'use strict';
function transactionQuery(input={}){
 const today=new Date();today.setUTCHours(0,1,0,0);const start=new Date(today);start.setUTCDate(start.getUTCDate()-30);
 const q={action:null,length:10,offset:0,description:'',fromDate:start.toISOString(),toDate:today.toISOString(),order:'DESC',customerDescription:'',chStatementSearchDirection:'END_TO_START',fromAmount:null,toAmount:null,typeTransaction:null,...input};
 const number=(v,name)=>{if(v===''||v===null||typeof v==='boolean')throw Error('Invalid '+name);const n=Number(v);if(!Number.isSafeInteger(n)||n<0)throw Error('Invalid '+name);return n;};
 if(q.account!==undefined){q.depositNumber=q.account;delete q.account;}
 if(q.page!==undefined){const page=number(q.page,'page'),size=number(q.size??q.length,'size');q.offset=page*size;q.length=size;delete q.page;delete q.size;}else if(q.size!==undefined){q.length=number(q.size,'size');delete q.size;}
 for(const k of ['length','offset','fromAmount','toAmount'])if(q[k]!==undefined&&q[k]!==null)q[k]=number(q[k],k);
 if(q.length<1||q.length>6000||!Number.isSafeInteger(q.offset))throw Error('Invalid pagination; size must be 1..6000');
 if(typeof q.depositNumber!=='string'||/^0+$/.test(q.depositNumber)||!/^[0-9-]+$/.test(q.depositNumber))throw Error('Invalid account; use transactions ACCOUNT PAGE SIZE or transactions PAGE SIZE');
 for(const k of ['fromDate','toDate']){if(typeof q[k]!=='string'||!/^\d{4}-\d{2}-\d{2}T/.test(q[k])||!Number.isFinite(Date.parse(q[k])))throw Error('Invalid date: '+k+'; use ISO 8601');}
 if(Date.parse(q.fromDate)>Date.parse(q.toDate))throw Error('fromDate must not exceed toDate');
 return q;
}
module.exports={transactionQuery};
