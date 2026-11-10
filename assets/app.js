// Vanilla charts + table rendering (no external deps).
function money(n){return "$"+Math.round(n).toLocaleString("en-US");}
function lineChart(id, series, yLabel){
  const c=document.getElementById(id); if(!c) return;
  const dpr=window.devicePixelRatio||1, W=c.clientWidth, H=c.clientHeight;
  c.width=W*dpr; c.height=H*dpr;
  const x=c.getContext("2d"); x.scale(dpr,dpr);
  const pad={l:64,r:12,t:12,b:28};
  const all=series.flatMap(s=>s.data.map(p=>p[1]));
  const ymin=Math.min(...all), ymax=Math.max(...all), span=(ymax-ymin)||1;
  const X=i=>pad.l+(W-pad.l-pad.r)*(i/(series[0].data.length-1));
  const Y=v=>pad.t+(H-pad.t-pad.b)*(1-(v-ymin)/span);
  x.strokeStyle="#e2e6ee"; x.fillStyle="#5b6577"; x.font="11px sans-serif";
  for(let g=0;g<=4;g++){const v=ymin+span*g/4, y=Y(v);
    x.beginPath();x.moveTo(pad.l,y);x.lineTo(W-pad.r,y);x.stroke();
    x.fillText("$"+Math.round(v/1000)+"k",6,y+4);}
  series.forEach(s=>{x.strokeStyle=s.color;x.lineWidth=2;x.beginPath();
    s.data.forEach((p,i)=>{const px=X(i),py=Y(p[1]); i?x.lineTo(px,py):x.moveTo(px,py);});x.stroke();});
  x.fillStyle="#5b6577";
  const years=series[0].data.map(p=>p[0]);
  [0,Math.floor(years.length/2),years.length-1].forEach(i=>x.fillText(years[i],X(i)-10,H-8));
  // legend
  let lx=pad.l+8; x.font="12px sans-serif";
  series.forEach(s=>{x.fillStyle=s.color;x.fillRect(lx,pad.t+2,14,4);x.fillStyle="#1a2233";
    x.fillText(s.label,lx+18,pad.t+8); lx+=18+x.measureText(s.label).width+22;});
}
function renderTable(id, rows, cols){
  const t=document.getElementById(id); if(!t) return;
  t.innerHTML="<thead><tr>"+cols.map(c=>"<th>"+c.label+"</th>").join("")+"</tr></thead><tbody>"+
    rows.map(r=>"<tr>"+cols.map(c=>"<td>"+(c.fmt?c.fmt(r[c.k]):r[c.k])+"</td>").join("")+"</tr>").join("")+"</tbody>";
}
document.addEventListener("DOMContentLoaded",()=>{
  if(window.CUP){
    lineChart("ch-cup-value",[{label:"Market value",color:"#0f6cbd",data:CUP.map(r=>[r.year,r.value])},
      {label:"Assessed (Prop 13)",color:"#0a7a42",data:CUP.map(r=>[r.year,r.assessed])}]);
    lineChart("ch-sf-value",[{label:"Market value",color:"#7c3aed",data:SF.map(r=>[r.year,r.value])},
      {label:"Assessed (Prop 13)",color:"#0a7a42",data:SF.map(r=>[r.year,r.assessed])}]);
    lineChart("ch-cup-cost",[{label:"Property tax",color:"#b91c1c",data:CUP.map(r=>[r.year,r.tax])},
      {label:"Insurance",color:"#b45309",data:CUP.map(r=>[r.year,r.insurance])},
      {label:"Maintenance",color:"#0f6cbd",data:CUP.map(r=>[r.year,r.maintenance])}]);
    lineChart("ch-sf-net",[{label:"Rent",color:"#0a7a42",data:SF.map(r=>[r.year,r.rent])},
      {label:"Total costs",color:"#b91c1c",data:SF.map(r=>[r.year,r.total_cost])}]);
    renderTable("tb-cup",CUP,[{k:"year",label:"Year"},{k:"value",label:"Market value",fmt:money},
      {k:"assessed",label:"Assessed",fmt:money},{k:"tax",label:"Tax",fmt:money},
      {k:"water",label:"Water",fmt:money},{k:"electric",label:"Electric",fmt:money},
      {k:"insurance",label:"Insurance",fmt:money},{k:"maintenance",label:"Maint.",fmt:money},
      {k:"total_cost",label:"Total cost",fmt:money}]);
    renderTable("tb-sf",SF,[{k:"year",label:"Year"},{k:"value",label:"Market value",fmt:money},
      {k:"assessed",label:"Assessed",fmt:money},{k:"tax",label:"Tax",fmt:money},
      {k:"water",label:"Water+sewer",fmt:money},{k:"electric",label:"Electric",fmt:money},
      {k:"insurance",label:"Insurance",fmt:money},{k:"maintenance",label:"Maint.",fmt:money},
      {k:"rent",label:"Rent",fmt:money},{k:"total_cost",label:"Total cost",fmt:money}]);
    renderTable("tb-scen",SCEN,[{k:"year",label:"Inherit year"},{k:"market",label:"Cupertino market",fmt:money},
      {k:"live_tax",label:"Tax if live-in (Prop 19)",fmt:money},{k:"full_tax",label:"Tax if rented (full reassess.)",fmt:money},
      {k:"rent_scenario_net",label:"Rent scenario net/yr",fmt:money},
      {k:"sell_net",label:"Sell net proceeds",fmt:money},
      {k:"invest_10yr",label:"Invested 10 yrs @7%",fmt:money},{k:"keep_home_10yr",label:"Kept home 10 yrs @3%",fmt:money}]);
  }
});
