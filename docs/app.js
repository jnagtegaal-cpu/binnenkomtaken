/* Binnenkomtaken rekenen – site
 * Pagina's (via de #-link, zodat je ze kunt delen of als bladwijzer kunt bewaren):
 *   #/                     startpagina met de groepen
 *   #/groep/5              groep 5, deze week en de komende weken
 *   #/groep/5/week/48      groep 5, vanaf week 48
 *   #/bord/5/48/3          nakijken op het digibord: groep 5, week 48, dag 3 (woensdag)
 * Weeknummers zijn de weken van de kalender (zoals in de agenda). Intern telt de generator lesweken 1–40;
 * de kalender (data/kalender.json) koppelt die aan de weeknummers ("kw").
 * Gegevens: data/kalender.json (schoolweken) en data/groepN.json + groepN/weekNN.json (gemaakt door generator/bouw.py).
 */
"use strict";

const GROEPEN = [3, 4, 5, 6, 7, 8];
const DAGEN = ["maandag", "dinsdag", "woensdag", "donderdag", "vrijdag"];
const DAG_KORT = ["ma", "di", "wo", "do", "vr"];
const MAANDEN = ["jan", "feb", "mrt", "apr", "mei", "jun", "jul", "aug", "sep", "okt", "nov", "dec"];
const VENSTER = 4; // aantal lesweken dat de groepspagina tegelijk laat zien

const app = document.getElementById("app");
const cache = {};
let kalender = null;

// ---------- hulpjes ----------
const $ = (html) => { const t = document.createElement("template"); t.innerHTML = html.trim(); return t.content.firstElementChild; };
const esc = (s) => String(s).replace(/[&<>"']/g, (c) => ({ "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;" }[c]));
const pad = (n) => String(n).padStart(2, "0");

function datum(iso) { const [j, m, d] = iso.split("-").map(Number); return new Date(j, m - 1, d); }
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

function opslaan(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* geen opslag beschikbaar */ } }
function ophalen(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }

async function json(url) {
  if (!cache[url]) {
    cache[url] = fetch(url, { cache: "no-cache" }).then((r) => {
      if (!r.ok) throw new Error(`${url}: ${r.status}`);
      return r.json();
    });
  }
  return cache[url];
}

// ---------- kalender ----------
function lesweken() { return kalender.weken.filter((w) => w.lesweek); }
function weekVan(n) { return kalender.weken.find((w) => w.lesweek === n); }
function kwVan(n) { return weekVan(n).kw; }
/** Weeknummer van de kalender -> lesweek (of null als die week geen blad heeft). */
function lesVanKw(kw) { const w = kalender.weken.find((x) => x.lesweek && x.kw === kw); return w ? w.lesweek : null; }
function bestand(g, n) { return `groep${g}/week${pad(kwVan(n))}`; }

/** De lesweek van vandaag. In een vakantie of weekend: de eerstvolgende lesweek. */
function huidig() {
  const vandaag = vandaagIso();
  const lw = lesweken();
  for (const w of lw) {
    if (vandaag <= plusDagen(w.maandag, 6)) {
      return { lesweek: w.lesweek, bezig: vandaag >= w.maandag, week: w };
    }
  }
  return { lesweek: 40, bezig: false, voorbij: true, week: lw[lw.length - 1] };
}

/** Is vandaag een vakantie? Geeft de naam terug. */
function vakantieNu() {
  const v = vandaagIso();
  const w = kalender.weken.find((x) => x.maandag <= v && v <= plusDagen(x.maandag, 6));
  if (w && w.soort === "vakantie") return w.naam;
  if (v < kalender.weken[0].maandag || v > plusDagen(kalender.weken[kalender.weken.length - 1].maandag, 6)) return "zomer";
  return null;
}

/** Dagnummer (1–5) van vandaag binnen lesweek n, anders 1. */
function standaardDag(n) {
  const w = weekVan(n);
  const v = vandaagIso();
  if (w && v >= w.maandag && v <= w.vrijdag) return datum(v).getDay(); // ma=1 … vr=5
  return 1;
}

// ---------- kop en voet ----------
function zetNav(actief) {
  const nav = document.getElementById("groepnav");
  nav.innerHTML = GROEPEN.map((g) => `<a href="#/groep/${g}" class="${g === actief ? "actief" : ""}">Groep ${g}</a>`).join("");
}
function zetVoet() {
  document.getElementById("voet").innerHTML =
    `Schooljaar ${esc(kalender.schooljaar)} · vakanties regio ${esc(kalender.regio)} · ` +
    `bladen sluiten aan bij de automatiseringslijn van het Rekenmuurtje.`;
}

// ---------- startpagina ----------
async function toonStart() {
  document.body.classList.remove("bordmodus");
  zetNav(null);
  document.title = "Binnenkomtaken rekenen";
  const h = huidig();
  const laatst = Number(ophalen("laatsteGroep"));
  const vak = vakantieNu();
  const tegels = await Promise.all(GROEPEN.map(async (g) => {
    let thema = "";
    try { const d = await json(`data/groep${g}.json`); thema = (d.weken.find((w) => w.week === h.lesweek) || {}).thema || ""; } catch (e) { /* nog niet gebouwd */ }
    return `<a class="tegel ${g === laatst ? "laatst" : ""}" href="#/groep/${g}">
      <div class="nr">${g}</div><div class="lbl">Groep ${g}</div>
      <div class="nu">${h.bezig ? "Deze week" : "Volgende week"}: week ${kwVan(h.lesweek)}${thema ? `<br>${esc(thema)}` : ""}</div></a>`;
  }));
  app.innerHTML = `
    <section class="intro">
      <h1>Kies je groep</h1>
      <p>Elke dag na de pauze een strookje met tien sommen. Per week één werkblad: print het voor je hele klas,
      snijd het in vijf stroken en leg elke dag een stapeltje klaar. Nakijken doen de kinderen zelf met het digibord.</p>
      ${vak ? `<p class="melding">Het is nu ${vak === "zomer" ? "zomervakantie" : esc(vak.toLowerCase())}. Je ziet de eerste week na de vakantie.</p>` : ""}
    </section>
    <div class="tegels">${tegels.join("")}</div>
    <section class="uitleg">
      <div><h3>1. Printen</h3><p>Open je groep en download het werkblad van deze week. Print één blad per leerling.</p></div>
      <div><h3>2. Snijden</h3><p>Snijd langs de stippellijnen: vijf stroken, één per dag. Leg ze na de pauze klaar.</p></div>
      <div><h3>3. Nakijken</h3><p>Open <em>Nakijken op het digibord</em>. Tik op een geel vakje om het antwoord te laten zien.</p></div>
    </section>`;
}

// ---------- groepspagina ----------
async function toonGroep(g, vanaf) {
  document.body.classList.remove("bordmodus");
  zetNav(g);
  opslaan("laatsteGroep", String(g));
  document.title = `Groep ${g} – Binnenkomtaken`;
  const data = await json(`data/groep${g}.json`);
  const h = huidig();
  const start = Math.min(Math.max(vanaf || h.lesweek, 1), 40);
  const eind = Math.min(start + VENSTER - 1, 40);
  const vak = vakantieNu();

  // alle kalenderweken van start t/m eind, inclusief vakanties ertussen
  const ws = kalender.weken;
  const i0 = ws.findIndex((w) => w.lesweek === start);
  const i1 = ws.findIndex((w) => w.lesweek === eind);
  const blok = ws.slice(i0, i1 + 1);

  const kaarten = blok.map((w) => {
    if (!w.lesweek) {
      return `<div class="vakantie"><span>${esc(w.naam)}</span><span>week ${w.kw} · ${bereik(w)}</span></div>`;
    }
    const info = data.weken.find((x) => x.week === w.lesweek);
    const isNu = w.lesweek === h.lesweek;
    const groot = isNu ? "groot" : "";
    const lab = isNu ? `<span class="label">${h.bezig ? "DEZE WEEK" : "VOLGENDE WEEK"}</span>` : "";
    const vrij = (w.vrije_dagen || []).map((v) => `${esc(v.naam)} (${DAG_KORT[datum(v.datum).getDay() - 1] || ""} ${kortDatum(v.datum)})`).join(", ");
    const map = bestand(g, w.lesweek);
    if (!info) {
      return `<article class="week"><div><h2>${lab}Week ${w.kw}</h2><div class="datum">${bereik(w)}</div>
        <p class="thema">Dit blad is nog niet klaar.</p></div></article>`;
    }
    return `<article class="week ${isNu ? "nu" : ""} ${groot}">
      <div>
        <h2>${lab}Week ${w.kw} <span class="datum">· ${bereik(w)}</span></h2>
        <p class="thema">${esc(info.thema)}</p>
        <div class="focus">${info.focus.map((f) => `<span>${f}</span>`).join("")}</div>
        ${vrij ? `<div class="vrij">Vrij: ${vrij}. Er blijft een strookje over (extra herhaling).</div>` : ""}
      </div>
      <div class="acties">
        <a class="knop primair" href="${map}.pdf" target="_blank" rel="noopener">Werkblad (PDF)</a>
        <a class="knop" href="${map}-antwoorden.pdf" target="_blank" rel="noopener">Antwoorden (PDF)</a>
        <a class="knop groen" href="#/bord/${g}/${w.kw}/${standaardDag(w.lesweek)}">Nakijken op het digibord</a>
      </div>
    </article>`;
  });

  const opties = lesweken().map((w) => `<option value="${w.lesweek}" ${w.lesweek === start ? "selected" : ""}>Week ${w.kw} · ${bereik(w)}</option>`).join("");
  app.innerHTML = `
    <div class="kop-groep">
      <div><h1>Groep ${g}</h1><div class="sub">${h.bezig ? "Deze week" : "Volgende week"}: week ${h.week.kw} (${bereik(h.week)})</div></div>
    </div>
    ${vak && !vanaf ? `<p class="melding">Het is nu ${vak === "zomer" ? "zomervakantie" : esc(vak.toLowerCase())}. Bovenaan staat de eerste week na de vakantie.</p>` : ""}
    <div class="bladeren">
      <button class="knop" id="eerder" ${start <= 1 ? "disabled" : ""}>← Eerdere weken</button>
      <button class="knop" id="nu" ${start === h.lesweek ? "disabled" : ""}>Deze week</button>
      <button class="knop" id="later" ${eind >= 40 ? "disabled" : ""}>Latere weken →</button>
      <select class="knop" id="kies" aria-label="Ga naar week">${opties}</select>
    </div>
    <section class="weken">${kaarten.join("")}</section>
    <section class="jaar">
      <h3>Heel schooljaar</h3>
      <div class="acties">
        <a class="knop" href="groep${g}/groep${g}-heel-jaar.pdf" target="_blank" rel="noopener">Alle 40 werkbladen (PDF)</a>
        <a class="knop" href="groep${g}/groep${g}-antwoorden-heel-jaar.pdf" target="_blank" rel="noopener">Alle antwoorden (PDF)</a>
        <a class="knop" href="groep${g}/groep${g}-jaaroverzicht.pdf" target="_blank" rel="noopener">Jaaroverzicht: opbouw per week</a>
      </div>
    </section>`;

  const naar = (n) => { location.hash = n === h.lesweek ? `#/groep/${g}` : `#/groep/${g}/week/${kwVan(n)}`; };
  document.getElementById("eerder").onclick = () => naar(Math.max(1, start - VENSTER));
  document.getElementById("later").onclick = () => naar(Math.min(40, start + VENSTER));
  document.getElementById("nu").onclick = () => naar(h.lesweek);
  document.getElementById("kies").onchange = (e) => naar(Number(e.target.value));
}

// ---------- digibord ----------
let bordToetsen = null;

async function toonBord(g, n, dag) {
  document.body.classList.add("bordmodus");
  zetNav(g);
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
      title="${vrijeDatums.has(dIso) ? "vrije dag" : ""}">${naam[0].toUpperCase() + naam.slice(1, 2)}<small>${kortDatum(dIso)}</small></button>`;
  }).join("");

  // gele vakjes over de antwoorden; bij omcirkel- en tekenopdrachten dekt het vakje de hele opdracht af
  let volgorde = [];
  const dekkingen = dd.vakjes.map((rects, i) => rects.map(([x, y, bw, bh], j) => {
    const isCel = dd.vakjes[i].length === 1 && bw > 0.12;
    const p = isCel ? 0 : 0.004; // klein randje extra
    volgorde.push(`${i}-${j}`);
    return `<button class="dekking ${isCel ? "cel" : ""}" data-i="${i}" aria-label="Antwoord ${i + 1} tonen"
      style="left:${(x - p) * 100}%;top:${(y - p * 3.55) * 100}%;width:${(bw + 2 * p) * 100}%;height:${(bh + 2 * p * 3.55) * 100}%">${j === 0 ? i + 1 : ""}</button>`;
  }).join("")).join("");

  app.innerHTML = `
    <div class="bordkop">
      <div>
        <h1>Groep ${g} · Week ${w.kw} · ${DAGEN[dag - 1]} ${kortDatum(datumDag)}</h1>
        <div class="sub">${esc(meta.thema)}</div>
      </div>
      <div class="dagen" role="tablist">${tabs}</div>
    </div>
    <div class="strook" id="strook">
      <img src="${bestand(g, n)}-dag${dag}.png" alt="Strook met antwoorden, ${DAGEN[dag - 1]} week ${w.kw}">
      ${dekkingen}
    </div>
    <div class="bordknoppen">
      <button class="knop groen" id="volgende">Volgend antwoord ▶</button>
      <button class="knop" id="alles">Alles tonen</button>
      <button class="knop" id="verberg">Alles verbergen</button>
      <button class="knop" id="vorigeDag">← Vorige dag</button>
      <button class="knop" id="volgendeDag">Volgende dag →</button>
      <button class="knop" id="scherm">Volledig scherm</button>
      <a class="knop" href="#/groep/${g}/week/${w.kw}">Terug</a>
    </div>
    <p class="tip">Tik op een geel vakje om het antwoord te zien. Toetsen: spatie = volgend antwoord, A = alles tonen, V = alles verbergen, ←/→ = vorige/volgende dag.</p>
    <details class="tekstantw"><summary>Antwoorden als tekst</summary><ol>${dd.antwoorden.map((a) => `<li>${esc(a)}</li>`).join("")}</ol></details>`;

  const dek = [...app.querySelectorAll(".dekking")];
  dek.forEach((b) => { b.onclick = () => { const i = b.dataset.i; dek.filter((x) => x.dataset.i === i).forEach((x) => x.classList.toggle("open")); }; });
  const volgende = () => {
    const dicht = dek.find((x) => !x.classList.contains("open"));
    if (dicht) dek.filter((x) => x.dataset.i === dicht.dataset.i).forEach((x) => x.classList.add("open"));
  };
  const alles = (open) => dek.forEach((x) => x.classList.toggle("open", open));
  const gaNaarDag = (stap) => {
    let nn = n, d2 = dag + stap;
    if (d2 < 1) { if (nn > 1) { nn--; d2 = 5; } else d2 = 1; }
    if (d2 > 5) { if (nn < 40) { nn++; d2 = 1; } else d2 = 5; }
    location.hash = `#/bord/${g}/${kwVan(nn)}/${d2}`;
  };
  app.querySelectorAll(".dagen button").forEach((b) => { b.onclick = () => { location.hash = `#/bord/${g}/${w.kw}/${b.dataset.dag}`; }; });
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
    app.innerHTML = `<p class="melding">Er ging iets mis bij het laden. Probeer de pagina te verversen.</p>`;
  }
  window.scrollTo(0, 0);
}
window.addEventListener("hashchange", route);
route();
