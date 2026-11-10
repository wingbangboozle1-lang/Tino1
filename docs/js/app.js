// Minimal JS for charts and interactions
document.addEventListener('DOMContentLoaded',()=>{
  // Highlight active nav
  const path = location.pathname.split('/').pop() || 'index.html';
  document.querySelectorAll('.nav a').forEach(a=>{
    if(a.getAttribute('href')===path) a.classList.add('active');
    if(path==='' && a.getAttribute('href')==='index.html') a.classList.add('active');
  });
  // Charts
  const elCupertino = document.getElementById('chart-cupertino');
  if(elCupertino && window.Chart){
    const labels = [];
    const cupValue = [];
    const cupAssess = [];
    const cupTaxParent = [];
    const cupTaxLiveIn = [];
    const cupTaxFull = [];
    // Cupertino baseline 2026
    let mv=3100000, av=550537;
    for(let y=2026;y<=2050;y++){
      labels.push(String(y));
      cupValue.push(Math.round(mv));
      cupAssess.push(Math.round(av));
      cupTaxParent.push(Math.round(av*0.01335)); // historical effective ~1.335% as observed
      // For inherited scenarios from 2040 onward: show both
      // Pre-2040 live-in/full not applicable, just show parent
      // Post-2040 we compute alternative (handled in table, chart shows parent path)
      mv*=1.045;
      av*=1.02;
    }
    new Chart(elCupertino,{type:'line',data:{labels,datasets:[
      {label:'Market Value (4.5% CAGR)', data:cupValue, borderColor:'#0ea5a4', backgroundColor:'rgba(14,165,164,.08)', tension:.3, fill:true},
      {label:'Assessed Value (Parent Prop13 2%)', data:cupAssess, borderColor:'#0b1e3a', borderDash:[6,4], tension:.3},
      {label:'Property Tax if Parent Retains (~1.34%)', data:cupTaxParent, borderColor:'#b45309', tension:.3, yAxisID:'y1'}
    ]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(2)+'M'}},y1:{position:'right', grid:{display:false}, ticks:{callback:v=>'$'+(v/1000).toFixed(0)+'k'}}} }});
  }
  const elSF = document.getElementById('chart-sf');
  if(elSF && window.Chart){
    const labels=[]; const mvArr=[]; const avArr=[]; const taxArr=[];
    let mv=1800000, av=114248;
    for(let y=2026;y<=2050;y++){
      labels.push(String(y));
      mvArr.push(Math.round(mv));
      avArr.push(Math.round(av));
      taxArr.push(Math.round(av*0.02135)); // observed ~2.13% (flagged high - includes specials)
      mv*=1.038;
      av*=1.02;
    }
    new Chart(elSF,{type:'line',data:{labels,datasets:[
      {label:'Market Value (3.8% CAGR)', data:mvArr, borderColor:'#7c3aed', backgroundColor:'rgba(124,58,237,.08)', tension:.3, fill:true},
      {label:'Assessed Value (Prop13 2%)', data:avArr, borderColor:'#1f2937', borderDash:[6,4], tension:.3},
      {label:'Property Tax (observed ~2.14% – flagged)', data:taxArr, borderColor:'#dc2626', tension:.3, yAxisID:'y1'}
    ]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(2)+'M'}},y1:{position:'right', grid:{display:false}}} }});
  }
  const elDecision = document.getElementById('chart-decision');
  if(elDecision && window.Chart){
    // 20-year wealth comparison if sell now vs hold scenarios (simplified NPV)
    const labels=['Year 0 (2026)','5yr (2031)','10yr (2036)','15yr (2041)','20yr (2046)'];
    // Sell & invest in market at 7% after costs
    const sellInvest=[2914000,4080000,5720000,8020000,11230000];
    // Live in Cupertino (avoid rent, save, but pay taxes) – equity + avoided rent
    const liveIn=[3100000,4200000,5600000,7600000,10100000];
    // Rent out Cupertino at market
    const rentOut=[3100000,4300000,5800000,8000000,10800000];
    new Chart(elDecision,{type:'line',data:{labels,datasets:[
      {label:'Sell Now & Reinvest (7% net, after tax)', data:sellInvest, borderColor:'#0ea5a4', tension:.3, fill:true, backgroundColor:'rgba(14,165,164,.08)'},
      {label:'Live In (Prop19 partial) + SF rental retained', data:liveIn, borderColor:'#0b1e3a', tension:.3},
      {label:'Rent Cupertino (Full reassessment)', data:rentOut, borderColor:'#b45309', borderDash:[6,4], tension:.3}
    ]},options:{responsive:true,maintainAspectRatio:false,interaction:{mode:'index',intersect:false},scales:{y:{ticks:{callback:v=>'$'+(v/1e6).toFixed(1)+'M'}}}});
  }
});
