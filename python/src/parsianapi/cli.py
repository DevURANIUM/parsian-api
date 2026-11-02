from __future__ import annotations
import argparse
import asyncio
import getpass
import json
import os
import sys
from typing import Any
from . import Client, ParsianError
from ._core import OPERATIONS, configuration, _properties, _normal

_SIMPLE = {'pol','sheba','pol-sms','sheba-sms','pol-code','sheba-code'}

def _parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog='parsian-api', description='Python CLI for your running Parsian HTTP service')
    parser.add_argument('--base-url')
    parser.add_argument('--api-key')
    parser.add_argument('--env-file', help='Explicit .env file; defaults to .env in current directory')
    parser.add_argument('--json-errors', action='store_true')
    sub = parser.add_subparsers(dest='command', required=True)
    for op in OPERATIONS:
        p = sub.add_parser(op['command'], help=op['method']+' '+op['path'])
        p.add_argument('values', nargs='*', metavar='VALUE', help='Simple transfers: ACCOUNT IBAN AMOUNT; transactions: ACCOUNT PAGE SIZE')
        p.add_argument('--field', action='append', default=[], metavar='NAME=VALUE', help='Advanced field; snake_case is accepted')
        p.add_argument('--amount', type=int)
        p.add_argument('--account')
        p.add_argument('--iban')
        p.add_argument('--reason')
        p.add_argument('--branch')
        p.add_argument('--password', help='Omit to use a hidden prompt')
        p.add_argument('--username')
        p.add_argument('--mobile')
        p.add_argument('--customer')
        p.add_argument('--page', type=int)
        p.add_argument('--size', type=int)
        p.add_argument('--limit', type=int)
    return parser

def main(argv: list[str] | None = None) -> int:
    args = _parser().parse_args(argv)
    try:
        settings = configuration(args.env_file)
        with Client(args.base_url, args.api_key, env_file=args.env_file) as client:
            fields: dict[str, Any] = {}
            for item in args.field:
                key, separator, value = item.partition('=')
                if not separator or not key or key in fields:
                    raise ValueError('Use a unique --field NAME=VALUE')
                parts=key.split('.')
                target=fields
                for part in parts[:-1]:
                    if part in ('__proto__','constructor','prototype'): raise ValueError('Invalid field path')
                    target=target.setdefault(part,{})
                if parts[-1] in target: raise ValueError('Duplicate field')
                target[parts[-1]]=value
            if args.command == 'login':
                if len(args.values)>2:
                    raise ValueError('Usage: login [username] [password]')
                username = args.username or (args.values[0] if args.values else None) or settings.get('PARSIAN_USER') or input('Username: ')
                password = args.password or (args.values[1] if len(args.values)>1 else None) or settings.get('PARSIAN_PASS') or getpass.getpass('Password: ')
                mobile = args.mobile or settings.get('PARSIAN_MOBILE') or input('Mobile number: ')
                result = client.login(username,password,mobile)
            elif args.command in _SIMPLE:
                if len(args.values) not in (0,3):
                    raise ValueError('Usage: '+args.command+' ACCOUNT IBAN AMOUNT')
                account = args.account or (args.values[0] if args.values else None) or settings.get('PARSIAN_ACCOUNT') or input('Source account: ')
                iban = args.iban or (args.values[1] if args.values else None) or input('Destination IBAN: ')
                amount = args.amount if args.amount is not None else int(args.values[2] if args.values else input('Amount (IRR): '))
                if args.command.endswith('-code'):
                    result = getattr(client,args.command.replace('-','_'))(account,iban,amount,username=args.username,customer_number=args.customer)
                else:
                    reason = args.reason or settings.get('PARSIAN_REASON') or input('Payment reason code: ')
                    branch = args.branch or settings.get('PARSIAN_BRANCH')
                    extra = {'branch_code':branch or input('Source branch code: ')} if args.command.startswith('pol') else {}
                    password = args.password or getpass.getpass('SMS code: ' if args.command.endswith('-sms') else 'Fixed transfer password: ')
                    result = getattr(client,args.command.replace('-','_'))(account,iban,amount,password,reason=reason,**extra)
            else:
                op = next(op for op in OPERATIONS if op['command']==args.command)
                path_names = [p['name'] for p in op['parameters'] if p['in']=='path']
                if args.command in ('otp','otp-request') and args.values:
                    if len(args.values)>2: raise ValueError('Too many OTP arguments')
                    if args.command=='otp':
                        fields['code']=args.values[0]
                        if len(args.values)>1:fields['mobileNo']=args.values[1]
                    else:fields['mobileNo']=args.values[0]
                elif args.command in ('transactions','transactions-latest') and args.values:
                    fields['account']=args.values[0]
                    if args.command=='transactions':
                        if len(args.values)>3:raise ValueError('Usage: transactions ACCOUNT [PAGE] [SIZE]')
                        if len(args.values)>1:fields['page']=int(args.values[1])
                        if len(args.values)>2:fields['size']=int(args.values[2])
                    else:
                        if len(args.values)>2:raise ValueError('Usage: transactions-latest ACCOUNT [LIMIT]')
                        if len(args.values)>1:fields['limit']=int(args.values[1])
                elif args.values:
                    if len(args.values)!=len(path_names):raise ValueError('Unexpected positional values; use --field NAME=VALUE')
                    fields.update(zip(path_names,args.values))
                for name in ('account','page','size','limit','amount','iban','reason','branch','username','mobile','customer','password'):
                    value=getattr(args,name)
                    if value is not None:
                        candidates={**_properties(op['bodySchema']),**{p['name']:p for p in op['parameters']}}
                        alternatives={'mobile':['mobileNo','mobileNumber'],'branch':['branch','branchCode'],'customer':['customer','customerNumber'],'account':['account','accountNumber','number']}.get(name,[name])
                        resolved=next((key for key in candidates if any(_normal(key)==_normal(alias) for alias in alternatives)),None)
                        if resolved is None: raise ValueError('Option not supported for this command: '+name)
                        fields[resolved]=value
                if args.command=='otp':
                    fields['code']=args.password or fields.get('code') or getpass.getpass('SMS code: ')
                    if args.mobile:fields['mobileNo']=args.mobile
                if args.command=='otp-request' and args.mobile:fields['mobileNo']=args.mobile
                if args.command=='otp':result=client.verify_otp(fields['code'],fields.get('mobileNo'))
                elif args.command=='otp-request':result=client.request_otp(fields.get('mobileNo'))
                elif args.command=='transactions':result=client.transactions(**fields)
                elif args.command=='transactions-latest':result=client.latest_transactions(**fields)
                else:result=client.operation(args.command,**fields)
            print(json.dumps(result,ensure_ascii=False,indent=2))
        return 0
    except (ParsianError,ValueError,OSError,EOFError) as error:
        info={'error':str(error)}
        for source,target in [('status_code','status'),('code','code'),('next_action','nextAction'),('request_may_have_succeeded','requestMayHaveSucceeded')]:
            if getattr(error,source,None) is not None:info[target]=getattr(error,source)
        print(json.dumps(info,ensure_ascii=False) if args.json_errors else info['error'],file=sys.stderr)
        return 1

if __name__=='__main__':
    raise SystemExit(main())
