'use strict';
// Local interface follows the Saman /v1 convention. Upstream contracts remain Parsian HAR contracts.
const definitions=[
 ['customer-config-public','POST','/customer/config','General_GetCustomerConfigDetailByCifWithOutSession'],['workflow-latest','POST','/workflow/latest','Workflow_GetLatestActiveInstance'],
 ['transfer-instant','POST','/transfers/instant','Transfer_PostPaymentOrder'],['transfer-instant-otp','POST','/transfers/instant/otp','Otp_OtpGenerateForAccountTransfer'],['transfer-iban-otp','POST','/transfers/iban/otp','Otp_OtpGenerateForAccountTransfer'],['transfer-order','POST','/transfers/order','Transfer_PostPaymentOrder'],
 ['validate-mobile','POST','/auth/mobile/validate','General_ValidateWhitelistedUser'],
 ['otp-request','POST','/auth/otp/request','Otp_OtpGeneratorWithMobileNo'],['otp','POST','/auth/otp','Otp_ValidateMobileNoWithOtp'],['login','POST','/auth/login','User_Login'],
 ['cards','GET','/cards','Inquiry_GetCardsWithAmount'],['accounts','GET','/accounts','Inquiry_GetDeposits'],['profile','POST','/profile','Inquiry_GetCustomerExtraData'],
 ['config','GET','/config','General_GetCustomerConfigDetailByCif'],['contacts','GET','/contacts','Inquiry_GetUserContactWithContactDetails'],
 ['workflow-active','GET','/workflow/active','Workflow_GetActiveInstances'],['requests','POST','/requests','MyRequest_GetMyRequests'],['cartable','POST','/cartable','Cartable_GetCartableRequests'],
 ['accounts-with-cards','GET','/accounts/with-cards','General_GetCardAndDepositWithAmount'],['home','GET','/home','General_GetHomePageServices'],
 ['wallet-token','POST','/wallet/token','Wallet_TokenExchange'],['banners','GET','/banners','General_GetBannersByMode'],['menus','GET','/menus','General_GetBottomTabMenus'],
 ['account-balance','GET','/accounts/{number}/balance','Inquiry_GetAccountBalance'],['transfer-limits','POST','/transfers/limits','Inquiry_GetModernGatewayNewServiceLimitation'],
 ['workflow-cancel','POST','/workflow/cancel','Workflow_CancelInstance'],['card-owner','POST','/transfers/card/owner','Inquiry_GetCardOwnerWithoutLogin'],
 ['iban','GET','/cards/{number}/iban','Inquiry_GetIbanFromCard'],['transfer-methods','POST','/transfers/methods','General_GetTransmissionMethod'],
 ['workflow-create','POST','/workflow/create','Workflow_createAndExecute'],['workflow-state','POST','/workflow/state','Workflow_InquiryState'],['workflow-event','POST','/workflow/event','Workflow_PublishEvent'],
 ['card-password-status','POST','/cards/password/status','otp_GetOfflinePasswordStatus'],['transfer-otp','POST','/transfers/card/otp','Otp_ShetabOtpSmsV2'],
 ['transfer-card','POST','/transfers/card','Transfer_CardTransferWithoutLogin'],['owner','GET','/owner/iban/{iban}','Inquiry_IbanEnquiry'],
 ['payment-id-check','POST','/payments/id/check','payment_PaymentIDCheckByCB'],['parameters','POST','/parameters','General_LoadGeneralParameter'],
 ['sayah-inquiry','POST','/transfers/sayah','Inquiry_SayahSystemCompatibilityInquiry'],['account-transfer-otp','POST','/transfers/account/otp','Otp_OtpGenerateForAccountTransfer'],
 ['transfer-iban','POST','/transfers/iban','Transfer_PostPaymentOrder'],['payment-orders','POST','/reports/payment-orders','Report_GetPaymentOrder'],
 ['transfer-ach','POST','/transfers/ach','Transfer_AchNormalTransfer'],['transactions','GET','/transactions','Inquiry_GetStatement'],
 ['balance-average','POST','/balances/average','Inquiry_GetMinBalanceAverage'],['transaction','GET','/transactions/{id}','Receipt_GetNextBankReceiptByStatement_by_id'],
 ['transfer-report','POST','/reports/transfers','Inquiry_AchTransferFullReport'],['receipts','POST','/receipts','Receipt_GetNextBankReceipts'],
 ['config-save','POST','/config','General_HandleCustomerConfigAndDetail'],['services','GET','/services','General_GetServicePageServices'],['customer-cards','GET','/customer/cards','card_getCustomerAccountAndCard']
];
const operations=definitions.map(([command,method,path,endpoint])=>({command,method,path,endpoint})).concat(require('./transfer-modes').routes,require('./shortcuts').routes);
const extra=[['status','GET','/auth/session'],['check-session','POST','/auth/session/check'],['ensure-session','POST','/auth/session/ensure'],['logout','POST','/auth/logout'],['deposits','GET','/deposits'],['cards-all','GET','/cards/all'],['deposits-all','GET','/deposits/all'],['balance','GET','/balance'],['balance-cards','GET','/balances/cards'],['balance-deposits','GET','/balances/deposits'],['transactions-latest','GET','/transactions/latest'],['transaction-find','GET','/transactions/find/{code}']].map(([command,method,path])=>({command,method,path}));
const cliHttpMap=[...operations,...extra].map(o=>({...o,path:'/v1'+o.path}));
function optionsFor(op,input={},params={}){
 let body=input,query={},pathParams={};
 if(op.endpoint==='Inquiry_GetAccountBalance')body={accountNumber:params.number};
 if(op.endpoint==='Inquiry_GetIbanFromCard')body={cardNumber:params.number};
 if(op.endpoint==='Inquiry_IbanEnquiry')body={iban:params.iban};
 if(op.endpoint==='Receipt_GetNextBankReceiptByStatement_by_id'){body=undefined;pathParams={statementId:params.id};}
 const e=require('./data/endpoints.json').find(e=>e.id===op.endpoint);
 for(const key of e.queryKeys)if(input?.[key]!==undefined)query[key]=input[key];
 if(!e.hasBody)body=undefined;else if(Object.hasOwn(e,'defaultBody'))body=e.defaultBody;
 if(op.endpoint==='Inquiry_GetStatement')body=require('./transactions').transactionQuery(input);
 return {body,query,params:pathParams};
}
module.exports={operations,cliHttpMap,optionsFor};
