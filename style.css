/* ===================== PropValuate AI — client logic (talks to Python/FastAPI backend) ===================== */
let STATE = { predicted: null, contributions: null, forecast: null, rec: null, loc: null, form: null };
let META = null;       // /api/meta response
let HEATMAP = null;    // /api/heatmap response
let mapInstance = null;

/* ---------- Formatting ---------- */
function fmtINR(n) {
  n = Math.round(n);
  return '₹' + n.toLocaleString('en-IN');
}
function fmtINRShort(n) {
  if (n >= 10000000) return '₹' + (n / 10000000).toFixed(2) + ' Cr';
  if (n >= 100000) return '₹' + (n / 100000).toFixed(2) + ' L';
  return fmtINR(n);
}

/* ---------- Render: waterfall ---------- */
function renderWaterfall(contribs) {
  const maxAbs = Math.max(...contribs.map(c => Math.abs(c.value)), 1);
  const el = document.getElementById('wf-rows');
  el.innerHTML = contribs.map(c => {
    const pct = Math.min(100, Math.abs(c.value) / maxAbs * 50);
    const cls = c.value >= 0 ? 'pos' : 'neg';
    return `<div class="wf-row">
      <div>${c.label}</div>
      <div class="wf-bar-track"><div class="wf-mid"></div><div class="wf-bar ${cls}" style="width:${pct}%;"></div></div>
      <div class="wf-val" style="color:${c.value >= 0 ? 'var(--teal)' : 'var(--coral)'}">${c.value >= 0 ? '+' : ''}${fmtINRShort(c.value)}</div>
    </div>`;
  }).join('');
}

/* ---------- Render: forecast chart (hand-drawn SVG) ---------- */
function renderForecastChart(forecast) {
  const w = 640, h = 280, pad = { l: 70, r: 20, t: 20, b: 36 };
  const vals = forecast.map(f => f.value);
  const min = Math.min(...vals) * 0.98, max = Math.max(...vals) * 1.02;
  const x = i => pad.l + (w - pad.l - pad.r) * (i / (forecast.length - 1));
  const y = v => h - pad.b - (h - pad.t - pad.b) * ((v - min) / (max - min));
  let path = forecast.map((f, i) => `${i === 0 ? 'M' : 'L'} ${x(i).toFixed(1)} ${y(f.value).toFixed(1)}`).join(' ');
  let area = path + ` L ${x(forecast.length - 1).toFixed(1)} ${h - pad.b} L ${x(0).toFixed(1)} ${h - pad.b} Z`;
  let gridlines = '', labels = '';
  for (let i = 0; i <= 4; i++) {
    const gy = pad.t + (h - pad.t - pad.b) * i / 4;
    gridlines += `<line x1="${pad.l}" y1="${gy.toFixed(1)}" x2="${w - pad.r}" y2="${gy.toFixed(1)}" stroke="rgba(237,232,220,0.08)"/>`;
    const val = max - (max - min) * i / 4;
    labels += `<text x="${pad.l - 10}" y="${(gy + 4).toFixed(1)}" text-anchor="end" font-size="10" fill="rgba(237,232,220,0.5)">${fmtINRShort(val)}</text>`;
  }
  let points = forecast.map((f, i) => `<circle cx="${x(i).toFixed(1)}" cy="${y(f.value).toFixed(1)}" r="4" fill="#C79A3E"/>
    <text x="${x(i).toFixed(1)}" y="${h - 14}" text-anchor="middle" font-size="11" fill="rgba(237,232,220,0.6)">${f.year === 0 ? 'Now' : 'Yr ' + f.year}</text>`).join('');
  const svg = `<svg viewBox="0 0 ${w} ${h}" width="100%" height="${h}">
    ${gridlines}${labels}
    <path d="${area}" fill="rgba(199,154,62,0.12)" stroke="none"/>
    <path d="${path}" fill="none" stroke="#C79A3E" stroke-width="2.5"/>
    ${points}
  </svg>`;
  document.getElementById('forecast-chart').innerHTML = svg;
}

/* ---------- Render: facilities ---------- */
function renderFacilities(loc) {
  const items = [
    { icon: '🏫', name: loc.nearest_school, dist: loc.distance_to_school_km },
    { icon: '🏥', name: loc.nearest_hospital, dist: loc.distance_to_hospital_km },
    { icon: '🛒', name: loc.nearest_supermarket, dist: loc.distance_to_supermarket_km },
    { icon: '🚉', name: loc.nearest_transit_station, dist: loc.distance_to_transit_km },
    { icon: '🌳', name: loc.nearest_park, dist: loc.distance_to_park_km },
  ];
  document.getElementById('fac-grid').innerHTML = items.map(i => `
    <div class="fac-card"><div class="icon">${i.icon}</div><div class="name">${i.name}</div><div class="dist">${i.dist.toFixed(2)} km away</div></div>
  `).join('');
  document.getElementById('conv-score-val').textContent = loc.location_convenience_score.toFixed(0) + '/100';
  document.getElementById('conv-fill').style.width = loc.location_convenience_score + '%';
  const noteEl = document.getElementById('fac-area-note');
  if (noteEl) {
    noteEl.textContent = loc.estimated
      ? `Estimated figures for ${loc.sublocality}, ${loc.location} — no verified listings sampled in this area yet, so these numbers are modeled rather than measured.`
      : `Based on ${loc.sample_size} sampled propert${loc.sample_size === 1 ? 'y' : 'ies'} near ${loc.sublocality}, ${loc.location}.`;
  }
}

/* ---------- Render: recommendation ---------- */
function renderRecommendation(rec, predicted) {
  const badge = document.getElementById('rec-badge');
  badge.className = 'rec-badge ' + rec.verdict;
  badge.textContent = rec.verdict === 'buy' ? 'BUY' : rec.verdict === 'wait' ? 'WAIT' : 'AVOID';
  document.getElementById('rec-reasons').innerHTML = rec.reasons.map(r => `<li>${r}</li>`).join('');
  document.getElementById('rec-neg').innerHTML = `Suggested opening offer: <b>${fmtINRShort(rec.negotiation)}</b> &nbsp;·&nbsp; Typical property price in this area: ${fmtINRShort(rec.comparable)}`;
}

/* ---------- Map ---------- */
function renderMap(highlightCity, highlightSub) {
  if (mapInstance) { mapInstance.remove(); }
  mapInstance = L.map('map', { zoomControl: true, attributionControl: false }).setView([21.5, 79], 4.6);
  L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', { maxZoom: 13 }).addTo(mapInstance);
  HEATMAP.forEach(p => {
    const color = p.demand_index >= 70 ? '#3E9C82' : p.demand_index >= 45 ? '#C79A3E' : '#D2624B';
    L.circleMarker([p.latitude, p.longitude], {
      radius: 4 + (p.demand_index / 100) * 6,
      color, fillColor: color, fillOpacity: 0.55, weight: 1
    }).bindPopup(`<b>${p.sublocality || ''}, ${p.location}</b><br>₹${Math.round(p.price_per_sqft).toLocaleString('en-IN')}/sqft<br>Demand: ${p.demand_index.toFixed(0)}/100`).addTo(mapInstance);
  });
  if (highlightCity && highlightSub) {
    const sub = META.sub_stats[highlightCity] && META.sub_stats[highlightCity][highlightSub];
    if (sub) {
      mapInstance.setView([sub.latitude, sub.longitude], 12);
      L.marker([sub.latitude, sub.longitude]).addTo(mapInstance)
        .bindPopup(`<b>${highlightSub}, ${highlightCity}</b> — your search`).openPopup();
    }
  }
}

/* ---------- Chat (server-side now) ---------- */
async function chatRespond(msg) {
  if (!STATE.predicted) {
    return "Run a valuation first (fill the form above and hit 'Estimate value') and I'll be able to answer questions about your specific property.";
  }
  const res = await fetch('/api/chat', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ message: msg, valuation: STATE.raw }),
  });
  const data = await res.json();
  return data.reply;
}
function addMsg(text, who) {
  const body = document.getElementById('chat-body');
  const div = document.createElement('div');
  div.className = 'msg ' + who;
  div.textContent = text;
  body.appendChild(div);
  body.scrollTop = body.scrollHeight;
}

/* ---------- PDF report (now generated server-side — no browser library needed) ---------- */
async function generatePDF() {
  if (!STATE.form) { alert('Run a valuation first.'); return; }
  const btn = document.getElementById('pdf-btn');
  const originalText = btn.textContent;
  btn.textContent = 'Generating…';
  btn.disabled = true;
  try {
    const res = await fetch('/api/pdf-report', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(STATE.form),
    });
    if (!res.ok) throw new Error('PDF generation failed: ' + res.status);
    const blob = await res.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `PropValuate_Report_${STATE.form.sublocality}_${STATE.form.location}.pdf`;
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);
  } catch (err) {
    alert('Could not generate the PDF report. Please try again.');
    console.error(err);
  } finally {
    btn.textContent = originalText;
    btn.disabled = false;
  }
}

/* ---------- Main run: calls /api/valuate ---------- */
async function runValuation(e) {
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

  const submitBtn = e.target.querySelector('button[type="submit"]');
  const originalText = submitBtn.textContent;
  submitBtn.textContent = 'Estimating…';
  submitBtn.disabled = true;

  let data;
  try {
    const res = await fetch('/api/valuate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(form),
    });
    if (!res.ok) throw new Error('Valuation failed: ' + res.status);
    data = await res.json();
  } catch (err) {
    alert('Could not run the valuation. Please try again.');
    console.error(err);
    submitBtn.textContent = originalText;
    submitBtn.disabled = false;
    return;
  }
  submitBtn.textContent = originalText;
  submitBtn.disabled = false;

  const { predicted, contributions, forecast, recommendation, location } = data;
  STATE = { predicted, contributions: contributions, forecast, rec: recommendation, loc: location, form, raw: data };

  document.getElementById('seal-amt').textContent = fmtINRShort(predicted);
  document.getElementById('seal-range').textContent = `${fmtINRShort(predicted * 0.93)} – ${fmtINRShort(predicted * 1.07)}`;
  document.getElementById('seal-loc').textContent = `${form.sublocality.toUpperCase()}, ${form.location.toUpperCase()} · ${new Date().getFullYear()}`;

  renderWaterfall(contributions);
  renderForecastChart(forecast);
  document.getElementById('info-rate').textContent = ((META.growth_rates?.[location.growth_rate_zone]) ?? 0.05) * 100 + '% / yr';
  document.getElementById('info-zone').textContent = location.growth_rate_zone;
  document.getElementById('info-demand').textContent = location.demand_index.toFixed(0) + '/100';
  document.getElementById('info-5yr').textContent = fmtINRShort(forecast[5].value);

  renderFacilities(location);
  renderRecommendation(recommendation, predicted);
  renderMap(form.location, form.sublocality);

  document.querySelectorAll('.result-wrap').forEach(el => el.classList.add('show'));
  document.getElementById('valuate-results').scrollIntoView({ behavior: 'smooth', block: 'start' });
}

/* ---------- Dependent dropdown: city -> sub-district ---------- */
function populateSublocalities(city) {
  const sel = document.getElementById('f-sublocality');
  sel.innerHTML = '';
  const areas = Object.keys(META.sub_stats[city] || {});
  areas.forEach(a => sel.innerHTML += `<option value="${a}">${a}</option>`);
}

/* ---------- Dependent dropdown: city -> property types actually seen in that city ---------- */
function populatePtypes(city) {
  const sel = document.getElementById('f-ptype');
  sel.innerHTML = '';
  const valid = META.city_ptypes[city] || [];
  valid.forEach(p => sel.innerHTML += `<option value="${p}">${p}</option>`);
}

/* ---------- Init ---------- */
function showInitError(msg) {
  console.error('PropValuate init error:', msg);
  const form = document.getElementById('valuation-form');
  if (!form) return;
  let banner = document.getElementById('init-error-banner');
  if (!banner) {
    banner = document.createElement('div');
    banner.id = 'init-error-banner';
    banner.style.cssText = 'background:#4a1414;border:1px solid #ff6f61;color:#ffd7d0;padding:14px 18px;border-radius:8px;margin-bottom:20px;font-size:13.5px;';
    form.parentNode.insertBefore(banner, form);
  }
  banner.textContent = 'Could not load property data from the server: ' + msg + ' — check that uvicorn is running without errors, then refresh this page (Ctrl/Cmd+Shift+R for a hard refresh).';
}

document.addEventListener('DOMContentLoaded', async () => {
  // Fetch metadata + heatmap from the Python backend
  let metaRes, heatmapRes;
  try {
    [metaRes, heatmapRes] = await Promise.all([fetch('/api/meta'), fetch('/api/heatmap')]);
  } catch (err) {
    showInitError('network request failed (' + err.message + '). Is the server running at this address?');
    return;
  }
  if (!metaRes.ok) {
    showInitError('/api/meta returned HTTP ' + metaRes.status);
    return;
  }
  if (!heatmapRes.ok) {
    showInitError('/api/heatmap returned HTTP ' + heatmapRes.status);
    return;
  }
  try {
    META = await metaRes.json();
    HEATMAP = await heatmapRes.json();
  } catch (err) {
    showInitError('server response was not valid JSON (' + err.message + ')');
    return;
  }
  if (!META || !Array.isArray(META.locations) || META.locations.length === 0) {
    showInitError('server returned no locations — the data files may be missing on the server.');
    return;
  }

  document.getElementById('model-r2-inline').textContent = (META.r2 * 100).toFixed(1) + '%';
  document.getElementById('model-mae-inline').textContent = '₹' + Math.round(META.mae).toLocaleString('en-IN');

  const locSel = document.getElementById('f-location');
  const tierLabels = { 1: 'Tier 1 Cities', 2: 'Tier 2 Cities', 3: 'Tier 3 Cities' };
  const byTier = { 1: [], 2: [], 3: [] };
  META.locations.forEach(l => {
    const tier = (META.city_tier && META.city_tier[l]) || 1;
    byTier[tier].push(l);
  });
  [1, 2, 3].forEach(tier => {
    if (!byTier[tier].length) return;
    const group = document.createElement('optgroup');
    group.label = tierLabels[tier];
    byTier[tier].forEach(l => {
      const opt = document.createElement('option');
      opt.value = l; opt.textContent = l;
      group.appendChild(opt);
    });
    locSel.appendChild(group);
  });
  locSel.value = META.locations[0];
  populateSublocalities(META.locations[0]);
  populatePtypes(META.locations[0]);
  locSel.addEventListener('change', () => {
    populateSublocalities(locSel.value);
    populatePtypes(locSel.value);
  });

  const furnishSel = document.getElementById('f-furnish');
  META.furnish.forEach(f => furnishSel.innerHTML += `<option value="${f}">${f}</option>`);

  document.getElementById('valuation-form').addEventListener('submit', runValuation);
  document.getElementById('pdf-btn').addEventListener('click', generatePDF);

  renderMap(null, null);

  // ticker-style stats (if present in the page)
  const setText = (id, txt) => { const el = document.getElementById(id); if (el) el.textContent = txt; };
  setText('t-cities', META.cities_count);
  setText('t-psf', '₹' + META.avg_price_per_sqft.toLocaleString('en-IN'));
  setText('t-r2', (META.r2 * 100).toFixed(1) + '%');
  setText('t-demand', META.avg_demand + '/100');

  // chat
  const fab = document.getElementById('chat-fab');
  const panel = document.getElementById('chat-panel');
  fab.addEventListener('click', () => panel.classList.toggle('open'));
  document.getElementById('chat-close').addEventListener('click', () => panel.classList.remove('open'));
  const input = document.getElementById('chat-input');
  async function send() {
    const val = input.value.trim();
    if (!val) return;
    addMsg(val, 'user'); input.value = '';
    const reply = await chatRespond(val);
    addMsg(reply, 'bot');
  }
  document.getElementById('chat-send').addEventListener('click', send);
  input.addEventListener('keydown', e => { if (e.key === 'Enter') send(); });
  document.querySelectorAll('.chip').forEach(c => c.addEventListener('click', () => { input.value = c.textContent; send(); }));
});
