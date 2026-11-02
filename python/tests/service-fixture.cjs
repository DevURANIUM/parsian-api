'use strict';
const fs=require('node:fs'),os=require('node:os'),path=require('node:path');
const {ParsianClient}=require('../../client');const {createApp}=require('../../server');
const dir=fs.mkdtempSync(path.join(os.tmpdir(),'parsian-sdk-integration-'));
const client=new ParsianClient({dataDir:dir,fetchImpl:async(url,options)=>{
 let data={received:options.body?JSON.parse(options.body):null,path:url.pathname};
 if(url.pathname.endsWith('/GetDeposits')||url.pathname.endsWith('/GetCardsWithAmount'))data=[];
 if(url.pathname.endsWith('/Login'))data={sessionId:'synthetic-session',customerNo:'synthetic-customer'};
 return Response.json({status:0,data,message:''});
}});
client.session={sessionId:'synthetic-session'};
const server=createApp(client,'fixture-service-key').listen(0,'127.0.0.1',()=>console.log(JSON.stringify({port:server.address().port})));
function stop(){server.close(()=>{fs.rmSync(dir,{recursive:true,force:true});process.exit(0);});}
for(const signal of ['SIGINT','SIGTERM'])process.once(signal,stop);
