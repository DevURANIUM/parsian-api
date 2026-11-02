'use strict';
const transfer=require('./transfer');
const routes=[
 {command:'transfer-instant-fixed',path:'/transfers/fixed/instant',kind:'instant',mode:'fixed',step:'submit',endpoint:'Transfer_PostPaymentOrder',title:'پل با رمز ثابت'},
 {command:'transfer-iban-fixed',path:'/transfers/fixed/iban',kind:'iban',mode:'fixed',step:'submit',endpoint:'Transfer_AchNormalTransfer',title:'شبا با رمز ثابت'},
 {command:'transfer-instant-sms-request',path:'/transfers/sms/instant/otp',kind:'instant',mode:'sms',step:'otp',endpoint:'Otp_OtpGenerateForAccountTransfer',title:'دریافت رمز پیامکی پل'},
 {command:'transfer-instant-sms',path:'/transfers/sms/instant',kind:'instant',mode:'sms',step:'submit',endpoint:'Transfer_PostPaymentOrder',title:'پل با رمز پیامکی'},
 {command:'transfer-iban-sms-request',path:'/transfers/sms/iban/otp',kind:'iban',mode:'sms',step:'otp',endpoint:'Otp_OtpGenerateForAccountTransfer',title:'دریافت رمز پیامکی شبا'},
 {command:'transfer-iban-sms',path:'/transfers/sms/iban',kind:'iban',mode:'sms',step:'submit',endpoint:'Transfer_AchNormalTransfer',title:'شبا با رمز پیامکی'}
].map(route=>({...route,method:'POST',group:route.mode==='fixed'?'transfers-fixed':'transfers-sms'}));
function planFor(route,input,context={}){
 if(!input||typeof input!=='object'||Array.isArray(input))throw Object.assign(Error('Transfer body must be an object'),{status:400,code:'INVALID_TRANSFER_INPUT'});
 if(input.passwordMode!==undefined&&input.passwordMode!==route.mode)throw Object.assign(Error('passwordMode must be '+route.mode+' for this route'),{status:400,code:'PASSWORD_MODE_MISMATCH'});
 if(route.step==='otp'){
  if(input.password!==undefined)throw Object.assign(Error('Do not send password when requesting SMS'),{status:400,code:'INVALID_TRANSFER_INPUT'});
  return transfer.accountOtp(route.kind,{username:context.username,customerNumber:context.customerNumber,...input});
 }
 return transfer.accountTransfer(route.kind,{...input,passwordMode:route.mode});
}
module.exports={routes,planFor};
