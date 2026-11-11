from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlparse
import re
root=Path(__file__).parent/'public'
allowed={'www.boe.ca.gov','www.irs.gov','www.sco.ca.gov','www.sf.gov','www.cpuc.ca.gov','www.insurance.ca.gov','www.bls.gov','fred.stlouisfed.org','www.bea.gov','leginfo.legislature.ca.gov','asr.santaclaracounty.gov','sftreasurer.org','www.ftb.ca.gov','www.investor.gov'}
class Check(HTMLParser):
 def __init__(self): super().__init__(); self.in_row=False; self.header=False; self.sourced=False; self.rows=0; self.links=[]
 def handle_starttag(self,tag,attrs):
  a=dict(attrs)
  if tag=='tr': self.in_row=True; self.header=False; self.sourced=False
  if self.in_row and tag=='th': self.header=True
  if tag in ('a','link','script','img'):
   u=a.get('href') or a.get('src')
   if not u:return
   if u.startswith('https://'):
    assert urlparse(u).hostname in allowed, u
    if self.in_row:self.sourced=True
   elif not u.startswith('#'):
    self.links.append(u.split('#')[0])
 def handle_endtag(self,tag):
  if tag=='tr':
   if not self.header: assert self.sourced,'unsourced table row'; self.rows+=1
   self.in_row=False
files=list(root.glob('*.html')); assert len(files)==8
rows=0
for f in files:
 text=f.read_text(); assert 'noindex,nofollow' in text
 for token in ('3,100,000','1,800,000','550,540','539,740','114,250','7,150','85,800','94122','95014'):
  assert token not in text, (f,token)
 p=Check();p.feed(text); rows+=p.rows
 for u in p.links: assert (root/u).is_file(),(f,u)
print(f'PASS: {len(files)} pages, {rows} sourced rows, internal links and privacy fingerprints checked')
