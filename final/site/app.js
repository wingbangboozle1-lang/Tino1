
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
})();
