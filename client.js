'use strict';
require('./env').loadEnv();
const fs = require('node:fs');
const path = require('node:path');
const endpoints = require('./data/endpoints.json');
function failure(message,status,code,extra={}) { return Object.assign(new Error(message),{status,code,...extra}); }
function object(value) { return value!==null && typeof value==='object' && !Array.isArray(value); }
class ParsianClient {
 constructor({fetchImpl=fetch,dataDir=process.env.PARSIAN_DATA_DIR||path.join(__dirname,'data')}={}) {
  this.fetch=fetchImpl;this.file=path.join(dataDir,'session.json');
  try { this.session=JSON.parse(fs.readFileSync(this.file,'utf8')); }
  catch(e) { if(e.code!=='ENOENT')throw e;this.session={}; }
 }
 save() { fs.mkdirSync(path.dirname(this.file),{recursive:true});fs.writeFileSync(this.file+'.tmp',JSON.stringify(this.session),{mode:0o600});fs.renameSync(this.file+'.tmp',this.file); }
 status() { const hasSession=Boolean(this.session.sessionId);return {hasSession,hasToken:hasSession,loggedIn:false,state:hasSession?(this.session.invalidatedAt?'expired':'unverified'):'logged_out',bankVerified:false,liveVerified:false,ok:false,nextAction:hasSession&&!this.session.invalidatedAt?'check_session':'login'}; }
 logout() { this.session={};this.save();return this.status(); }
 async call(id,options={}) {
  if(!object(options))throw failure('Request options must be an object',400,'INVALID_INPUT');
  let {body,query={},params={}}=options;
  if(!object(query)||!object(params))throw failure('query and params must be objects',400,'INVALID_INPUT');
  const endpoint=endpoints.find(e=>e.id===id);
  if(!endpoint)throw failure('Unknown endpoint',400,'UNKNOWN_ENDPOINT');
  if(body===undefined&&Object.hasOwn(endpoint,'defaultBody'))body=endpoint.defaultBody;
  if(endpoint.hasBody&&body===undefined)throw failure('Request body required; see endpoint bodySchema',400,'INVALID_INPUT');
  const type=endpoint.bodySchema.type;
  if(body!==undefined&&((type==='object'&&!object(body))||(type==='array'&&!Array.isArray(body))))throw failure('Invalid body type; expected '+type,400,'INVALID_INPUT');
  if(endpoint.auth&&!this.session.sessionId)throw failure('Session required; run node cli.js login',401,'LOGIN_REQUIRED',{nextAction:'login'});
  const route=endpoint.path.replace(/\{([^}]+)\}/g,(_,key)=>{if(params[key]===undefined||params[key]===null||String(params[key])==='')throw failure('Missing parameter: '+key,400,'INVALID_INPUT');return encodeURIComponent(params[key]);});
  const url=new URL(route,'https://nextapi.iparsian724.ir');
  for(const [key,value]of Object.entries(query)){if(value===undefined||value===null)continue;for(const item of Array.isArray(value)?value:[value]){if(typeof item==='object')throw failure('Invalid query value: '+key,400,'INVALID_INPUT');url.searchParams.append(key,String(item));}}
  const headers={accept:'application/json',origin:'https://nextui.iparsian724.ir',referer:'https://nextui.iparsian724.ir/'};
  if(endpoint.auth)headers.sessionId=this.session.sessionId;
  if(body!==undefined)headers['content-type']='application/json';
  let response,text;
  try { response=await this.fetch(url,{method:endpoint.method,headers,body:body===undefined?undefined:JSON.stringify(body),redirect:'error',signal:AbortSignal.timeout(30000)});text=await response.text(); }
  catch { throw failure('Bank connection failed or timed out; check session/reports before retrying',502,'BANK_CONNECTION_FAILED'); }
  let data;try { data=JSON.parse(text); }catch { data=null; }
  if(!response.ok) {
   if(response.status===401){if(endpoint.auth){this.session.invalidatedAt=new Date().toISOString();this.save();throw failure('Bank session expired or invalid; run node cli.js login, then check-session.',401,'SESSION_EXPIRED',{data,nextAction:'login'});}throw failure('Bank authentication rejected; check login credentials and mobile verification',401,'LOGIN_FAILED',{data,nextAction:'login'});}
   // Do not expose arbitrary upstream messages, which can contain submitted secrets.
   throw failure('Bank HTTP '+response.status,response.status>=400&&response.status<=599?response.status:502,'BANK_HTTP_ERROR',{data});
  }
  if(!object(data)||typeof data.status!=='number')throw failure('Invalid JSON response from bank',502,'INVALID_BANK_RESPONSE');
  if(data.status!==0)throw failure('Bank operation failed',422,'BANK_REJECTED',{bankStatus:data.status,data});
  if(id==='User_Login'){
   if(typeof data.data?.sessionId!=='string'||!data.data.sessionId.trim())throw failure('Bank login returned no usable session',502,'INVALID_BANK_RESPONSE');
   this.session={sessionId:data.data.sessionId};this.save();
  }
  return data;
 }
}
module.exports={ParsianClient,endpoints};
require('./domain-client');
