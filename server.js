'use strict';
require('./env').loadEnv();
const express=require('express'),crypto=require('node:crypto');
const {ParsianClient}=require('./domain-client');
const {operations,cliHttpMap,optionsFor}=require('./cli-http-map');
function createApp(client=new ParsianClient(),key=process.env.PARSIAN_API_KEY||''){
 const app=express(),router=express.Router();app.disable('x-powered-by');
 app.use((req,res,next)=>{res.set('Cache-Control','no-store');if(['/health','/v1/health'].includes(req.path)||!key)return next();const a=Buffer.from(req.get('x-api-key')||''),b=Buffer.from(key);if(a.length===b.length&&crypto.timingSafeEqual(a,b))return next();res.status(401).json({error:'missing or invalid x-api-key'});});
 app.use(express.urlencoded({extended:false,limit:'32kb',parameterLimit:300}));
 app.use(express.json({limit:'32kb',strict:false}));
 let queue=Promise.resolve();const handle=fn=>(req,res,next)=>{const task=queue.then(()=>fn(req));queue=task.catch(()=>{});task.then(x=>res.json(x),next);};
 router.get('/health',(req,res)=>res.json({ok:true}));router.get('/capabilities',(req,res)=>res.json({basePath:'/v1',operations:cliHttpMap}));router.get('/openapi.json',(req,res)=>res.json(require('./local-openapi.json')));
 router.get(['/status','/auth/session'],handle(()=>client.status()));router.post(['/logout','/auth/logout'],handle(()=>client.logout()));
 router.post('/auth/session/check',handle(()=>client.checkSession()));router.post('/auth/session/ensure',handle(req=>client.ensureSession({username:process.env.PARSIAN_USER,password:process.env.PARSIAN_PASS,mobileNumber:process.env.PARSIAN_MOBILE,...(req.body||{})})));
 const special={'User_Login':input=>client.login({username:process.env.PARSIAN_USER,password:process.env.PARSIAN_PASS,mobileNumber:process.env.PARSIAN_MOBILE,...input}),'Otp_OtpGeneratorWithMobileNo':input=>client.requestOtp(input),'Otp_ValidateMobileNoWithOtp':input=>client.verifyOtp(input),'Inquiry_GetDeposits':()=>client.accounts(),'Inquiry_GetCardsWithAmount':()=>client.cards()};
 for(const op of operations){const route=op.path.replace(/\{([^}]+)\}/g,':$1');router[op.method.toLowerCase()](route,handle(req=>{if(op.target)req.body=require('./shortcuts').expand(req.body||{});if(req.is('application/x-www-form-urlencoded'))req.body=require('./transfer-input').formBody(req.body,require('./transfer-schema').normalizedSchema(op.command)||require('./data/endpoints.json').find(e=>e.id===op.endpoint).bodySchema);return op.mode?client.transferMode(op.target||op.command,req.body):special[op.endpoint]?special[op.endpoint](req.body||{}):({ 'transfer-instant':()=>client.transferInstant(req.body), 'transfer-instant-otp':()=>client.requestAccountTransferOtp('instant',req.body), 'transfer-iban-otp':()=>client.requestAccountTransferOtp('iban',req.body), 'transfer-iban':()=>client.transferIban(req.body), 'transfer-ach':()=>client.transferAch(req.body), 'transfer-card':()=>client.transferCard(req.body), 'transfer-otp':()=>client.requestCardTransferOtp(req.body), 'account-transfer-otp':()=>client.requestAccountTransferOtp('iban',req.body) }[op.command]||(()=>client.call(op.endpoint,optionsFor(op,op.method==='GET'?req.query:req.body,req.params))))();}));}
 for(const [route,method]of Object.entries({'/deposits':'accounts','/deposits/all':'accounts','/cards/all':'cards','/balance':'balances','/balances':'balances','/balances/cards':'cardBalances','/balances/deposits':'depositBalances'}))router.get(route,handle(()=>client[method]()));
 // Register before the parameter route so "latest" cannot be interpreted as an ID.

 app.get(['/v1/transactions/latest','/transactions/latest'],handle(req=>client.latestTransactions(req.query)));
 router.get('/transactions/find/:code',handle(req=>client.findTransaction(req.params.code,req.query)));
 router.post('/call/:id',handle(req=>client.call(req.params.id,req.body===undefined?{}:req.body)));
 app.use('/v1',router);app.use('/',router);app.use((req,res)=>res.status(404).json({error:'route not found'}));
 app.use((err,req,res,next)=>{const status=err.type==='entity.parse.failed'?400:err.type==='entity.too.large'?413:err.status>=400&&err.status<=599?err.status:err.name==='TypeError'?502:400;res.status(status).json({error:err.message,...(err.code?{code:err.code}:{}),...(err.nextAction?{nextAction:err.nextAction}:{}),...(err.bankStatus!==undefined?{bankStatus:err.bankStatus}:{})});});return app;
}
function createServer(client,key){return require('node:http').createServer(createApp(client,key));}
if(require.main===module){const host=process.env.PARSIAN_HOST||'127.0.0.1',port=Number(process.env.PARSIAN_PORT||process.env.PORT||3101);if(!['127.0.0.1','::1','localhost'].includes(host)&&!process.env.PARSIAN_API_KEY)throw Error('PARSIAN_API_KEY required outside localhost');createApp().listen(port,host,()=>console.log(`Parsian API: http://${host}:${port}/v1`));}
module.exports={createApp,createServer};
