"""Read-only source/history audit. Reports locations and counts, never secret values."""
from __future__ import annotations
import hashlib,json,pathlib,re,subprocess
ROOT=pathlib.Path(__file__).resolve().parents[2]
PATTERNS={
 'private_key':rb'-----BEGIN (?:RSA |OPENSSH |EC )?PRIVATE KEY-----',
 'aws_access_key':rb'AKIA[0-9A-Z]{16}',
 'github_token':rb'gh[pousr]_[A-Za-z0-9]{30,}',
 'github_fine_grained':rb'github_pat_[A-Za-z0-9_]{50,}',
 'credential_url':rb'https?://[^/\s:@]+:[^/\s@]+@',
}
DENIED_SUFFIX={'.sqlite','.sqlite3','.db','.log','.tgz','.zip','.pem','.key','.pyc'}


def git(*args):return subprocess.check_output(['git','-C',str(ROOT),*args])
def scan(data):return [name for name,pattern in PATTERNS.items() if re.search(pattern,data)]
def main():
 current=set(git('ls-files').decode().splitlines())|set(git('ls-files','--others','--exclude-standard').decode().splitlines())
 findings=[];exposed=[]
 for name in sorted(current):
  p=ROOT/name
  if not p.is_file():continue
  data=p.read_bytes();hits=scan(data)
  if hits:findings.append({'path':name,'patterns':hits})
  if p.suffix in DENIED_SUFFIX or data.startswith(b'SQLite format 3'):exposed.append(name)
 objects={}
 for line in git('rev-list','--objects','--all').decode().splitlines():
  bits=line.split(' ',1)
  if len(bits)==2:objects[bits[0]]=bits[1]
 history_findings=[];history_data=[];blobs=0
 for oid,name in objects.items():
  if git('cat-file','-t',oid).strip()!=b'blob':continue
  blobs+=1;data=git('cat-file','blob',oid);hits=scan(data)
  if hits:history_findings.append({'object':oid,'path':name,'patterns':hits})
  if pathlib.Path(name).suffix in DENIED_SUFFIX or data.startswith(b'SQLite format 3'):history_data.append(name)
 private_docs=sorted({name for name in objects.values() if name.startswith(('docs/engineering-review/','docs/research/','docs/L2_'))})
 emails=set(git('log','--all','--format=%ae%n%ce').decode().splitlines())
 nontechnical=sum(not (e.endswith('@users.noreply.github.com') or e.endswith('@localhost')) for e in emails)
 result={'head':git('rev-parse','HEAD').decode().strip(),'commits':int(git('rev-list','--all','--count')),
         'current_files':len(current),'history_blobs':blobs,'high_confidence_current_findings':findings,
         'high_confidence_history_findings':history_findings,'forbidden_current_artifacts':exposed,
         'forbidden_history_artifacts':sorted(set(history_data)),
         'private_history_document_count':len(private_docs),'unreviewed_commit_contact_identity_count':nontechnical,
         'history_publication_approved':False,'export_policy':'fresh allowlisted source export; never publish this .git history',
         'limitations':'Pattern scan is not proof of absence; owner provenance, contacts and all selected release files still require review.'}
 print(json.dumps(result,indent=2))


if __name__=='__main__':main()
