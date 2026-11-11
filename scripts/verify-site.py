"""Verify ES migration content, shared faculty profiles, and deployment paths."""
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlsplit,unquote
import json,re,sys,unicodedata
ROOT=Path(__file__).resolve().parents[1];OUT=ROOT/'_site';UNIT=ROOT.parent/'css-shared/src/data/units/es'
prefix=sys.argv[1].rstrip('/') if len(sys.argv)>1 else ''
class Scan(HTMLParser):
    def __init__(self):super().__init__();self.ids=[];self.urls=[];self.h1=0;self.parts=[];self.skip=[];self.description=False
    def handle_starttag(self,t,attrs):
        a=dict(attrs)
        if t in ['script','style','svg']:self.skip.append(t)
        if t=='h1':self.h1+=1
        if a.get('id'):self.ids.append(a['id'])
        if t=='meta' and a.get('name')=='description' and a.get('content'):self.description=True
        if t in ['a','img','script','link','iframe']:
            v=a.get('href') if t in ['a','link'] else a.get('src')
            if v:self.urls.append(v)
    def handle_endtag(self,t):
        if self.skip and self.skip[-1]==t:self.skip.pop()
    def handle_data(self,d):
        if not self.skip and d.strip():self.parts.append(re.sub(r'\s+','',unicodedata.normalize('NFC',d)))
def scan(s):p=Scan();p.feed(s);return p
pages={p:scan(p.read_text()) for p in OUT.rglob('*.html')};errors=[]
heroes=json.loads((UNIT/'heroes.json').read_text())['pages'];heroes.update(json.loads((UNIT/'faculty-heroes.json').read_text())['pages'])
for f,p in pages.items():
    rel=str(f.relative_to(OUT));raw=f.read_text();url='/' if rel=='index.html' else '/'+rel.removesuffix('index.html') if rel.endswith('/index.html') else '/'+rel
    if p.h1!=1:errors.append(rel+': H1 count')
    if not p.description:errors.append(rel+': missing description')
    if len(p.ids)!=len(set(p.ids)):errors.append(rel+': duplicate IDs')
    if url not in heroes or heroes[url]['image'] not in raw:errors.append(rel+': missing hero')
    if any(x in raw for x in ['{{','{%','wp-block-','gb-headline','logo-google-scholar','logo-research-gate','hawaii.edu/mailto:']):errors.append(rel+': imported/template remnants')
    for v in p.urls:
        u=urlsplit(v)
        if u.scheme or u.netloc:continue
        path=unquote(u.path)
        if prefix and path.startswith('/'):
            if not path.startswith(prefix+'/'):errors.append(rel+': missing prefix '+v);continue
            path=path[len(prefix):]
        target=OUT/path.lstrip('/') if path.startswith('/') else f.parent/path if path else f
        if target.is_dir():target=target/'index.html'
        if not target.exists():errors.append(rel+': missing '+v)
        elif u.fragment and target in pages and unquote(u.fragment) not in pages[target].ids:errors.append(rel+': missing anchor '+v)
expected=json.loads((ROOT/'reference/preserved-content.json').read_text())
for url,source in expected.items():
    rel='index.html' if url=='/' else url.lstrip('/')+'index.html' if url.endswith('/') else url.lstrip('/')
    out=''.join(pages[OUT/rel].parts);cursor=0
    for chunk in scan(source).parts:
        pos=out.find(chunk,cursor)
        if pos<0:errors.append(rel+': source text missing '+chunk[:70]);break
        cursor=pos+len(chunk)
    for tag in ['table','tr','td','th']:
        if len(re.findall('<'+tag+r'\b',source))>len(re.findall('<'+tag+r'\b',(OUT/rel).read_text())):errors.append(rel+': missing table structure '+tag)
faculty=json.loads((UNIT/'faculty.json').read_text())
for person in faculty:
    h=(OUT/person['url'].lstrip('/')).read_text()
    if 'profile-sidebar' not in h or 'profile-biography' not in h or person['photo'] not in h:errors.append(person['name']+': shared profile incomplete')
    for a in person.get('awards',[]):
        if a['name'] not in h or a.get('year','') not in h:errors.append(person['name']+': missing award')
if len(faculty)!=9 or len(pages)!=26:errors.append('Unexpected page/faculty count')
if errors:print('\n'.join(errors));sys.exit(1)
print(f'Checked {len(pages)} pages, 9 shared faculty bios, {len(expected)} preserved content bodies, links/assets/anchors, metadata, and heroes. Prefix: {prefix or "/"}.')
