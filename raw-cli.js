'use strict';
const fs=require('node:fs');
const {ParsianClient,endpoints}=require('./client');
const kebab=s=>s.replace(/([a-z0-9])([A-Z])/g,'$1-$2').replaceAll('_','-').toLowerCase();
const commands=endpoints.map(e=>({...e,command:kebab(e.id)}));
const aliases={login:'User_Login','otp-request':'Otp_OtpGeneratorWithMobileNo','otp-verify':'Otp_ValidateMobileNoWithOtp',cards:'Inquiry_GetCardsWithAmount',deposits:'Inquiry_GetDeposits',accounts:'General_GetCardAndDepositWithAmount',balance:'Inquiry_GetAccountBalance',transactions:'Inquiry_GetStatement',receipts:'Receipt_GetNextBankReceipts',receipt:'Receipt_GetNextBankReceiptByStatement_by_id','transfer-card':'Transfer_CardTransferWithoutLogin','transfer-ach':'Transfer_AchNormalTransfer','transfer-order':'Transfer_PostPaymentOrder','transfer-otp':'Otp_OtpGenerateForAccountTransfer','card-otp':'Otp_ShetabOtpSmsV2','iban-inquiry':'Inquiry_IbanEnquiry','card-owner':'Inquiry_GetCardOwnerWithoutLogin','card-iban':'Inquiry_GetIbanFromCard'};
const localAliases=Object.fromEntries(require('./cli-http-map').operations.map(o=>[o.command,o.endpoint]));
Object.assign(aliases,localAliases);
const find=s=>commands.find(c=>c.command===s||c.id===s||c.id===aliases[s]);
function help(e){const fields=s=>Object.entries(s.properties||{}).flatMap(([key,value])=>value.type==='object'?fields(value).map(k=>key+'.'+k):[key]);return e?[e.command,e.id,e.method+' '+e.path,'Bank session: '+e.auth,'Fields: '+fields(e.bodySchema).map(k=>'--'+k).join(' '),'Query: '+e.queryKeys.map(k=>'--'+k).join(' '),'Use --field VALUE; nested fields: --parent.child VALUE; arrays: repeat the option.','--dry-run sends nothing; --json-errors prints structured errors.'].join('\n'):['Parsian CLI','help [COMMAND] | endpoints | status | logout','call ENDPOINT_ID --field VALUE | COMMAND --field VALUE','Nested fields: --parent.child VALUE. Query/path fields are routed automatically.','--dry-run --json-errors','',...commands.map(c=>c.command+' '+Object.entries(aliases).filter(([,id])=>id===c.id).map(([k])=>'| '+k).join(' ')+' '+c.method+' '+c.path)].join('\n');}

function json(s){try{return JSON.parse(s.startsWith('@')?fs.readFileSync(s.slice(1),'utf8').replace(/^\uFEFF/,''):s);}catch{throw Error('Invalid JSON or unreadable JSON file');}}
function record(v){if(!v||typeof v!=='object'||Array.isArray(v)||Object.keys(v).some(k=>['__proto__','constructor','prototype'].includes(k)))throw Error('Expected a JSON object with valid keys');return v;}
async function run(argv,{clientFactory=()=>new ParsianClient()}={}){
 const args=argv.filter(x=>x!=='--json-errors'),command=args.shift()||'help';
 if(['help','--help','-h'].includes(command)){if(args.length>1||args.length&&!find(args[0]))throw Error('Unknown help command');return help(find(args[0]));}
 if(command==='endpoints'){if(args.length)throw Error('Unexpected argument');return commands;}
 if(['status','logout'].includes(command)){if(args[0]==='--help')return 'node cli.js '+command;if(args.length)throw Error('Unexpected argument');return clientFactory()[command]();}
 const e=find(command==='call'?args.shift():command);if(!e)throw Error('Unknown command or endpoint; use --help');
 if(args.includes('--help')||args.includes('-h'))return help(e);
 let opts={},dry=false;if(args[0]&&!args[0].startsWith('--'))opts=record(json(args.shift()));
 if(Object.keys(opts).some(k=>!['body','query','params'].includes(k)))throw Error('Unknown option key');
 while(args.length){const flag=args.shift();if(flag==='--dry-run'){dry=true;continue;}if(!flag.startsWith('--')||!args.length||args[0].startsWith('--'))throw Error('Missing value or unexpected argument');const value=args.shift(),key=flag.slice(2);if(['body','query','params'].includes(key)){opts[key]=json(value);continue;}
 const input=require('./transfer-input');const paramKeys=[...e.path.matchAll(/\{([^}]+)\}/g)].map(m=>m[1]);const param=paramKeys.find(k=>k===key||input.kebab(k)===key);const query=e.queryKeys.find(k=>k===key||input.kebab(k)===key);if(param){opts.params??={};opts.params[param]=value;continue;}if(query){opts.query??={};opts.query[query]=value;continue;}
 const first=key.split('.')[0],props=input.properties(e.bodySchema);if(e.bodySchema.type!=='array'&&!Object.keys(props).some(k=>k===first||input.kebab(k)===first))throw Error('Unknown flag: '+flag);
 opts._fields??={};if(Object.hasOwn(opts._fields,key))opts._fields[key]=Array.isArray(opts._fields[key])?[...opts._fields[key],value]:[opts._fields[key],value];else opts._fields[key]=value;
 }
 if(opts._fields){if(opts.body!==undefined)throw Error('Conflicting input formats');opts.body=require('./transfer-input').fieldsBody(opts._fields,e.bodySchema);delete opts._fields;}

 if(opts.query!==undefined)record(opts.query);if(opts.params!==undefined)record(opts.params);
 if(opts.body===undefined&&Object.hasOwn(e,'defaultBody'))opts.body=e.defaultBody;
 if(e.hasBody&&opts.body===undefined)throw Error('Request fields required; use COMMAND --help');
 for(const [,key]of e.path.matchAll(/\{([^}]+)\}/g))if(opts.params?.[key]===undefined)throw Error('Missing path parameter: '+key);
 if(dry)return {endpoint:e.id,method:e.method,path:e.path,auth:e.auth,options:opts};return clientFactory().call(e.id,opts);
}
if(require.main===module)run(process.argv.slice(2)).then(x=>{if(x!==undefined)console.log(typeof x==='string'?x:JSON.stringify(x,null,2));}).catch(e=>{console.error(process.argv.includes('--json-errors')?JSON.stringify({error:e.message,...(e.status?{status:e.status}:{}),...(e.bankStatus!==undefined?{bankStatus:e.bankStatus}:{})}):e.message);process.exitCode=1;});
module.exports={run,commands,aliases,help,readJson:json};
