/* ===================== PropValuate AI — client logic ===================== */
let STATE = { predicted:null, contributions:null, forecast:null, rec:null, loc:null, form:null };

/* ---------- XGBoost tree evaluator ---------- */
function evalTree(node, feats){
  if(node.leaf !== undefined) return node.leaf;
  let v = feats[node.split];
  if(v === undefined || v === null || Number.isNaN(v)) v = -Infinity; // mimic missing-goes-default handling loosely
  const goYes = v < node.split_condition;
  const targetId = goYes ? node.yes : node.no;
  const child = node.children.find(c => c.nodeid === targetId);
  return evalTree(child, feats);
}
function predictRaw(feats){
  let sum = MODEL.base_score;
  for(const t of MODEL.trees) sum += evalTree(t, feats);
  return sum;
}

/* ---------- Build feature vector from form ---------- */
function buildFeatures(form){
  const sub = SUB_STATS[form.location][form.sublocality];
  return {
    area: form.area,
    bedrooms: form.bedrooms,
    bathrooms: form.bathrooms,
    stories: form.stories,
    parking: form.parking,
    property_age_years: form.age,
    mainroad_b: form.mainroad ? 1:0,
    guestroom_b: form.guestroom ? 1:0,
    basement_b: form.basement ? 1:0,
    hotwaterheating_b: form.hotwater ? 1:0,
    airconditioning_b: form.ac ? 1:0,
    prefarea_b: form.prefarea ? 1:0,
    location_c: META.loc_map[form.location],
    ptype_c: META.ptype_map[form.ptype],
    furnish_c: META.furnish_map[form.furnish],
    distance_to_school_km: sub.distance_to_school_km,
    distance_to_hospital_km: sub.distance_to_hospital_km,
    distance_to_supermarket_km: sub.distance_to_supermarket_km,
    distance_to_transit_km: sub.distance_to_transit_km,
    distance_to_park_km: sub.distance_to_park_km,
    location_convenience_score: sub.location_convenience_score,
    demand_index: sub.demand_index,
    local_market_index: sub.local_market_index,
  };
}

/* ---------- Approx SHAP-like contributions (marginal, baseline = dataset means) ---------- */
function computeContributions(feats){
  const baseline = {...META.feature_means};
  const basePred = predictRaw(baseline);
  const labels = {
    local_market_index:'Local market index', location_c:'Location', area:'Area (sq.ft)',
    demand_index:'Area demand index', airconditioning_b:'Air conditioning', bathrooms:'Bathrooms',
    furnish_c:'Furnishing', parking:'Parking', basement_b:'Basement', stories:'Stories',
    distance_to_hospital_km:'Distance to hospital', mainroad_b:'Main road access',
    property_age_years:'Property age', distance_to_school_km:'Distance to school',
    ptype_c:'Property type', prefarea_b:'Preferred area', distance_to_supermarket_km:'Distance to supermarket',
    guestroom_b:'Guest room', distance_to_transit_km:'Distance to transit', distance_to_park_km:'Distance to park',
    location_convenience_score:'Convenience score', hotwaterheating_b:'Hot water heating', bedrooms:'Bedrooms'
  };
  let contribs = [];
  for(const key of Object.keys(baseline)){
    const perturbed = {...baseline, [key]: feats[key]};
    const p = predictRaw(perturbed);
    contribs.push({key, label: labels[key]||key, value: p - basePred});
  }
  contribs.sort((a,b)=>Math.abs(b.value)-Math.abs(a.value));
  return {basePred, contribs: contribs.slice(0,8)};
}

/* ---------- Forecast ---------- */
function computeForecast(predicted, growthZone){
  const rate = META.growth_rates[growthZone] ?? 0.05;
  const years = [0,1,2,3,4,5];
  return years.map(y => ({year:y, value: predicted * Math.pow(1+rate, y)}));
}

/* ---------- "Typical property in this area" baseline, used as the comparable price ---------- */
function computeComparablePrediction(loc){
  const baseline = {...META.feature_means}; // dataset-average bedrooms/bathrooms/stories/parking/age/amenities/area
  baseline.location_c = META.loc_map[loc.location];
  baseline.distance_to_school_km = loc.distance_to_school_km;
  baseline.distance_to_hospital_km = loc.distance_to_hospital_km;
  baseline.distance_to_supermarket_km = loc.distance_to_supermarket_km;
  baseline.distance_to_transit_km = loc.distance_to_transit_km;
  baseline.distance_to_park_km = loc.distance_to_park_km;
  baseline.location_convenience_score = loc.location_convenience_score;
  baseline.demand_index = loc.demand_index;
  baseline.local_market_index = loc.local_market_index;
  return predictRaw(baseline);
}

/* ---------- Recommendation ---------- */
function computeRecommendation(predicted, loc, area){
  const comparable = computeComparablePrediction(loc);
  const diffPct = (predicted - comparable) / comparable;
  const rate = META.growth_rates[loc.growth_rate_zone] ?? 0.05;
  const highDemand = loc.demand_index >= 65;
  let verdict, reasons=[];
  if(diffPct <= -0.06 && (loc.growth_rate_zone !== 'Stable')){
    verdict='buy';
    reasons.push(`Priced ${Math.abs(diffPct*100).toFixed(1)}% below a typical property in ${loc.sublocality}, ${loc.location}.`);
    reasons.push(`${loc.growth_rate_zone} zone — projected ~${(rate*100).toFixed(0)}% annual appreciation.`);
  } else if(diffPct >= 0.10){
    verdict = highDemand ? 'wait' : 'avoid';
    reasons.push(`Priced ${(diffPct*100).toFixed(1)}% above a typical property in this area — limited room to negotiate.`);
    reasons.push(highDemand ? `Demand is still high (index ${loc.demand_index.toFixed(0)}/100), so it may settle with time.` : `Demand index is only ${loc.demand_index.toFixed(0)}/100 in this micro-market.`);
  } else {
    verdict='wait';
    reasons.push(`Priced close to a typical property here (${diffPct>=0?'+':''}${(diffPct*100).toFixed(1)}% vs. the area norm).`);
    reasons.push(`${loc.growth_rate_zone} zone with demand index ${loc.demand_index.toFixed(0)}/100 — no urgency either way.`);
  }
  reasons.push(`Location convenience score: ${loc.location_convenience_score.toFixed(0)}/100.`);
  if(loc.estimated) reasons.push(`Note: no sampled listings within a few km of ${loc.sublocality} — figures lean on nearby-area interpolation.`);
  const negotiation = verdict==='avoid' ? predicted*0.90 : (verdict==='wait' ? predicted*0.96 : predicted*0.985);
  return {verdict, reasons, negotiation, diffPct, comparable};
}

/* ---------- Formatting ---------- */
function fmtINR(n){
  n = Math.round(n);
  return '₹' + n.toLocaleString('en-IN');
}
function fmtINRShort(n){
  if(n>=10000000) return '₹'+(n/10000000).toFixed(2)+' Cr';
  if(n>=100000) return '₹'+(n/100000).toFixed(2)+' L';
  return fmtINR(n);
}

/* ---------- Render: waterfall ---------- */
function renderWaterfall(contribs){
  const maxAbs = Math.max(...contribs.map(c=>Math.abs(c.value)), 1);
  const el = document.getElementById('wf-rows');
  el.innerHTML = contribs.map(c=>{
    const pct = Math.min(100, Math.abs(c.value)/maxAbs*50);
    const cls = c.value>=0?'pos':'neg';
    const style = c.value>=0 ? `width:${pct}%;` : `width:${pct}%;`;
    return `<div class="wf-row">
      <div>${c.label}</div>
      <div class="wf-bar-track"><div class="wf-mid"></div><div class="wf-bar ${cls}" style="${style}"></div></div>
      <div class="wf-val" style="color:${c.value>=0?'var(--teal)':'var(--coral)'}">${c.value>=0?'+':''}${fmtINRShort(c.value)}</div>
    </div>`;
  }).join('');
}

/* ---------- Render: forecast chart (hand-drawn SVG) ---------- */
function renderForecastChart(forecast){
  const w=640,h=280,pad={l:70,r:20,t:20,b:36};
  const vals = forecast.map(f=>f.value);
  const min = Math.min(...vals)*0.98, max = Math.max(...vals)*1.02;
  const x = i => pad.l + (w-pad.l-pad.r) * (i/(forecast.length-1));
  const y = v => h-pad.b - (h-pad.t-pad.b) * ((v-min)/(max-min));
  let path = forecast.map((f,i)=> `${i===0?'M':'L'} ${x(i).toFixed(1)} ${y(f.value).toFixed(1)}`).join(' ');
  let area = path + ` L ${x(forecast.length-1).toFixed(1)} ${h-pad.b} L ${x(0).toFixed(1)} ${h-pad.b} Z`;
  let gridlines='', labels='';
  for(let i=0;i<=4;i++){
    const gy = pad.t + (h-pad.t-pad.b)*i/4;
    gridlines += `<line x1="${pad.l}" y1="${gy.toFixed(1)}" x2="${w-pad.r}" y2="${gy.toFixed(1)}" stroke="rgba(237,232,220,0.08)"/>`;
    const val = max - (max-min)*i/4;
    labels += `<text x="${pad.l-10}" y="${(gy+4).toFixed(1)}" text-anchor="end" font-size="10" fill="rgba(237,232,220,0.5)">${fmtINRShort(val)}</text>`;
  }
  let points = forecast.map((f,i)=>`<circle cx="${x(i).toFixed(1)}" cy="${y(f.value).toFixed(1)}" r="4" fill="#C79A3E"/>
    <text x="${x(i).toFixed(1)}" y="${h-14}" text-anchor="middle" font-size="11" fill="rgba(237,232,220,0.6)">${f.year===0?'Now':'Yr '+f.year}</text>`).join('');
  const svg = `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}">
    ${gridlines}${labels}
    <path d="${area}" fill="rgba(199,154,62,0.12)" stroke="none"/>
    <path d="${path}" fill="none" stroke="#C79A3E" stroke-width="2.5"/>
    ${points}
  </svg>`;
  document.getElementById('forecast-chart').innerHTML = svg;
}

/* ---------- Render: facilities ---------- */
function renderFacilities(loc){
  const items = [
    {icon:'🏫', name:loc.nearest_school, dist:loc.distance_to_school_km},
    {icon:'🏥', name:loc.nearest_hospital, dist:loc.distance_to_hospital_km},
    {icon:'🛒', name:loc.nearest_supermarket, dist:loc.distance_to_supermarket_km},
    {icon:'🚉', name:loc.nearest_transit_station, dist:loc.distance_to_transit_km},
    {icon:'🌳', name:loc.nearest_park, dist:loc.distance_to_park_km},
  ];
  document.getElementById('fac-grid').innerHTML = items.map(i=>`
    <div class="fac-card"><div class="icon">${i.icon}</div><div class="name">${i.name}</div><div class="dist">${i.dist.toFixed(2)} km away</div></div>
  `).join('');
  document.getElementById('conv-score-val').textContent = loc.location_convenience_score.toFixed(0)+'/100';
  document.getElementById('conv-fill').style.width = loc.location_convenience_score+'%';
  const noteEl = document.getElementById('fac-area-note');
  if(noteEl){
    noteEl.textContent = loc.estimated
      ? `Showing citywide averages for ${loc.location} — not enough sampled listings in ${loc.sublocality} yet.`
      : `Based on ${loc.sample_size} sampled propert${loc.sample_size===1?'y':'ies'} near ${loc.sublocality}, ${loc.location}.`;
  }
}

/* ---------- Render: recommendation ---------- */
function renderRecommendation(rec, predicted){
  const badge = document.getElementById('rec-badge');
  badge.className = 'rec-badge ' + rec.verdict;
  badge.textContent = rec.verdict==='buy'?'BUY':rec.verdict==='wait'?'WAIT':'AVOID';
  document.getElementById('rec-reasons').innerHTML = rec.reasons.map(r=>`<li>${r}</li>`).join('');
  document.getElementById('rec-neg').innerHTML = `Suggested opening offer: <b>${fmtINRShort(rec.negotiation)}</b> &nbsp;·&nbsp; Typical property price in this area: ${fmtINRShort(rec.comparable)}`;
}

/* ---------- Map ---------- */
let mapInstance=null;
function renderMap(highlightCity, highlightSub){
  if(mapInstance){ mapInstance.remove(); }
  mapInstance = L.map('map', {zoomControl:true, attributionControl:false}).setView([21.5,79],4.6);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',{maxZoom:13}).addTo(mapInstance);
  HEATMAP.forEach(p=>{
    const color = p.demand_index>=70?'#3E9C82':p.demand_index>=45?'#C79A3E':'#D2624B';
    L.circleMarker([p.latitude,p.longitude],{
      radius: 4 + (p.demand_index/100)*6,
      color, fillColor: color, fillOpacity:0.55, weight:1
    }).bindPopup(`<b>${p.sublocality||''}, ${p.location}</b><br>₹${Math.round(p.price_per_sqft).toLocaleString('en-IN')}/sqft<br>Demand: ${p.demand_index.toFixed(0)}/100`).addTo(mapInstance);
  });
  if(highlightCity && highlightSub){
    const sub = SUB_STATS[highlightCity] && SUB_STATS[highlightCity][highlightSub];
    if(sub){
      mapInstance.setView([sub.latitude, sub.longitude], 12);
      L.marker([sub.latitude, sub.longitude]).addTo(mapInstance)
        .bindPopup(`<b>${highlightSub}, ${highlightCity}</b> — your search`).openPopup();
    }
  }
}

/* ---------- Chatbot (rule-based) ---------- */
function chatRespond(msg){
  const m = msg.toLowerCase();
  if(!STATE.predicted) return "Run a valuation first (fill the form above and hit 'Estimate value') and I'll be able to answer questions about your specific property.";
  const P = STATE.predicted, loc = STATE.loc, rec = STATE.rec, fc = STATE.forecast;
  if(/price|value|worth|cost/.test(m)) return `The estimated market value is ${fmtINRShort(P)} (${fmtINR(P)}), based on comparable sales in ${loc.sublocality}, ${loc.location}.`;
  if(/forecast|future|5 year|next year|appreciat/.test(m)) return `In ${loc.growth_rate_zone.toLowerCase()} conditions, the model projects ${fmtINRShort(fc[5].value)} in 5 years — about ${(((fc[5].value/P)-1)*100).toFixed(0)}% total growth.`;
  if(/buy|wait|avoid|recommend|should i/.test(m)) return `My read: ${rec.verdict.toUpperCase()}. ${rec.reasons[0]}`;
  if(/negotiat|offer|discount/.test(m)) return `A reasonable opening offer would be around ${fmtINRShort(rec.negotiation)}, versus a typical property price of ${fmtINRShort(rec.comparable)} in this area.`;
  if(/school|hospital|park|transit|metro|market|facilit|nearby/.test(m)) return `Nearest school: ${loc.nearest_school} (${loc.distance_to_school_km.toFixed(1)}km). Nearest hospital: ${loc.nearest_hospital} (${loc.distance_to_hospital_km.toFixed(1)}km). Convenience score: ${loc.location_convenience_score.toFixed(0)}/100.`;
  if(/demand/.test(m)) return `${loc.sublocality}, ${loc.location} has a demand index of ${loc.demand_index.toFixed(0)}/100, in a ${loc.growth_rate_zone.toLowerCase()} zone.`;
  if(/why|explain|factor|shap/.test(m)) return `The biggest drivers for this estimate were ${STATE.contributions.contribs.slice(0,3).map(c=>c.label.toLowerCase()).join(', ')}. See the "Why this price" panel for the full breakdown.`;
  return `I can help with the price, 5-year forecast, buy/wait/avoid recommendation, negotiation range, or nearby facilities for ${loc.sublocality}, ${loc.location} — what would you like to know?`;
}
function addMsg(text, who){
  const body = document.getElementById('chat-body');
  const div = document.createElement('div');
  div.className = 'msg '+who;
  div.textContent = text;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

/* ---------- PDF report ---------- */
function generatePDF(){
  if(!STATE.predicted){ alert('Run a valuation first.'); return; }
  const {jsPDF} = window.jspdf;
  const doc = new jsPDF();
  const loc = STATE.loc, f = STATE.form, rec = STATE.rec, fc = STATE.forecast;
  let y = 20;
  doc.setFont('times','bold'); doc.setFontSize(20);
  doc.text('PropValuate AI — Valuation Report', 105, y, {align:'center'}); y+=8;
  doc.setFontSize(10); doc.setFont('helvetica','normal'); doc.setTextColor(120);
  doc.text('Generated ' + new Date().toLocaleDateString('en-IN'), 105, y, {align:'center'}); y+=14;
  doc.setDrawColor(200); doc.line(15,y,195,y); y+=10;

  doc.setTextColor(20); doc.setFont('helvetica','bold'); doc.setFontSize(13); doc.text('Property Details', 15, y); y+=8;
  doc.setFont('helvetica','normal'); doc.setFontSize(11);
  const details = [
    ['Sub-locality', f.sublocality], ['Location', f.location], ['Property type', f.ptype], ['Area', f.area+' sq.ft'],
    ['Bedrooms', f.bedrooms], ['Bathrooms', f.bathrooms], ['Stories', f.stories],
    ['Age', f.age+' years'], ['Furnishing', f.furnish],
  ];
  details.forEach(([k,v])=>{ doc.text(`${k}:`, 15, y); doc.text(`${v}`, 70, y); y+=7; });
  y+=4; doc.setDrawColor(220); doc.line(15,y,195,y); y+=10;

  doc.setFont('helvetica','bold'); doc.setFontSize(13); doc.text('Predicted Market Value', 15, y); y+=9;
  doc.setFont('times','bold'); doc.setFontSize(18); doc.setTextColor(150,110,30);
  doc.text(fmtINR(STATE.predicted), 15, y); y+=10;
  doc.setTextColor(20); doc.setFont('helvetica','normal'); doc.setFontSize(10.5);
  doc.text(`Model R-squared: ${(META.r2*100).toFixed(1)}%  |  Mean abs. error: ${fmtINRShort(META.mae)}`, 15, y); y+=10;

  doc.setFont('helvetica','bold'); doc.setFontSize(12); doc.text('Top Value Drivers (SHAP)', 15, y); y+=8;
  doc.setFont('helvetica','normal'); doc.setFontSize(10.5);
  STATE.contributions.contribs.slice(0,6).forEach(c=>{
    doc.text(`${c.label}: ${c.value>=0?'+':''}${fmtINRShort(c.value)}`, 15, y); y+=6.5;
  });
  y+=4; doc.setDrawColor(220); doc.line(15,y,195,y); y+=10;

  doc.setFont('helvetica','bold'); doc.setFontSize(12); doc.text('5-Year Forecast', 15, y); y+=8;
  doc.setFont('helvetica','normal'); doc.setFontSize(10.5);
  fc.forEach(pt=>{ doc.text(`${pt.year===0?'Today':'Year '+pt.year}: ${fmtINRShort(pt.value)}`, 15, y); y+=6.5; });
  y+=4;
  if(y>250){doc.addPage(); y=20;}
  doc.setDrawColor(220); doc.line(15,y,195,y); y+=10;

  doc.setFont('helvetica','bold'); doc.setFontSize(12); doc.text('Market & Facilities Summary', 15, y); y+=8;
  doc.setFont('helvetica','normal'); doc.setFontSize(10.5);
  [`Demand index: ${loc.demand_index.toFixed(0)}/100 (${loc.growth_rate_zone})`,
   `Location convenience score: ${loc.location_convenience_score.toFixed(0)}/100`,
   `Nearest school: ${loc.nearest_school} (${loc.distance_to_school_km.toFixed(1)} km)`,
   `Nearest hospital: ${loc.nearest_hospital} (${loc.distance_to_hospital_km.toFixed(1)} km)`,
   `Nearest transit: ${loc.nearest_transit_station} (${loc.distance_to_transit_km.toFixed(1)} km)`,
  ].forEach(t=>{ doc.text(t,15,y); y+=6.5; });
  y+=4; doc.setDrawColor(220); doc.line(15,y,195,y); y+=10;

  doc.setFont('helvetica','bold'); doc.setFontSize(12); doc.text('Buying & Negotiation Recommendation', 15, y); y+=8;
  doc.setFont('helvetica','bold'); doc.setFontSize(13);
  const vColor = rec.verdict==='buy'?[62,156,130]:rec.verdict==='avoid'?[210,98,75]:[199,154,62];
  doc.setTextColor(vColor[0], vColor[1], vColor[2]);
  doc.text(rec.verdict.toUpperCase(), 15, y); y+=8;
  doc.setTextColor(20); doc.setFont('helvetica','normal'); doc.setFontSize(10.5);
  rec.reasons.forEach(r=>{ doc.text('- '+r, 15, y); y+=6.5; });
  doc.text(`Suggested negotiation price: ${fmtINRShort(rec.negotiation)}`, 15, y); y+=8;

  doc.setFontSize(9); doc.setTextColor(140);
  doc.text('AI Assistant Summary: ' + chatRespond('why'), 15, y, {maxWidth:180}); 

  doc.save(`PropValuate_Report_${f.sublocality}_${f.location}.pdf`);
}

/* ---------- Main run ---------- */
function runValuation(e){
  e.preventDefault();
  const form = {
    location: document.getElementById('f-location').value,
    sublocality: document.getElementById('f-sublocality').value,
    ptype: document.getElementById('f-ptype').value,
    furnish: document.getElementById('f-furnish').value,
    area: parseFloat(document.getElementById('f-area').value),
    bedrooms: parseInt(document.getElementById('f-bedrooms').value),
    bathrooms: parseInt(document.getElementById('f-bathrooms').value),
    stories: parseInt(document.getElementById('f-stories').value),
    parking: parseInt(document.getElementById('f-parking').value),
    age: parseFloat(document.getElementById('f-age').value),
    mainroad: document.getElementById('f-mainroad').checked,
    guestroom: document.getElementById('f-guestroom').checked,
    basement: document.getElementById('f-basement').checked,
    hotwater: document.getElementById('f-hotwater').checked,
    ac: document.getElementById('f-ac').checked,
    prefarea: document.getElementById('f-prefarea').checked,
  };
  const loc = SUB_STATS[form.location][form.sublocality];
  const feats = buildFeatures(form);
  const predicted = predictRaw(feats);
  const contributions = computeContributions(feats);
  const forecast = computeForecast(predicted, loc.growth_rate_zone);
  const rec = computeRecommendation(predicted, loc, form.area);

  STATE = {predicted, contributions, forecast, rec, loc, form};

  document.getElementById('seal-amt').textContent = fmtINRShort(predicted);
  document.getElementById('seal-range').textContent = `${fmtINRShort(predicted*0.93)} – ${fmtINRShort(predicted*1.07)}`;
  document.getElementById('seal-loc').textContent = `${form.sublocality.toUpperCase()}, ${form.location.toUpperCase()} · ${new Date().getFullYear()}`;

  renderWaterfall(contributions.contribs);
  renderForecastChart(forecast);
  document.getElementById('info-rate').textContent = ((META.growth_rates[loc.growth_rate_zone]||0.05)*100).toFixed(0)+'% / yr';
  document.getElementById('info-zone').textContent = loc.growth_rate_zone;
  document.getElementById('info-demand').textContent = loc.demand_index.toFixed(0)+'/100';
  document.getElementById('info-5yr').textContent = fmtINRShort(forecast[5].value);

  renderFacilities(loc);
  renderRecommendation(rec, predicted);
  renderMap(form.location, form.sublocality);

  document.querySelectorAll('.result-wrap').forEach(el=>el.classList.add('show'));
  document.getElementById('valuate-results').scrollIntoView({behavior:'smooth', block:'start'});
}

/* ---------- Dependent dropdown: city -> sub-district ---------- */
function populateSublocalities(city){
  const sel = document.getElementById('f-sublocality');
  sel.innerHTML = '';
  const areas = Object.keys(SUB_STATS[city] || {});
  areas.forEach(a => sel.innerHTML += `<option value="${a}">${a}</option>`);
}

/* ---------- Dependent dropdown: city -> property types actually seen in that city ---------- */
function populatePtypes(city){
  const sel = document.getElementById('f-ptype');
  sel.innerHTML = '';
  const valid = META.city_ptypes[city] || META.ptypes;
  valid.forEach(p => sel.innerHTML += `<option value="${p}">${p}</option>`);
}

/* ---------- Init ---------- */
document.addEventListener('DOMContentLoaded', ()=>{
  const locSel = document.getElementById('f-location');
  META.locations.forEach(l=> locSel.innerHTML += `<option value="${l}">${l}</option>`);
  locSel.value = META.locations[0];
  populateSublocalities(META.locations[0]);
  populatePtypes(META.locations[0]);
  locSel.addEventListener('change', ()=>{
    populateSublocalities(locSel.value);
    populatePtypes(locSel.value);
  });

  const furnishSel = document.getElementById('f-furnish');
  META.furnish.forEach(f=> furnishSel.innerHTML += `<option value="${f}">${f}</option>`);

  document.getElementById('valuation-form').addEventListener('submit', runValuation);
  document.getElementById('pdf-btn').addEventListener('click', generatePDF);

  renderMap(null, null);

  // ticker stats
  const avgPsf = Math.round(HEATMAP.reduce((a,p)=>a+p.price_per_sqft,0)/HEATMAP.length);
  const avgDemand = Math.round(HEATMAP.reduce((a,p)=>a+p.demand_index,0)/HEATMAP.length);
  document.getElementById('t-cities').textContent = META.locations.length;
  document.getElementById('t-psf').textContent = '₹'+avgPsf.toLocaleString('en-IN');
  document.getElementById('t-r2').textContent = (META.r2*100).toFixed(1)+'%';
  document.getElementById('t-demand').textContent = avgDemand+'/100';

  // chat
  const fab = document.getElementById('chat-fab');
  const panel = document.getElementById('chat-panel');
  fab.addEventListener('click', ()=> panel.classList.toggle('open'));
  document.getElementById('chat-close').addEventListener('click', ()=> panel.classList.remove('open'));
  const input = document.getElementById('chat-input');
  function send(){
    const val = input.value.trim();
    if(!val) return;
    addMsg(val,'user'); input.value='';
    setTimeout(()=> addMsg(chatRespond(val),'bot'), 350);
  }
  document.getElementById('chat-send').addEventListener('click', send);
  input.addEventListener('keydown', e=>{ if(e.key==='Enter') send(); });
  document.querySelectorAll('.chip').forEach(c=> c.addEventListener('click', ()=>{ input.value=c.textContent; send(); }));
});
