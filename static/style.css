:root{
  --ink:#11131C;
  --ink-2:rgba(27,30,44,0.60);
  --ink-2-solid:#1B1E2C;
  --paper:#F5F1E8;
  --brass:#F2B84B;
  --brass-dim:#d8b02e;
  --teal:#2FD9C4;
  --coral:#FF6F61;
  --violet:#8B7FD6;
  --blue:#5AA9E6;
  --line:rgba(245,241,232,0.14);
  --glass:rgba(27,30,44,0.55);
  --glass-2:rgba(27,30,44,0.72);
  --serif:'Fraunces',serif;
  --sans:'Inter',sans-serif;
}
*{box-sizing:border-box;}
html{scroll-behavior:smooth;}

/* ===== FULL-PAGE 360 HOUSE BACKGROUND ===== */
body{
  margin:0;
  background:var(--ink);
  color:var(--paper);
  font-family:var(--sans);
  line-height:1.5;
  -webkit-font-smoothing:antialiased;
  position:relative;
  min-height:100vh;
}
body::before{
  content:'';
  position:fixed;
  inset:0;
  background-image:
    linear-gradient(160deg, rgba(17,19,28,0.74) 0%, rgba(17,19,28,0.84) 45%, rgba(12,13,20,0.94) 100%),
    url('https://images.unsplash.com/photo-1613977257363-707ba9348227?auto=format&fit=crop&w=2000&q=80');
  background-size:cover;
  background-position:center;
  background-attachment:fixed;
  background-repeat:no-repeat;
  filter:saturate(1.1) brightness(0.85);
  z-index:-2;
}
body::after{
  content:'';
  position:fixed;
  inset:0;
  background:
    radial-gradient(circle at 15% 20%, rgba(90,169,230,0.22), transparent 45%),
    radial-gradient(circle at 85% 15%, rgba(255,111,97,0.18), transparent 45%),
    radial-gradient(circle at 50% 90%, rgba(47,217,196,0.18), transparent 50%);
  z-index:-1;
  pointer-events:none;
}
@media(max-width:800px){
  body::before{background-attachment:scroll;}
}

::selection{background:var(--brass);color:var(--ink);}

a{color:inherit;}
img,svg{display:block;max-width:100%;}

.wrap{max-width:1180px;margin:0 auto;padding:0 28px;}

/* NAV */
header.nav{
  position:sticky;top:0;z-index:50;
  background:rgba(17,19,28,0.58);
  backdrop-filter:blur(14px) saturate(1.3);
  -webkit-backdrop-filter:blur(14px) saturate(1.3);
  border-bottom:1px solid var(--line);
}
.nav-inner{display:flex;align-items:center;justify-content:space-between;padding:16px 28px;max-width:1180px;margin:0 auto;}
.brand{display:flex;align-items:center;gap:10px;font-family:var(--serif);font-weight:600;font-size:20px;letter-spacing:0.2px;}
.brand .mark{
  width:30px;height:30px;border-radius:50%;
  background:linear-gradient(135deg,var(--coral),var(--brass),var(--teal));
  display:flex;align-items:center;justify-content:center;font-size:13px;color:#151622;font-weight:800;
  box-shadow:0 0 14px rgba(242,184,75,0.4);
}
nav.links{display:flex;gap:28px;font-size:14px;}
nav.links a{opacity:0.78;text-decoration:none;transition:all .2s;}
nav.links a:nth-child(1):hover{opacity:1;color:var(--coral);}
nav.links a:nth-child(2):hover{opacity:1;color:var(--brass);}
nav.links a:nth-child(3):hover{opacity:1;color:var(--teal);}
nav.links a:nth-child(4):hover{opacity:1;color:var(--blue);}
nav.links a:nth-child(5):hover{opacity:1;color:var(--violet);}
@media(max-width:820px){nav.links{display:none;}}

/* HERO */
.hero{padding:88px 0 64px;position:relative;overflow:hidden;}
.hero-grid{display:grid;grid-template-columns:1.15fr 0.85fr;gap:56px;align-items:center;}
@media(max-width:900px){.hero-grid{grid-template-columns:1fr;}}
.eyebrow{font-size:12.5px;letter-spacing:2.4px;text-transform:uppercase;color:var(--brass);font-weight:600;margin-bottom:18px;display:block;}
h1.hero-title{
  font-family:var(--serif);
  font-size:clamp(38px,5vw,60px);
  font-weight:600;
  line-height:1.06;
  margin:0 0 22px;
  letter-spacing:-0.5px;
  text-shadow:0 2px 30px rgba(0,0,0,0.4);
}
h1.hero-title em{
  font-style:italic;font-weight:500;
  background:linear-gradient(135deg,var(--coral),var(--brass));
  -webkit-background-clip:text;background-clip:text;color:transparent;
}
.hero-sub{font-size:17px;opacity:0.85;max-width:480px;margin-bottom:32px;}
.btn{
  display:inline-flex;align-items:center;gap:8px;
  background:linear-gradient(135deg,var(--coral),var(--brass));
  color:#1D1108;
  border:none;padding:14px 26px;border-radius:6px;
  font-family:var(--sans);font-weight:700;font-size:15px;
  cursor:pointer;transition:transform .15s ease,box-shadow .2s,filter .2s;
  text-decoration:none;
  box-shadow:0 8px 24px rgba(255,111,97,0.28);
}
.btn:hover{filter:brightness(1.08);transform:translateY(-2px);box-shadow:0 12px 30px rgba(255,111,97,0.4);}
.btn.ghost{background:rgba(255,255,255,0.06);border:1px solid rgba(245,241,232,0.35);color:var(--paper);box-shadow:none;}
.btn.ghost:hover{border-color:var(--brass);color:var(--brass);background:rgba(242,184,75,0.08);transform:translateY(-2px);}
.btn.full{width:100%;justify-content:center;padding:16px;font-size:16px;}

/* 360 HOUSE VISUAL */
.house-360-wrap{
  position:relative;width:300px;height:300px;margin:0 auto 30px;
}
.house-360-ring{
  position:absolute;inset:0;border-radius:50%;
  background:conic-gradient(from 0deg,var(--coral),var(--brass),var(--teal),var(--blue),var(--violet),var(--coral));
  animation:ringSpin 10s linear infinite;
  padding:7px;
  box-shadow:0 20px 60px rgba(0,0,0,0.55);
}
.house-360-ring-inner{
  width:100%;height:100%;border-radius:50%;background:var(--ink);
}
.house-360-photo{
  position:absolute;inset:15px;border-radius:50%;overflow:hidden;
  box-shadow:inset 0 0 0 2px rgba(255,255,255,0.08);
}
.house-360-photo img{width:100%;height:100%;object-fit:cover;display:block;}
@keyframes ringSpin{to{transform:rotate(360deg);}}
.house-360-badge{
  position:absolute;bottom:2px;left:50%;transform:translateX(-50%);
  background:linear-gradient(135deg,var(--blue),var(--teal));
  color:#0E1420;font-size:11px;font-weight:800;letter-spacing:1.2px;
  padding:7px 16px;border-radius:20px;box-shadow:0 8px 20px rgba(0,0,0,0.45);
  white-space:nowrap;
}

.ticker{display:flex;gap:0;border-top:1px solid var(--line);margin-top:40px;padding-top:0;overflow-x:auto;}
.ticker-item{flex:1;min-width:140px;padding:20px 22px;border-right:1px solid var(--line);}
.ticker-item:last-child{border-right:none;}
.ticker-item .val{font-family:var(--serif);font-size:26px;}
.ticker-item:nth-child(1) .val{color:var(--coral);}
.ticker-item:nth-child(2) .val{color:var(--brass);}
.ticker-item:nth-child(3) .val{color:var(--teal);}
.ticker-item:nth-child(4) .val{color:var(--blue);}
.ticker-item .lbl{font-size:11.5px;text-transform:uppercase;letter-spacing:1px;opacity:0.65;margin-top:4px;}

/* SECTIONS */
section{padding:80px 0;border-top:1px solid var(--line);}
.section-head{margin-bottom:44px;max-width:640px;}
.section-head .eyebrow{margin-bottom:12px;}
.section-head h2{font-family:var(--serif);font-size:clamp(28px,3.4vw,38px);font-weight:600;margin:0 0 14px;letter-spacing:-0.3px;text-shadow:0 2px 20px rgba(0,0,0,0.35);}
.section-head p{opacity:0.78;font-size:15.5px;margin:0;}

/* GLASS PANELS (used everywhere a card sits over the background) */
.ledger,.stamp-card,.waterfall,.chart-card,.info-card,.fac-card,.rec-card,.conv-gauge,.chat-panel{
  background:var(--glass);
  border:1px solid var(--line);
  border-radius:12px;
  backdrop-filter:blur(16px) saturate(1.2);
  -webkit-backdrop-filter:blur(16px) saturate(1.2);
  box-shadow:0 12px 40px rgba(0,0,0,0.35);
}

/* FORM (ledger style) */
.ledger{padding:36px;}
.ledger-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:22px 24px;}
@media(max-width:760px){.ledger-grid{grid-template-columns:repeat(2,1fr);}}
@media(max-width:520px){.ledger-grid{grid-template-columns:1fr;}}
.field{display:flex;flex-direction:column;gap:8px;}
.field label{font-size:11.5px;text-transform:uppercase;letter-spacing:1px;opacity:0.7;}
.field select,.field input{
  background:rgba(10,10,16,0.5);border:1px solid var(--line);color:var(--paper);
  padding:11px 12px;font-family:var(--sans);font-size:14.5px;border-radius:6px;
  outline:none;transition:border-color .2s,box-shadow .2s;
}
.field select:focus,.field input:focus{border-color:var(--brass);box-shadow:0 0 0 3px rgba(242,184,75,0.18);}
.checks{grid-column:1/-1;display:flex;flex-wrap:wrap;gap:14px 26px;padding-top:6px;border-top:1px dashed var(--line);margin-top:6px;}
.chk{display:flex;align-items:center;gap:8px;font-size:14px;opacity:0.88;cursor:pointer;}
.chk input{accent-color:var(--brass);width:16px;height:16px;}
.ledger-actions{margin-top:28px;display:flex;gap:14px;flex-wrap:wrap;}

/* RESULT */
.result-wrap{display:none;margin-top:56px;}
.result-wrap.show{display:block;animation:fadeUp .5s ease both;}
@keyframes fadeUp{from{opacity:0;transform:translateY(14px);}to{opacity:1;transform:translateY(0);}}
.result-grid{display:grid;grid-template-columns:340px 1fr;gap:36px;}
@media(max-width:860px){.result-grid{grid-template-columns:1fr;}}

.stamp-card{
  padding:32px;
  display:flex;flex-direction:column;align-items:center;text-align:center;position:relative;
}
.seal{
  width:150px;height:150px;border-radius:50%;
  border:3px solid transparent;
  background:
    linear-gradient(var(--ink-2-solid),var(--ink-2-solid)) padding-box,
    conic-gradient(from 90deg,var(--coral),var(--brass),var(--teal),var(--blue),var(--coral)) border-box;
  display:flex;align-items:center;justify-content:center;flex-direction:column;
  transform:rotate(-6deg);
  margin-bottom:22px;position:relative;
}
.seal::before{
  content:'';position:absolute;inset:8px;border:1px dashed rgba(242,184,75,0.5);border-radius:50%;
}
.seal .tag{font-size:9px;letter-spacing:1.6px;text-transform:uppercase;color:var(--brass);margin-bottom:4px;}
.seal .amt{font-family:var(--serif);font-size:22px;font-weight:600;color:var(--paper);line-height:1.15;}
.stamp-card .range{font-size:13px;opacity:0.65;margin-top:2px;}
.stamp-card .conf{margin-top:18px;font-size:12.5px;opacity:0.65;}
.stamp-card .conf b{color:var(--teal);}

.waterfall{padding:28px 32px;}
.waterfall h3{font-family:var(--serif);font-size:18px;margin:0 0 4px;font-weight:600;}
.waterfall .wf-sub{font-size:13px;opacity:0.65;margin-bottom:22px;}
.wf-row{display:grid;grid-template-columns:170px 1fr 90px;gap:12px;align-items:center;margin-bottom:10px;font-size:13px;}
.wf-bar-track{background:rgba(255,255,255,0.08);height:18px;border-radius:4px;position:relative;overflow:hidden;}
.wf-bar{height:100%;border-radius:4px;position:absolute;top:0;}
.wf-bar.pos{background:linear-gradient(90deg,var(--teal),#8FF5E4);left:50%;}
.wf-bar.neg{background:linear-gradient(90deg,#FF9A8F,var(--coral));right:50%;}
.wf-mid{position:absolute;left:50%;top:0;bottom:0;width:1px;background:rgba(255,255,255,0.25);}
.wf-val{text-align:right;opacity:0.8;font-variant-numeric:tabular-nums;}

/* FORECAST */
.forecast-grid{display:grid;grid-template-columns:1fr 320px;gap:36px;}
@media(max-width:860px){.forecast-grid{grid-template-columns:1fr;}}
.chart-card,.info-card{padding:28px 32px;}
.info-card h4{font-family:var(--serif);margin:0 0 14px;font-size:16px;}
.info-row{display:flex;justify-content:space-between;font-size:13.5px;padding:9px 0;border-bottom:1px solid var(--line);}
.info-row:last-child{border-bottom:none;}
.info-row .v{color:var(--brass);font-variant-numeric:tabular-nums;}

/* MAP */
#map{height:460px;border-radius:12px;border:1px solid var(--line);filter:saturate(1.05);box-shadow:0 12px 40px rgba(0,0,0,0.35);}
.legend{display:flex;gap:20px;margin-top:16px;flex-wrap:wrap;font-size:12.5px;opacity:0.8;}
.legend .dot{width:10px;height:10px;border-radius:50%;display:inline-block;margin-right:6px;}

/* FACILITIES */
.fac-grid{display:grid;grid-template-columns:repeat(5,1fr);gap:18px;}
@media(max-width:900px){.fac-grid{grid-template-columns:repeat(2,1fr);}}
.fac-card{padding:22px 18px;text-align:center;transition:transform .2s;}
.fac-card:hover{transform:translateY(-4px);}
.fac-card .icon{font-size:26px;margin-bottom:10px;}
.fac-card .name{font-size:13.5px;font-weight:600;margin-bottom:4px;}
.fac-card .dist{font-size:12px;opacity:0.65;}
.conv-gauge{margin-top:26px;padding:22px 26px;display:flex;align-items:center;gap:22px;}
.gauge-track{flex:1;height:9px;background:rgba(255,255,255,0.1);border-radius:5px;overflow:hidden;}
.gauge-fill{height:100%;background:linear-gradient(90deg,var(--coral),var(--brass),var(--teal),var(--blue));}

/* RECOMMENDATION */
.rec-card{padding:36px;display:grid;grid-template-columns:220px 1fr;gap:32px;align-items:center;}
@media(max-width:760px){.rec-card{grid-template-columns:1fr;}}
.rec-badge{padding:20px;border-radius:10px;text-align:center;font-family:var(--serif);font-size:24px;font-weight:600;letter-spacing:0.5px;}
.rec-badge.buy{background:rgba(47,217,196,0.16);color:var(--teal);border:1px solid var(--teal);box-shadow:0 0 24px rgba(47,217,196,0.25);}
.rec-badge.wait{background:rgba(242,184,75,0.16);color:var(--brass);border:1px solid var(--brass);box-shadow:0 0 24px rgba(242,184,75,0.25);}
.rec-badge.avoid{background:rgba(255,111,97,0.16);color:var(--coral);border:1px solid var(--coral);box-shadow:0 0 24px rgba(255,111,97,0.25);}
.rec-reasons{list-style:none;padding:0;margin:0 0 18px;}
.rec-reasons li{font-size:14px;padding:8px 0;border-bottom:1px solid var(--line);opacity:0.88;}
.rec-reasons li:last-child{border-bottom:none;}
.rec-neg{font-size:13.5px;opacity:0.75;}
.rec-neg b{color:var(--brass);font-size:16px;}

/* CHATBOT */
.chat-fab{
  position:fixed;bottom:26px;right:26px;z-index:60;
  width:58px;height:58px;border-radius:50%;
  background:linear-gradient(135deg,var(--coral),var(--brass));
  color:#1D1108;
  display:flex;align-items:center;justify-content:center;font-size:24px;cursor:pointer;
  border:none;box-shadow:0 8px 24px rgba(0,0,0,0.45);
  transition:transform .2s;
}
.chat-fab:hover{transform:scale(1.08);}
.chat-panel{
  position:fixed;bottom:96px;right:26px;z-index:60;width:340px;max-height:460px;
  display:none;flex-direction:column;overflow:hidden;
}
.chat-panel.open{display:flex;}
.chat-head{padding:14px 16px;border-bottom:1px solid var(--line);font-family:var(--serif);font-size:15px;display:flex;justify-content:space-between;align-items:center;}
.chat-head span.dot{width:8px;height:8px;border-radius:50%;background:var(--teal);display:inline-block;margin-right:6px;box-shadow:0 0 8px var(--teal);}
.chat-body{flex:1;overflow-y:auto;padding:14px 16px;display:flex;flex-direction:column;gap:10px;font-size:13.5px;}
.msg{max-width:85%;padding:9px 12px;border-radius:10px;line-height:1.4;}
.msg.bot{background:rgba(255,255,255,0.08);align-self:flex-start;border-bottom-left-radius:2px;}
.msg.user{background:linear-gradient(135deg,var(--brass),var(--coral));color:#1D1108;align-self:flex-end;border-bottom-right-radius:2px;}
.chat-input{display:flex;border-top:1px solid var(--line);}
.chat-input input{flex:1;background:transparent;border:none;color:var(--paper);padding:12px 14px;font-size:13.5px;outline:none;}
.chat-input button{background:none;border:none;color:var(--brass);padding:0 16px;cursor:pointer;font-size:16px;}
.chat-suggest{display:flex;flex-wrap:wrap;gap:6px;padding:0 16px 10px;}
.chip{font-size:11.5px;padding:5px 10px;border:1px solid var(--line);border-radius:12px;cursor:pointer;opacity:0.78;}
.chip:hover{border-color:var(--brass);color:var(--brass);opacity:1;}

footer{padding:40px 0 60px;text-align:center;font-size:13px;opacity:0.55;border-top:1px solid var(--line);}

.hidden{display:none!important;}
.small-note{font-size:12px;opacity:0.6;margin-top:10px;}