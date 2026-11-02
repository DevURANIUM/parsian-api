'use strict';
const path=require('node:path');
function loadEnv(file=path.join(__dirname,'.env')){try{process.loadEnvFile(file);}catch(error){if(error.code!=='ENOENT')throw Error('Cannot load .env; check its format and permissions');}}
module.exports={loadEnv};
