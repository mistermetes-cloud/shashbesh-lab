"""Unauthenticated read-only release-link check. No login, writes or publication."""
import datetime,json,urllib.request,urllib.error
URLS=[('game','https://shashbesh.pages.dev'),('game_github','https://github.com/mistermetes-cloud/ShashBesh'),
      ('lab_planned','https://shashbesh-lab.pages.dev'),('lab_github_planned','https://github.com/mistermetes-cloud/shashbesh-lab')]
results=[]
for name,public in URLS:
    check=public.replace('https://github.com/','https://api.github.com/repos/') if 'github.com/' in public else public
    item={'resource':name,'public_url':public,'checked_url':check,'planned':name.startswith('lab')}
    try:
        with urllib.request.urlopen(urllib.request.Request(check,headers={'User-Agent':'ShashBesh-release-readiness-audit'}),timeout=20) as r:
            item.update(http_status=r.status,reachable=True)
            if 'api.github.com' in check:
                data=json.load(r);item.update(public_repository=not data['private'],issues_enabled=data['has_issues'],discussions_enabled=data['has_discussions'],detected_license=(data.get('license') or {}).get('spdx_id'))
    except Exception as e:item.update(http_status=getattr(e,'code',None),reachable=False,error=type(e).__name__)
    results.append(item)
print(json.dumps({'checked_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'results':results,
                 'lab_publication_confirmed':False,'note':'404 may also mean inaccessible/private; no authenticated lookup or publication was performed.'},indent=2))
