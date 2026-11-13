
(function(){
  var t=document.getElementById('tsel');
  if(t){t.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;
    t.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});
    document.querySelectorAll('#dash tbody').forEach(function(tb){tb.hidden=tb.getAttribute('data-t')!==b.getAttribute('data-t')});});}
  var y=document.getElementById('ysel');
  if(y){var ids=['a-pre','a-live','a-rent','b-all'];
    var show=function(k){ids.forEach(function(i){var el=document.getElementById(i);if(el)el.closest('.tablewrap').hidden=(k!=='all'&&k!==i)});};
    show('a-pre');
    y.addEventListener('click',function(ev){var b=ev.target.closest('button');if(!b)return;
      y.querySelectorAll('button').forEach(function(x){x.classList.toggle('on',x===b)});show(b.getAttribute('data-y'));});}
  var sg=document.getElementById('sgwrap');
  if(sg){var KEY='tino1-review-choices';
    var load=function(){try{return JSON.parse(localStorage.getItem(KEY)||'{}')}catch(err){return{}}};
    var save=function(o){try{localStorage.setItem(KEY,JSON.stringify(o))}catch(err){}};
    var st=load();
    var refresh=function(){var n=0,a=0,h=0,r=0,u=0;
      Array.prototype.forEach.call(sg.querySelectorAll('select.sg'),function(s){
        var v=st[s.getAttribute('data-id')]||'';s.value=v;n++;
        if(v==='Adopt')a++;else if(v==='Hold')h++;else if(v==='Reject')r++;else u++;});
      var path=st['path']||'';
      Array.prototype.forEach.call(sg.querySelectorAll('input.pth'),function(rb){rb.checked=(rb.value===path)});
      var el=document.getElementById('sgsum');
      if(el){el.textContent=n+' suggestions: '+a+' adopted, '+h+' on hold, '+r+' rejected, '+u+' not yet reviewed. '+
        (path?'Implementation path chosen: '+path+'. ':'No implementation path chosen yet. ')+
        'Your choices are saved in this browser only and are not sent anywhere. Implement nothing until every adopted suggestion has been reviewed against the Flagged for Review page.';}};
    sg.addEventListener('change',function(ev){var t=ev.target;
      if(t.tagName==='SELECT'&&t.getAttribute('class')==='sg'){st[t.getAttribute('data-id')]=t.value;}
      else if(t.type==='radio'&&t.getAttribute('class')==='pth'){st['path']=t.value;}
      save(st);refresh();});
    var rb=document.getElementById('sgreset');
    if(rb){rb.addEventListener('click',function(){st={};save(st);refresh();});}
    refresh();}
})();
