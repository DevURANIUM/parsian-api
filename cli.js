#!/usr/bin/env node
'use strict';
require('./env').loadEnv();
const raw=require('./raw-cli');
const transfers=require('./transfer');
const {ParsianClient}=require('./domain-client');
const {operations,cliHttpMap,optionsFor}=require('./cli-http-map');
const readline=require('node:readline/promises');const {Writable}=require('node:stream');
async function ask(label,hidden=false){if(!process.stdin.isTTY)throw Error('Interactive terminal required; use command arguments or environment credentials');const output=hidden?new Writable({write(c,e,done){done();}}):process.stderr;const rl=readline.createInterface({input:process.stdin,output,terminal:true});try{if(hidden)process.stderr.write(label);return await rl.question(hidden?'':label);}finally{rl.close();if(hidden){output.end();process.stderr.write('\n');}}}
const HELP=`Simple transfers: pol ACCOUNT IBAN AMOUNT | sheba ACCOUNT IBAN AMOUNT
SMS: pol-code / sheba-code to request; pol-sms / sheba-sms to submit
Usage: node cli.js [--json-errors] COMMAND
login [username] [password]     PARSIAN_USER/PARSIAN_PASS/PARSIAN_MOBILE or prompts
otp-request [mobileNo]         Send mobile verification OTP
otp [code] [mobileNo]           Verify mobile OTP; sends code as signedPassword
status | check-session | ensure-session | logout
accounts | deposits | cards | cards-all | deposits-all | accounts-with-cards
balance [account] | balance-deposits | balance-cards
transactions <account> [page] [size] | transactions [page] [size]
  Default account: PARSIAN_ACCOUNT or the only bank deposit. Last 30 days by default.
transactions-latest <account> [limit]
transaction <statementId> | receipt <statementId>
transaction-find <code> <account>
iban <cardNumber> | owner <iban>
transfer-card SOURCE_CARD DEST_CARD AMOUNT --cvv2 CVV2 --expiry YYMM --transaction-number ID --mobile-number MOBILE
transfer-iban | transfer-ach | transfer-instant ACCOUNT IBAN AMOUNT --reason CODE --password-mode sms|fixed
transfer-instant-otp | transfer-iban-otp ACCOUNT IBAN AMOUNT --username USER --customer-number CIF
transfer-otp SOURCE_CARD DEST_CARD AMOUNT --tracking-number ID
Fixed: transfer-instant-fixed | transfer-iban-fixed ACCOUNT IBAN AMOUNT --reason CODE [--branch-code BRANCH]
SMS request: transfer-instant-sms-request | transfer-iban-sms-request ACCOUNT IBAN AMOUNT
SMS submit: transfer-instant-sms | transfer-iban-sms ACCOUNT IBAN AMOUNT --reason CODE [--branch-code BRANCH]
Other commands: --help for all upstream and local commands.
Pass fields as --field VALUE; nested fields as --parent.child VALUE. --dry-run sends nothing.
No HTTP server required. HTTP uses /v1 and x-api-key like Saman.
Dates and transfer payloads follow Parsian HAR, not Saman.
`;
async function run(argv,deps={}){
 const args=argv.filter(x=>x!=='--json-errors'),cmd=args.shift()||'help';const factory=deps.clientFactory||(()=>new ParsianClient());const prompt=deps.prompt||ask;const env=deps.env||process.env;
 if(['help','--help','-h'].includes(cmd)&&!args.length)return HELP+'\n'+raw.help()+'\n\nLocal mappings:\n'+cliHttpMap.map(x=>x.command+' '+x.method+' '+x.path).join('\n');
 if(cmd==='help'&&args.length===1&&require('./transfer-modes').routes.some(route=>route.command===args[0]))return run([args[0],'--help'],deps);
 const short=require('./shortcuts').routes.find(r=>r.command===cmd);
 if(short){
  if(args.includes('--help'))return 'node cli.js '+cmd+' ACCOUNT IBAN AMOUNT [options]';
  let shortArgs=args;if(args.length===2&&/^IR/.test(args[0]))shortArgs=[env.PARSIAN_ACCOUNT||await prompt('Source account: '),...args];const parsed=require('./transfer-input').parseArgs(shortArgs);let body=require('./shortcuts').expand(parsed.body);if(!parsed.dryRun){body.sourceAccount??=env.PARSIAN_ACCOUNT||await prompt('Source account: ');body.iban??=await prompt('Destination IBAN: ');if(body.amount===undefined)body.amount=require('./transfer-input').formBody({amount:await prompt('Amount (IRR): ')}).amount;}
  if(short.step==='submit'){body.reason??=env.PARSIAN_REASON;if(!body.reason&&!parsed.dryRun)body.reason=await prompt('Payment reason code: ');if(short.kind==='instant'){body.branchCode??=env.PARSIAN_BRANCH;if(!body.branchCode&&!parsed.dryRun)body.branchCode=await prompt('Source branch code: ');}}
  const flags=Object.entries(body).flatMap(([key,value])=>['--'+require('./transfer-input').kebab(key),String(value)]);
  return run([short.target,...flags,...(parsed.dryRun?['--dry-run']:[])],deps);
 }
 const modeRoute=require('./transfer-modes').routes.find(route=>route.command===cmd);
 if(modeRoute){
  if(args.includes('--help')||args.includes('-h'))return modeRoute.title+'\nUsage: '+cmd+' SOURCE IBAN AMOUNT --reason CODE [--branch-code CODE] [--password VALUE] [--dry-run]\nThe command binds passwordMode='+modeRoute.mode+'. Conflicting modes are rejected.';
  let {body,dryRun}=require('./transfer-input').parseArgs(args,{schema:require('./transfer-schema').normalizedSchema(cmd)});
  if(modeRoute.step==='submit'&&!body.password){require('./transfer-modes').planFor(modeRoute,{...body,password:'PREVIEW_ONLY'});if(dryRun)body.password='PREVIEW_ONLY';else body.password=await prompt(modeRoute.mode==='fixed'?'Fixed transfer password: ':'SMS code: ',true);}
  let client;if(modeRoute.step==='otp'&&!dryRun&&body&&(!body.username||!body.customerNumber))client=factory();
  const plan=require('./transfer-modes').planFor(modeRoute,body,client?.session);
  if(dryRun)return transfers.preview(plan);return (client||factory()).call(plan.endpoint,plan.options);
 }
 const transferNames={ 'transfer-pol':'instant','transfer-instant':'instant','transfer-iban':'iban','transfer-ach':'iban','transfer-card':'card','transfer-instant-otp':'instant-otp','transfer-pol-otp':'instant-otp','transfer-iban-otp':'iban-otp','account-transfer-otp':'iban-otp','transfer-otp':'card-otp','card-otp':'card-otp' };
 if(transferNames[cmd]&&args.length&&!args.includes('--help')){
  let {body,dryRun}=require('./transfer-input').parseArgs(args,{schema:require('./transfer-schema').normalizedSchema(cmd)||{},card:['transfer-card','transfer-otp','card-otp'].includes(cmd)});
  const kind=transferNames[cmd];let plan,client;if(transfers.normalized(body)&&kind.endsWith('-otp')&&kind!=='card-otp'&&!dryRun&&(!body.username||!body.customerNumber)){client=factory();body={username:client.session?.username,customerNumber:client.session?.customerNumber,...body};}
  if(transfers.normalized(body)&&!kind.endsWith('-otp')&&!body.password){if(kind==='card')transfers.cardTransfer({...body,password:'PREVIEW_ONLY'});else transfers.accountTransfer(kind,{...body,password:'PREVIEW_ONLY'});body.password=dryRun?'PREVIEW_ONLY':await prompt('Transfer password: ',true);}
  if(transfers.normalized(body))plan=kind==='card'?transfers.cardTransfer(body):kind==='card-otp'?transfers.cardOtp(body):kind.endsWith('-otp')?transfers.accountOtp(kind.slice(0,-4),body):transfers.accountTransfer(kind,body);
  else{const endpoint=kind==='instant'?'Transfer_PostPaymentOrder':kind==='card'?'Transfer_CardTransferWithoutLogin':kind==='card-otp'?'Otp_ShetabOtpSmsV2':kind.endsWith('-otp')?'Otp_OtpGenerateForAccountTransfer':cmd==='transfer-iban'?'Transfer_PostPaymentOrder':'Transfer_AchNormalTransfer';if(body===undefined)throw Error('Request body required');plan={endpoint,options:{body}};}
  if(dryRun)return transfers.preview(plan);return (client||factory()).call(plan.endpoint,plan.options);
 }
 if(transferNames[cmd]&&args.includes('--help'))return 'Usage: '+cmd+' SOURCE IBAN AMOUNT --reason CODE [--branch-code CODE] [--password VALUE] [--dry-run]\npasswordMode: sms | fixed; password: SMS code or fixed account password. Separate OTP command sends SMS. Instant requires branchCode and reason. See /parsian/#cli.';
 if(['transactions','transactions-latest'].includes(cmd)&&args[0]?.startsWith('--')&&!args.includes('--body')&&!args.includes('--help')){
  const schema={type:'object',properties:{...require('./data/endpoints.json').find(e=>e.id==='Inquiry_GetStatement').bodySchema.properties,account:{type:'string'},page:{type:'integer'},size:{type:'integer'},limit:{type:'integer'}}};const parsed=require('./transfer-input').parseArgs(args,{schema});const query=parsed.body;for(const key of Object.keys(query))if(!Object.hasOwn(schema.properties,key))throw Error('Unknown transaction option: '+key);
  if(parsed.dryRun){const {limit,...rest}=query;return {endpoint:'Inquiry_GetStatement',options:{body:require('./transactions').transactionQuery(cmd==='transactions-latest'?{...rest,offset:0,length:limit??10}:query)},dryRun:true};}
  return cmd==='transactions'?factory().transactions(query):factory().latestTransactions(query);
 }
 if(cmd==='transaction-find'){const code=args.shift();let account=args.shift();if(account==='--account')account=args.shift();if(!code||!account||args.length)throw Error('Usage: transaction-find code account');return factory().findTransaction(code,{account});}
 if(args.includes('--help')&&['check-session','ensure-session','balance','balance-cards','balance-deposits','transactions-latest'].includes(cmd))return HELP;
 if(args.some(x=>x.startsWith('--'))||args[0]?.startsWith('{')||args[0]?.startsWith('@')){
  if(['balance','balance-cards','balance-deposits'].includes(cmd)&&!args.includes('--account-number')){
   if(args.includes('--help'))return HELP;
  }else return raw.run(argv,{clientFactory:factory});
 }
 const op=operations.find(o=>o.command===cmd);
 if(cmd==='check-session'||cmd==='ensure-session'){if(args.length)throw Error('Unexpected argument');const c=factory();return cmd==='check-session'?c.checkSession():c.ensureSession(env.PARSIAN_USER&&env.PARSIAN_PASS?{username:env.PARSIAN_USER,password:env.PARSIAN_PASS,mobileNumber:env.PARSIAN_MOBILE}:{});}
 if(cmd==='login'){if(args.length>2)throw Error('Usage: login [username] [password]');const username=args[0]||env.PARSIAN_USER||await prompt('Username: '),password=args[1]||env.PARSIAN_PASS||await prompt('Password: ',true),mobileNumber=env.PARSIAN_MOBILE||await prompt('Mobile number: ');return factory().login({username,password,mobileNumber});}
 if(cmd==='otp-request'){if(args.length>1)throw Error('Usage: otp-request [mobileNo]');return factory().requestOtp({mobileNo:args[0]||env.PARSIAN_MOBILE||await prompt('Mobile number: ')});}
 if(cmd==='otp'){if(args.length>2)throw Error('Usage: otp [signedPassword] [mobileNo]');const c=factory();return c.verifyOtp({code:args[0]||await prompt('SMS code: ',true),mobileNo:args[1]||env.PARSIAN_MOBILE||c.session?.pendingMobile||await prompt('Mobile number: ')});}
 const methods={accounts:'accounts',deposits:'accounts','deposits-all':'accounts',cards:'cards','cards-all':'cards','accounts-with-cards':'balances','balance-deposits':'depositBalances','balance-cards':'cardBalances'};
 if(methods[cmd]){if(args.length)throw Error('Unexpected argument');return factory()[methods[cmd]]();}
 if(cmd==='balance'){if(args.length>1)throw Error('Usage: balance [account]');return args.length?factory().call('Inquiry_GetAccountBalance',{body:{accountNumber:args[0]}}):factory().balances();}
 if(['transactions','transactions-latest'].includes(cmd)){
  const c=factory();let account,page,size;
  if(cmd==='transactions'&&args.length<=2&&(!args.length||/^\d{1,4}$/.test(args[0]))){page=args[0]??0;size=args[1]??10;account=env.PARSIAN_ACCOUNT;if(!account){const result=await c.accounts();const deposits=result.deposits||result.data||[];if(deposits.length!==1)throw Error('Multiple or no accounts. Use transactions ACCOUNT PAGE SIZE or set PARSIAN_ACCOUNT.');account=deposits[0].depositNumber;}}
  else{if(!args[0]||args.length>(cmd==='transactions'?3:2))throw Error('Usage: '+cmd+' ACCOUNT [PAGE/LIMIT] [SIZE]');account=args[0];page=args[1]??0;size=args[2]??10;}
  return cmd==='transactions'?c.transactions({account,page,size}):c.latestTransactions({account,limit:args[1]??10});
 }
 if(['transaction','receipt'].includes(cmd)){if(args.length!==1)throw Error('Usage: '+cmd+' statementId');return factory().transactionDetail(args[0]);}
 if(['iban','owner','account-balance'].includes(cmd)){if(args.length!==1)throw Error('Usage: '+cmd+' number');return factory().call(op.endpoint,optionsFor(op,{},cmd==='owner'?{iban:args[0]}:{number:args[0]}));}
 if(op&&!args.length){const e=raw.commands.find(e=>e.id===op.endpoint);if(e.hasBody&&!Object.hasOwn(e,'defaultBody'))throw Error('Request fields required; use '+cmd+' --help');return factory().call(op.endpoint,optionsFor(op));}
 return raw.run(argv,{clientFactory:factory});
}
async function runCommand(argv,{client=new ParsianClient(),prompt=ask,out=x=>console.log(JSON.stringify(x,null,2)),note=x=>console.error(x),env=process.env}={}){const result=await run(argv,{clientFactory:()=>client,prompt,env});if(typeof result==='string')note(result);else if(result!==undefined)out(result);return result;}
if(require.main===module)runCommand(process.argv.slice(2)).catch(e=>{console.error(process.argv.includes('--json-errors')?JSON.stringify({error:e.message,status:e.status,bankStatus:e.bankStatus,code:e.code,nextAction:e.nextAction}):e.message);process.exitCode=1;});
module.exports={...raw,run,runCommand,HELP,ask};
