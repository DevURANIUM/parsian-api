"""Generate explicit sync/async endpoint methods and metadata from the local API contract."""
from pathlib import Path
import json,re
ROOT=Path(__file__).resolve().parents[2]
PACKAGE=ROOT/'python/src/parsianapi'
spec=json.loads((ROOT/'local-openapi.json').read_text(encoding='utf8'))
ops=[]
for path,methods in spec['paths'].items():
 for method,op in methods.items():
  ops.append({'command':op['summary'],'method':method.upper(),'path':path,'parameters':op.get('parameters',[]),'bodySchema':op.get('requestBody',{}).get('content',{}).get('application/json',{}).get('schema',{})})
(PACKAGE/'_operations.json').write_text(json.dumps(ops,indent=2,ensure_ascii=False)+'\n',encoding='utf8')
common=[
 ('login', 'username: str | None = None, password: str | None = None, mobile_number: str | None = None', "self.request('POST', '/auth/login', fields=_core.login_fields(self._settings,username,password,mobile_number))"),
 ('sign_in', 'username: str | None = None, password: str | None = None, mobile_number: str | None = None', 'self.login(username,password,mobile_number)'),
 ('request_otp', 'mobile_number: str | None = None', "self.request('POST','/auth/otp/request',fields=_core.clean({'mobileNo':mobile_number or self._settings.get('PARSIAN_MOBILE')}))"),
 ('verify_otp', 'code: str, mobile_number: str | None = None', "self.request('POST','/auth/otp',fields=_core.clean({'code':code,'mobileNo':mobile_number or self._settings.get('PARSIAN_MOBILE')}))"),
 ('ensure_session','username: str | None = None, password: str | None = None, mobile_number: str | None = None',"self.request('POST','/auth/session/ensure',fields=_core.clean({'username':username or self._settings.get('PARSIAN_USER'),'password':password or self._settings.get('PARSIAN_PASS'),'mobileNumber':mobile_number or self._settings.get('PARSIAN_MOBILE')}))"),
 ('transactions', 'account: str, page: int = 0, size: int = 10, **filters: Any', "self.operation('transactions',account=account,page=page,size=size,**filters)"),
 ('latest_transactions', 'account: str, limit: int = 10', "self.operation('transactions-latest',account=account,limit=limit)"),
 ('transaction', 'statement_id: str', "self.operation('transaction',id=statement_id)"),
 ('find_transaction', 'code: str, account: str, *, pages: int = 20, size: int = 50', "self.operation('transaction-find',code=code,account=account,pages=pages,size=size)"),
 ('iban','card_number: str',"self.operation('iban',number=card_number)"),
 ('owner','iban: str',"self.operation('owner',iban=iban)"),
 ('account_balance','account: str',"self.operation('account-balance',number=account)"),
 ('pol','account: str, iban: str, amount: int, password: str, *, reason: str, branch_code: str, **options: Any',"self.operation('pol',from_=account,to=iban,amount=_core.amount(amount),pass_=password,reason=reason,branch=branch_code,**options)"),
 ('sheba','account: str, iban: str, amount: int, password: str, *, reason: str, **options: Any',"self.operation('sheba',from_=account,to=iban,amount=_core.amount(amount),pass_=password,reason=reason,**options)"),
 ('pol_sms','account: str, iban: str, amount: int, code: str, *, reason: str, branch_code: str, **options: Any',"self.operation('pol-sms',from_=account,to=iban,amount=_core.amount(amount),pass_=code,reason=reason,branch=branch_code,**options)"),
 ('sheba_sms','account: str, iban: str, amount: int, code: str, *, reason: str, **options: Any',"self.operation('sheba-sms',from_=account,to=iban,amount=_core.amount(amount),pass_=code,reason=reason,**options)"),
 ('pol_code','account: str, iban: str, amount: int, *, username: str | None = None, customer_number: str | None = None',"self.operation('pol-code',from_=account,to=iban,amount=_core.amount(amount),user=username,customer=customer_number)"),
 ('sheba_code','account: str, iban: str, amount: int, *, username: str | None = None, customer_number: str | None = None',"self.operation('sheba-code',from_=account,to=iban,amount=_core.amount(amount),user=username,customer=customer_number)"),
 ('card_transfer','source_card: str, destination_card: str, amount: int, password: str, *, cvv2: str, expiry: str, transaction_number: str, mobile_number: str, **options: Any',"self.operation('transfer-card',source_card=source_card,destination_card=destination_card,amount=_core.amount(amount),password=password,cvv2=cvv2,expiry=expiry,transaction_number=transaction_number,mobile_number=mobile_number,**options)"),
 ('card_otp','source_card: str, destination_card: str, amount: int, tracking_number: str',"self.operation('transfer-otp',source_card=source_card,destination_card=destination_card,amount=_core.amount(amount),tracking_number=tracking_number)"),
]
for name,route in [('health','/health'),('accounts','/accounts'),('deposits','/deposits'),('cards','/cards'),('balance','/balance'),('status','/auth/session')]:common.append((name,'',f"self.request('GET',{route!r})"))
for name,route in [('check_session','/auth/session/check'),('logout','/auth/logout')]:common.append((name,'',f"self.request('POST',{route!r},fields={{}})"))
for asynchronous in [False,True]:
 class_name='AsyncMethods' if asynchronous else 'SyncMethods'
 lines=['# Generated by tools/generate.py; edit the generator, not this file.','from __future__ import annotations','from typing import Any','from . import _core','',f'class {class_name}:']
 names=set()
 for name,signature,expression in common:
  names.add(name)
  lines += [f'    {"async " if asynchronous else ""}def {name}(self{", " if signature else ""}{signature}) -> Any:',f'        """{name.replace("_"," ").capitalize()}; complete service response is preserved."""']
  if name in ['transactions','latest_transactions','find_transaction']:
   if name=='transactions':lines += ["        if isinstance(page,bool) or not isinstance(page,int) or page<0 or isinstance(size,bool) or not isinstance(size,int) or not 1<=size<=6000: raise ValueError('Invalid page or size')"]
   if name=='latest_transactions':lines += ["        if isinstance(limit,bool) or not isinstance(limit,int) or not 1<=limit<=6000: raise ValueError('Invalid limit')"]
  if name=='verify_otp':lines += ["        if not isinstance(code,str) or not code: raise ValueError('code must be a nonempty string')"]
  lines += [f'        return {"await " if asynchronous else ""}{expression}','']
 for op in ops:
  name=op['command'].replace('-','_')
  if name in names:continue
  names.add(name)
  lines += [f'    {"async " if asynchronous else ""}def {name}(self, **fields: Any) -> Any:',f'        """{op["method"]} {op["path"]}; field keywords accept snake_case."""',f'        return {"await " if asynchronous else ""}self.operation({op["command"]!r}, **fields)','']
 (PACKAGE/('_async_methods.py' if asynchronous else '_sync_methods.py')).write_text('\n'.join(lines)+'\n',encoding='utf8')
reference=['# Python method reference','','All methods exist on Client and AsyncClient; await async calls.','', '| Method | HTTP |', '| --- | --- |']
common_signatures={name:signature for name,signature,_ in common}
for op in ops:
 name=op['command'].replace('-','_');signature=common_signatures.get(name,'**fields').replace('|','\\|')
 reference.append(f'| `{name}({signature})` | `{op["method"]} {op["path"]}` |')
(ROOT/'python/docs').mkdir(exist_ok=True)
(ROOT/'python/docs/reference.md').write_text('\n'.join(reference)+'\n',encoding='utf8')
print(f'Generated {len(ops)} endpoint operations for sync and async clients')
