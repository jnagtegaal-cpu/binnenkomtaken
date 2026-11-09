/* Binnenkomtaken rekenen – site
 * Pagina's (via de #-link, zodat je ze kunt delen of als bladwijzer kunt bewaren):
 *   #/                     startpagina: alle groepen met de week van nu
 *   #/groep/5              groep 5: deze week en de komende weken
 *   #/groep/5/week/48      groep 5, vanaf week 48
 *   #/bord/5/48/3          nakijken op het digibord: groep 5, week 48, dag 3 (woensdag)
 * Weeknummers zijn de weken van de kalender (zoals in de agenda). Intern telt de generator lesweken 1–40;
 * de kalender (data/kalender.json) koppelt die aan de weeknummers ("kw").
 * Elke groep heeft een eigen kleur: de klasse g3 … g8 op <body> zet de CSS-variabele --g.
 */
"use strict";

const GROEPEN = [3, 4, 5, 6, 7, 8];
const DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag"];
const DAG_KORT = ["ma", "di", "wo", "do", "vr"];
const MAANDEN = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"];
const VENSTER = 6; // aantal lesweken in de lijst "komende weken"

const app = document.getElementById("app");
const kop = document.getElementById("kop");
const cache = {};
let kalender = null;

// ---------- pictogrammen ----------
const I = {
  pdf: '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 3v12m0 0-4-4m4 4 4-4M5 19h14"/></svg>',
  check: '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 11l3 3 8-8"/><path d="M20 12v6a2 2 0 0 1-2 2H6a2 2 0 0 1-2-2V6a2 2 0 0 1 2-2h9"/></svg>',
  bord: '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><rect x="3" y="4" width="18" height="12" rx="2"/><path d="M8 20h8M12 16v4"/></svg>',
  pijl: '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M9 6l6 6-6 6"/></svg>',
  zon: '<svg class="zon" viewBox="0 0 24 24" fill="#ffd43b" stroke="#1f2340" stroke-width="1.8" stroke-linecap="round"><circle cx="12" cy="12" r="4.5"/><path d="M12 2v2.5M12 19.5V22M2 12h2.5M19.5 12H22M4.9 4.9l1.8 1.8M17.3 17.3l1.8 1.8M4.9 19.1l1.8-1.8M17.3 6.7l1.8-1.8"/></svg>',
  terug: '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M15 6l-6 6 6 6"/></svg>',
  scherm: '<svg class="i" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M4 9V4h5M20 9V4h-5M4 15v5h5M20 15v5h-5"/></svg>',
};

// ---------- hulpjes ----------
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pad = (n) => String(n).padStart(2, "0");
const hoofdletter = (s) => s.charAt(0).toUpperCase() + s.slice(1);

function datum(isoStr) { const [j, m, d] = isoStr.split("-").map(Number); return new Date(j, m - 1, d); }
function iso(d) { return `${d.getFullYear()}-${pad(d.getMonth() + 1)}-${pad(d.getDate())}`; }
function plusDagen(isoStr, n) { const d = datum(isoStr); d.setDate(d.getDate() + n); return iso(d); }
function kortDatum(isoStr) { const d = datum(isoStr); return `${d.getDate()} ${MAANDEN[d.getMonth()]}`; }
function bereik(w) {
  const a = datum(w.maandag), b = datum(w.vrijdag);
  return a.getMonth() === b.getMonth()
    ? `${a.getDate()}–${b.getDate()} ${MAANDEN[b.getMonth()]}`
    : `${kortDatum(w.maandag)} – ${kortDatum(w.vrijdag)}`;
}
function vandaagIso() {
  // ?datum=2027-01-12 in de adresbalk doet alsof het die dag is (handig om te testen)
  const p = new URLSearchParams(location.search).get("datum");
  return p && /^\d{4}-\d{2}-\d{2}$/.test(p) ? p : iso(new Date());
}
function opslaan(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* geen opslag */ } }

async function json(url) {
  if (!cache[url]) {
    cache[url] = fetch(url, { cache: "no-cache" }).then((r) => {
      if (!r.ok) throw new Error(`${url}: ${r.status}`);
      return r.json();
    });
  }
  return cache[url];
}

function zetGroepkleur(g) {
  GROEPEN.forEach((x) => document.body.classList.remove(`g${x}`));
  if (g) document.body.classList.add(`g${g}`);
}

// ---------- kalender ----------
function lesweken() { return kalender.weken.filter((w) => w.lesweek); }
function weekVan(n) { return kalender.weken.find((w) => w.lesweek === n); }
function kwVan(n) { return weekVan(n).kw; }
function lesVanKw(kw) { const w = kalender.weken.find((x) => x.lesweek && x.kw === kw); return w ? w.lesweek : null; }
function bestand(g, n) { return `groep${g}/week${pad(kwVan(n))}`; }

/** De lesweek van vandaag. In een vakantie of weekend: de eerstvolgende lesweek. */
function huidig() {
  const vandaag = vandaagIso();
  const lw = lesweken();
  for (const w of lw) {
    if (vandaag <= plusDagen(w.maandag, 6)) return { lesweek: w.lesweek, bezig: vandaag >= w.maandag, week: w };
  }
  return { lesweek: 40, bezig: false, voorbij: true, week: lw[lw.length - 1] };
}
function vakantieNu() {
  const v = vandaagIso();
  const w = kalender.weken.find((x) => x.maandag <= v && v <= plusDagen(x.maandag, 6));
  if (w && w.soort === "vakantie") return w.naam;
  if (v < kalender.weken[0].maandag || v > plusDagen(kalender.weken[kalender.weken.length - 1].maandag, 6)) return "Zomervakantie";
  return null;
}
function standaardDag(n) {
  const w = weekVan(n), v = vandaagIso();
  if (w && v >= w.maandag && v <= w.vrijdag) return datum(v).getDay();
  return 1;
}
function vrijTekst(w) {
  return (w.vrije_dagen || []).map((v) => `${esc(v.naam)} (${DAG_KORT[datum(v.datum).getDay() - 1] || ""} ${kortDatum(v.datum)})`).join(", ");
}

// ---------- kop, navigatie en voet ----------
function zetNav(actief) {
  document.getElementById("groepnav").innerHTML = GROEPEN.map((g) =>
    `<a href="#/groep/${g}" class="g${g} ${g === actief ? "actief" : ""}" ${g === actief ? 'aria-current="page"' : ""}>Groep ${g}</a>`).join("");
}
function zetVoet() {
  const s = kalender.school ? `${esc(kalender.school)} · ` : "";
  document.getElementById("voet").innerHTML =
    `${s}Schooljaar ${esc(kalender.schooljaar)} · vakanties regio ${esc(kalender.regio)} · ` +
    `de bladen sluiten aan bij de automatiseringslijn van het Rekenmuurtje.`;
  document.getElementById("schoolnaam").textContent = kalender.school || "";
}

function knoppenWeek(g, n, groot) {
  const k = groot ? "" : " klein";
  return `
    <a class="knop vol${k}" href="${bestand(g, n)}.pdf" target="_blank" rel="noopener">${I.pdf}Werkblad</a>
    <a class="knop${k}" href="${bestand(g, n)}-antwoorden.pdf" target="_blank" rel="noopener">${I.check}Antwoorden</a>
    <a class="knop zacht${k}" href="#/bord/${g}/${kwVan(n)}/${standaardDag(n)}">${I.bord}Digibord</a>`;
}

// ---------- startpagina: tabel van deze week ----------
async function toonStart() {
  document.body.classList.remove("bordmodus");
  zetGroepkleur(null); zetNav(null); kop.innerHTML = "";
  document.title = kalender.school ? `Binnenkomtaken rekenen – ${kalender.school}` : "Binnenkomtaken rekenen";
  const h = huidig();
  const vak = vakantieNu();
  const kaarten = await Promise.all(GROEPEN.map(async (g) => {
    let info = null;
    try { info = (await json(`data/groep${g}.json`)).weken.find((w) => w.week === h.lesweek); } catch (e) { /* nog niet gebouwd */ }
    return `<article class="groepkaart g${g}">
      <a class="kaartkop" href="#/groep/${g}"><span class="badge">${g}</span><strong>Groep ${g}</strong>
        <span class="meer">alle weken${I.pijl}</span></a>
      <p class="thema">${info ? esc(info.thema) : "Nog niet beschikbaar"}</p>
      <div class="acties">${info ? knoppenWeek(g, h.lesweek, false) : ""}</div>
    </article>`;
  }));
  app.innerHTML = `
    <div class="paginakop">
      <h1>${h.bezig ? "Deze week" : "Volgende week"}: week ${h.week.kw}</h1>
      <div class="sub">${hoofdletter(bereik(h.week))} · elke dag na de pauze tien sommen</div>
    </div>
    ${vak ? `<p class="melding">Het is nu ${esc(vak.toLowerCase())}. Je ziet de eerste week na de vakantie.</p>` : ""}
    ${h.week.vrije_dagen ? `<p class="melding">Deze week vrij: ${vrijTekst(h.week)}. Er blijft een strookje over voor extra herhaling.</p>` : ""}
    <section class="kaarten" aria-label="Binnenkomtaken per groep">${kaarten.join("")}</section>
    <section class="stappen">
      <div><b>1</b><h3>Printen</h3><p>Download het werkblad van deze week en print één blad per leerling.</p></div>
      <div><b>2</b><h3>Snijden</h3><p>Snijd langs de stippellijnen: vijf stroken, één per dag. Leg ze na de pauze klaar.</p></div>
      <div><b>3</b><h3>Nakijken</h3><p>Open <em>Digibord</em> en tik op een geel vakje om het antwoord te laten zien.</p></div>
    </section>`;
}

// ---------- groepspagina ----------
async function toonGroep(g, vanaf) {
  document.body.classList.remove("bordmodus");
  zetGroepkleur(g); zetNav(g); opslaan("laatsteGroep", String(g));
  document.title = `Groep ${g} – Binnenkomtaken rekenen`;
  const data = await json(`data/groep${g}.json`);
  const h = huidig();
  const vak = vakantieNu();
  const focus = Math.min(Math.max(vanaf || h.lesweek, 1), 40);
  const info = (n) => data.weken.find((x) => x.week === n);
  const fw = weekVan(focus);
  const fi = info(focus);
  const isNu = focus === h.lesweek;

  // de lijst: de weken na de uitgelichte week, met vakanties ertussen
  const ws = kalender.weken;
  const i0 = ws.indexOf(fw) + 1;
  let teller = 0;
  const lijst = [];
  for (let i = i0; i < ws.length && teller < VENSTER; i++) {
    const w = ws[i];
    if (w.lesweek) {
      teller++;
      const x = info(w.lesweek);
      lijst.push(`<div class="rij">
        <div class="wk">Week ${w.kw}<small>${bereik(w)}</small></div>
        <div class="thema"><strong>${x ? esc(x.thema) : "Nog niet beschikbaar"}</strong>
          ${w.vrije_dagen ? `<div class="vrij">Vrij: ${vrijTekst(w)}</div>` : ""}</div>
        <div class="acties">${x ? knoppenWeek(g, w.lesweek, false) : ""}</div>
      </div>`);
    } else if (lijst.length) {
      lijst.push(`<div class="rij vak"><div class="wk">Week ${w.kw}</div><div class="naam">${I.zon}${esc(w.naam)}</div><div>${bereik(w)}</div></div>`);
    }
  }

  const opties = lesweken().map((w) => `<option value="${w.lesweek}" ${w.lesweek === focus ? "selected" : ""}>Week ${w.kw} · ${bereik(w)}</option>`).join("");
  kop.innerHTML = `
    <section class="groepkop"><div class="groepkop-in">
      <div class="titel"><span class="badge">${g}</span><div><h1>Groep ${g}</h1><div class="sub">${h.bezig ? "Deze week" : "Volgende week"}: week ${h.week.kw} · ${bereik(h.week)}</div></div></div>
      <div class="bladeren">
        <button class="knop klein" id="eerder" ${focus <= 1 ? "disabled" : ""}>${I.terug}Vorige</button>
        <button class="knop klein" id="nu" ${isNu ? "disabled" : ""}>Deze week</button>
        <button class="knop klein" id="later" ${focus >= 40 ? "disabled" : ""}>Volgende${I.pijl}</button>
        <select class="knop klein" id="kies" aria-label="Ga naar week">${opties}</select>
      </div>
    </div></section>`;

  app.innerHTML = `
    ${vak && !vanaf ? `<p class="melding">Het is nu ${esc(vak.toLowerCase())}. Hieronder staat de eerste week na de vakantie.</p>` : ""}
    <article class="nu-kaart">
      <div>
        <span class="etiket">${isNu ? (h.bezig ? "Deze week" : "Volgende week") : (focus < h.lesweek ? "Eerdere week" : "Later dit jaar")}</span>
        <h2>Week ${fw.kw} <span class="datum">· ${bereik(fw)}</span></h2>
        <p class="thema-groot">${fi ? esc(fi.thema) : "Dit blad is nog niet beschikbaar."}</p>
        ${fw.vrije_dagen ? `<div class="vrij">Vrij: ${vrijTekst(fw)}. Er blijft een strookje over voor extra herhaling.</div>` : ""}
      </div>
      <div class="acties">${fi ? knoppenWeek(g, focus, true) : ""}</div>
    </article>
    ${lijst.length ? `<h2 class="sectie">Daarna</h2><section class="lijst">${lijst.join("")}</section>` : ""}
    <h2 class="sectie">Heel schooljaar</h2>
    <div class="jaar">
      <a class="knop" href="groep${g}/groep${g}-heel-jaar.pdf" target="_blank" rel="noopener">${I.pdf}Alle 40 werkbladen</a>
      <a class="knop" href="groep${g}/groep${g}-antwoorden-heel-jaar.pdf" target="_blank" rel="noopener">${I.check}Alle antwoorden</a>
      <a class="knop" href="groep${g}/groep${g}-jaaroverzicht.pdf" target="_blank" rel="noopener">${I.pdf}Jaaroverzicht: opbouw per week</a>
    </div>`;

  const naar = (n) => { location.hash = n === h.lesweek ? `#/groep/${g}` : `#/groep/${g}/week/${kwVan(n)}`; };
  document.getElementById("eerder").onclick = () => naar(Math.max(1, focus - 1));
  document.getElementById("later").onclick = () => naar(Math.min(40, focus + 1));
  document.getElementById("nu").onclick = () => naar(h.lesweek);
  document.getElementById("kies").onchange = (e) => naar(Number(e.target.value));
}

// ---------- digibord ----------
let bordToetsen = null;

async function toonBord(g, n, dag) {
  document.body.classList.add("bordmodus");
  zetGroepkleur(g); zetNav(g);
  n = Math.min(Math.max(n, 1), 40);
  dag = Math.min(Math.max(dag, 1), 5);
  const w = weekVan(n);
  const meta = await json(`${bestand(g, n)}.json`);
  const dd = meta.dagen[dag - 1];
  const datumDag = plusDagen(w.maandag, dag - 1);
  document.title = `Nakijken groep ${g} – week ${w.kw} ${DAGEN[dag - 1]}`;
  const vrijeDatums = new Set((w.vrije_dagen || []).map((v) => v.datum));

  const tabs = DAGEN.map((naam, i) => {
    const dIso = plusDagen(w.maandag, i);
    return `<button data-dag="${i + 1}" class="${i + 1 === dag ? "actief" : ""} ${vrijeDatums.has(dIso) ? "vrij" : ""}"
      ${vrijeDatums.has(dIso) ? 'title="vrije dag"' : ""}>${hoofdletter(DAG_KORT[i])}<small>${kortDatum(dIso)}</small></button>`;
  }).join("");

  // vakjes over de antwoorden; bij omcirkel- en tekenopdrachten dekt het vakje de hele opdracht af
  const dekkingen = dd.vakjes.map((rects, i) => rects.map(([x, y, bw, bh], j) => {
    const isCel = rects.length === 1 && bw > 0.12;
    const p = isCel ? 0 : 0.004;
    return `<button class="dekking ${isCel ? "cel" : ""}" data-i="${i}" aria-label="Antwoord ${i + 1} tonen"
      style="left:${(x - p) * 100}%;top:${(y - p * 3.55) * 100}%;width:${(bw + 2 * p) * 100}%;height:${(bh + 2 * p * 3.55) * 100}%">${j === 0 ? i + 1 : ""}</button>`;
  }).join("")).join("");

  kop.innerHTML = `
    <section class="bordbalk"><div class="bordbalk-in">
      <div><h1>Groep ${g} · Week ${w.kw} · ${DAGEN[dag - 1]} ${kortDatum(datumDag)}</h1><div class="sub">${esc(meta.thema)}</div></div>
      <div class="dagen" role="tablist" aria-label="Dag">${tabs}</div>
    </div></section>`;
  app.innerHTML = `
    <div class="bordvlak">
      <div class="strook" id="strook">
        <img src="${bestand(g, n)}-dag${dag}.png" alt="Strook met antwoorden, ${DAGEN[dag - 1]} week ${w.kw}">
        ${dekkingen}
      </div>
      <div class="bordknoppen">
        <button class="knop vol" id="volgende">Volgend antwoord${I.pijl}</button>
        <button class="knop" id="alles">Alles tonen</button>
        <button class="knop" id="verberg">Alles verbergen</button>
        <button class="knop" id="vorigeDag">${I.terug}Vorige dag</button>
        <button class="knop" id="volgendeDag">Volgende dag${I.pijl}</button>
        <button class="knop" id="scherm">${I.scherm}Volledig scherm</button>
        <a class="knop" href="#/groep/${g}/week/${w.kw}">Terug</a>
      </div>
      <p class="tip">Tik op een geel vakje om het antwoord te zien. Toetsen: spatie = volgend antwoord, A = alles tonen, V = alles verbergen, ←/→ = vorige/volgende dag.</p>
      <details class="tekstantw"><summary>Antwoorden als tekst</summary><ol>${dd.antwoorden.map((a) => `<li>${esc(a)}</li>`).join("")}</ol></details>
    </div>`;

  const dek = [...app.querySelectorAll(".dekking")];
  const groep = (i) => dek.filter((x) => x.dataset.i === i);
  dek.forEach((b) => { b.onclick = () => groep(b.dataset.i).forEach((x) => x.classList.toggle("open")); });
  const volgende = () => { const d = dek.find((x) => !x.classList.contains("open")); if (d) groep(d.dataset.i).forEach((x) => x.classList.add("open")); };
  const alles = (open) => dek.forEach((x) => x.classList.toggle("open", open));
  const gaNaarDag = (stap) => {
    let nn = n, d2 = dag + stap;
    if (d2 < 1) { if (nn > 1) { nn--; d2 = 5; } else d2 = 1; }
    if (d2 > 5) { if (nn < 40) { nn++; d2 = 1; } else d2 = 5; }
    location.hash = `#/bord/${g}/${kwVan(nn)}/${d2}`;
  };
  kop.querySelectorAll(".dagen button").forEach((b) => { b.onclick = () => { location.hash = `#/bord/${g}/${w.kw}/${b.dataset.dag}`; }; });
  document.getElementById("volgende").onclick = volgende;
  document.getElementById("alles").onclick = () => alles(true);
  document.getElementById("verberg").onclick = () => alles(false);
  document.getElementById("vorigeDag").onclick = () => gaNaarDag(-1);
  document.getElementById("volgendeDag").onclick = () => gaNaarDag(1);
  document.getElementById("scherm").onclick = () => {
    const el = document.documentElement;
    if (!document.fullscreenElement && el.requestFullscreen) el.requestFullscreen().catch(() => {});
    else if (document.exitFullscreen) document.exitFullscreen().catch(() => {});
  };
  if (bordToetsen) document.removeEventListener("keydown", bordToetsen);
  bordToetsen = (e) => {
    if (!location.hash.startsWith("#/bord/")) return;
    if (e.key === " " || e.key === "Enter") { e.preventDefault(); volgende(); }
    else if (e.key === "a" || e.key === "A") alles(true);
    else if (e.key === "v" || e.key === "V") alles(false);
    else if (e.key === "ArrowRight" || e.key === "PageDown") gaNaarDag(1);
    else if (e.key === "ArrowLeft" || e.key === "PageUp") gaNaarDag(-1);
  };
  document.addEventListener("keydown", bordToetsen);
}

// ---------- router ----------
async function route() {
  const p = location.hash.replace(/^#\/?/, "").split("/").filter(Boolean);
  try {
    if (!kalender) { kalender = await json("data/kalender.json"); zetVoet(); }
    if (p[0] === "groep" && GROEPEN.includes(Number(p[1]))) {
      await toonGroep(Number(p[1]), p[2] === "week" ? lesVanKw(Number(p[3])) : null);
    } else if (p[0] === "bord" && GROEPEN.includes(Number(p[1]))) {
      await toonBord(Number(p[1]), lesVanKw(Number(p[2])) || huidig().lesweek, Number(p[3]) || 1);
    } else {
      await toonStart();
    }
  } catch (e) {
    console.error(e);
    kop.innerHTML = "";
    app.innerHTML = `<p class="melding">Er ging iets mis bij het laden. Probeer de pagina te verversen.</p>`;
  }
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);
route();
