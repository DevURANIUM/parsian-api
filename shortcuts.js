'use strict';
const definitions=[['pol','transfer-instant-fixed','/pol'],['sheba','transfer-iban-fixed','/sheba'],['pol-sms','transfer-instant-sms','/pol/sms'],['sheba-sms','transfer-iban-sms','/sheba/sms'],['pol-code','transfer-instant-sms-request','/pol/code'],['sheba-code','transfer-iban-sms-request','/sheba/code']];
const routes=definitions.map(([command,target,path])=>({...require('./transfer-modes').routes.find(r=>r.command===target),command,target,path}));
const aliases={from:'sourceAccount',to:'iban',pass:'password',branch:'branchCode',user:'username',customer:'customerNumber'};
function expand(body){const out={...body};for(const [short,long]of Object.entries(aliases))if(Object.hasOwn(out,short)){if(Object.hasOwn(out,long))throw Object.assign(Error('Duplicate field: '+short),{status:400,code:'INVALID_INPUT'});out[long]=out[short];delete out[short];}return out;}
module.exports={routes,expand};
