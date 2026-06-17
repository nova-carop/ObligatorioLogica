"""
Sistema de Criptografia — ObligatorioLogica
Corre con: python main.py  (no requiere pip ni dependencias externas)
"""
import sys, os, re, json, subprocess, threading, webbrowser
from http.server import HTTPServer, BaseHTTPRequestHandler

# ── Rutas Prolog ───────────────────────────────────────────────────
BASE_DIR   = os.path.dirname(os.path.abspath(__file__))
LOGICA_DIR = os.path.join(BASE_DIR, "capa logica")
ALFA       = os.path.join(LOGICA_DIR, "alfabeto.pl")
CESAR      = os.path.join(LOGICA_DIR, "cifrado_cesar.pl")
PLAYFAIR   = os.path.join(LOGICA_DIR, "cifrado_playfare.pl")
VIGENERE   = os.path.join(LOGICA_DIR, "cifrado_vigenere.pl")

# ── Prolog ─────────────────────────────────────────────────────────
def esc(s):
    # Escapar comillas simples y backslashes para atoms de Prolog
    return s.replace("\\", "\\\\").replace("'", "''")

def run_prolog(files, goal):
    cmd = ["swipl", "-q"]
    for f in files: cmd += ["-l", f]
    cmd += ["-g", goal, "-g", "halt"]
    try:
        r = subprocess.run(cmd, capture_output=True, text=True, timeout=15)
        out = r.stdout.strip()
        return (out, None) if out else (None, r.stderr.strip() or "Sin resultado")
    except FileNotFoundError:
        return None, "SWI-Prolog no encontrado en el PATH."
    except subprocess.TimeoutExpired:
        return None, "Timeout — Prolog tardó demasiado."

def make_goal(alg, op, texto, key, idioma):
    t = esc(texto.lower())
    if alg == "cesar":
        p = "cifrar_lista" if op == "cifrar" else "descifrar_lista"
        g = f"atom_chars('{t}',L),{p}(L,{int(key)},{idioma},R),atomic_list_concat(R,Res),write(Res)"
        return [ALFA, CESAR], g
    if alg == "vigenere":
        k = esc(key.lower())
        p = "cifrar" if op == "cifrar" else "descifrar"
        return [ALFA, VIGENERE], f"{p}('{t}','{k}',{idioma},R),write(R)"
    if alg == "playfair":
        k = esc(key)
        p = "cifrar" if op == "cifrar" else "descifrar"
        return [ALFA, PLAYFAIR], f"{p}('{k}','{t}',R),write(R)"

# ── HTML embebido ──────────────────────────────────────────────────
HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>Cifrado Clásico — Obligatorio Lógica</title>
<link href="https://fonts.googleapis.com/css2?family=Space+Grotesk:wght@400;500;600;700;800&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0;-webkit-font-smoothing:antialiased}
:root{
  --bg:#0e0820; --surf:#1e1238; --surf2:#271848; --surf3:#321e58;
  --pink:#f72585; --cyan:#4cc9f0; --yellow:#f8c927;
  --purple:#b14aed; --green:#06d6a0; --red:#ff6b6b;
  --t1:#f2eeff; --t2:#c4a8e0; --t3:#9a7ec8; --t4:#6a4f96;
  --b:rgba(255,255,255,.09);
  --cc:#f72585; --cc-glow:rgba(247,37,133,.35); --cc-dim:rgba(247,37,133,.12);
  --gr:247,37,133;
}
html,body{height:100%;overflow:hidden}
body{
  background:var(--bg);font-family:'Space Grotesk',sans-serif;
  font-size:13px;color:var(--t1);display:flex;flex-direction:column;
}
body::before{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background-image:
    linear-gradient(rgba(var(--gr),.055) 1px,transparent 1px),
    linear-gradient(90deg,rgba(var(--gr),.055) 1px,transparent 1px);
  background-size:48px 48px;
  animation:gridMove 28s linear infinite;
}
body::after{
  content:'';position:fixed;inset:0;pointer-events:none;z-index:0;
  background:
    radial-gradient(ellipse 130% 70% at 50% -20%,rgba(177,74,237,.18) 0%,transparent 65%),
    radial-gradient(ellipse 50% 50% at 95% 95%,rgba(76,201,240,.09) 0%,transparent 60%);
}
@keyframes gridMove{0%{background-position:0 0,0 0}100%{background-position:48px 48px,48px 48px}}
::-webkit-scrollbar{width:4px}
::-webkit-scrollbar-thumb{background:rgba(var(--gr),.4);border-radius:4px}

/* ── HEADER ── */
header{
  position:relative;z-index:10;flex-shrink:0;
  padding:11px 20px 9px;
  border-bottom:1px solid rgba(var(--gr),.15);
  background:rgba(14,8,32,.85);backdrop-filter:blur(24px);
  display:flex;flex-direction:column;gap:9px;
}
.hrow{display:flex;align-items:center;gap:10px}
.hlogo{
  font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:800;
  background:linear-gradient(100deg,var(--pink) 0%,var(--cyan) 55%,var(--purple) 100%);
  -webkit-background-clip:text;-webkit-text-fill-color:transparent;background-clip:text;
  filter:drop-shadow(0 0 10px rgba(247,37,133,.5));letter-spacing:-.5px;
}
.hpill{
  padding:2px 9px;border-radius:99px;font-size:10px;font-weight:600;
  font-family:'JetBrains Mono',monospace;letter-spacing:.4px;
}
.hpill-c{background:rgba(76,201,240,.1);color:var(--cyan);border:1px solid rgba(76,201,240,.22)}
.hpill-p{background:rgba(177,74,237,.1);color:var(--purple);border:1px solid rgba(177,74,237,.18);margin-left:auto}

/* ── NAV TABS ── */
.htabs{display:flex;align-items:center;gap:5px}
.ctab{
  display:flex;align-items:center;gap:6px;padding:5px 14px;
  border-radius:8px;border:1px solid rgba(255,255,255,.07);
  cursor:pointer;font-size:12px;font-weight:700;
  font-family:'JetBrains Mono',monospace;color:var(--t4);
  transition:all .18s;letter-spacing:.2px;user-select:none;
}
.ctab:hover{background:rgba(255,255,255,.05);color:var(--t3)}
.ctab.active[data-c="cesar"]{background:rgba(247,37,133,.13);border-color:rgba(247,37,133,.55);color:var(--pink);box-shadow:0 0 16px rgba(247,37,133,.2)}
.ctab.active[data-c="vigenere"]{background:rgba(76,201,240,.13);border-color:rgba(76,201,240,.55);color:var(--cyan);box-shadow:0 0 16px rgba(76,201,240,.2)}
.ctab.active[data-c="playfair"]{background:rgba(248,201,39,.13);border-color:rgba(248,201,39,.55);color:var(--yellow);box-shadow:0 0 16px rgba(248,201,39,.2)}
.ctab.active[data-c="cmp"]{background:rgba(177,74,237,.13);border-color:rgba(177,74,237,.55);color:var(--purple);box-shadow:0 0 16px rgba(177,74,237,.2)}
.ctab.active[data-c="hist"]{background:rgba(6,214,160,.1);border-color:rgba(6,214,160,.45);color:var(--green);box-shadow:0 0 16px rgba(6,214,160,.18)}
.cdot{width:6px;height:6px;border-radius:50%;flex-shrink:0}
[data-c="cesar"] .cdot{background:var(--pink)}
[data-c="vigenere"] .cdot{background:var(--cyan)}
[data-c="playfair"] .cdot{background:var(--yellow)}
[data-c="cmp"] .cdot{background:var(--purple)}
[data-c="hist"] .cdot{background:var(--green)}
.ctab.active .cdot{box-shadow:0 0 6px currentColor}
.tab-divider{width:1px;height:18px;background:rgba(255,255,255,.1);margin:0 4px}
.hist-badge{
  display:none;min-width:16px;height:16px;border-radius:99px;
  background:var(--green);color:#0e0820;font-size:9px;font-weight:800;
  align-items:center;justify-content:center;padding:0 4px;
  font-family:'JetBrains Mono',monospace;
}
.hist-badge.show{display:flex}

/* ── LAYOUT ── */
.layout{flex:1;overflow:hidden;display:flex;flex-direction:column;position:relative;z-index:1}
main{flex:1;overflow-y:auto;padding:16px 20px 14px;display:flex;flex-direction:column;gap:13px}
.page{display:none;flex-direction:column;gap:12px}
.page.active{display:flex}
.two-col{display:grid;grid-template-columns:1fr 1fr;gap:13px;align-items:start}
.row2{display:grid;grid-template-columns:1fr 1fr;gap:9px}
.row3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:9px}

/* ── CARDS ── */
.card{
  background:var(--surf);border:1px solid var(--b);
  border-radius:13px;overflow:hidden;position:relative;
  transition:border-color .18s;
}
.card::before{
  content:'';position:absolute;left:0;top:16%;bottom:16%;
  width:3px;border-radius:0 3px 3px 0;
  background:var(--cc);box-shadow:0 0 10px var(--cc);opacity:.8;
}
.card-hd{
  padding:12px 14px 0 19px;display:flex;align-items:center;gap:7px;
  font-size:9px;font-weight:800;color:var(--t3);
  text-transform:uppercase;letter-spacing:1.4px;
  font-family:'JetBrains Mono',monospace;
}
.card-ico{font-size:13px;color:var(--cc);filter:drop-shadow(0 0 5px var(--cc))}
.card-body{padding:11px 14px 14px 19px}

/* ── FIELDS ── */
.field{margin-bottom:10px}.field:last-child{margin-bottom:0}
label{
  display:block;font-size:9px;font-weight:700;color:var(--t3);
  margin-bottom:4px;letter-spacing:.6px;text-transform:uppercase;
  font-family:'JetBrains Mono',monospace;
}
select,input,textarea{
  width:100%;background:rgba(255,255,255,.07);color:var(--t1);
  border:1px solid rgba(255,255,255,.13);border-radius:8px;
  padding:7px 11px;font-size:13px;font-family:'Space Grotesk',sans-serif;
  outline:none;transition:border-color .15s,box-shadow .15s;
  -webkit-appearance:none;appearance:none;
}
select{
  cursor:pointer;padding-right:26px;
  background-image:url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='9' height='5' viewBox='0 0 9 5'%3E%3Cpath d='M0 0l4.5 5L9 0z' fill='%239a7ec8'/%3E%3C/svg%3E");
  background-repeat:no-repeat;background-position:right 9px center;
}
select option{background:var(--surf2)}
input:focus,textarea:focus,select:focus{
  border-color:var(--cc);
  box-shadow:0 0 0 3px var(--cc-dim),0 0 14px var(--cc-glow);
}
textarea{resize:vertical;min-height:82px;line-height:1.65}
.note{font-size:10px;color:var(--t3);margin-top:3px;font-family:'JetBrains Mono',monospace}
.err-box{
  display:none;align-items:center;gap:7px;margin-top:9px;
  padding:8px 12px;border-radius:8px;
  background:rgba(255,107,107,.07);border:1px solid rgba(255,107,107,.2);
  font-size:11.5px;color:var(--red);font-family:'JetBrains Mono',monospace;
}
.err-box.show{display:flex}

/* ── BUTTONS ── */
.btns{display:flex;gap:7px;margin-top:12px}
.btn{
  padding:8px 18px;border-radius:8px;font-size:13px;font-weight:700;
  cursor:pointer;border:1px solid transparent;transition:all .18s;
  font-family:'Space Grotesk',sans-serif;display:inline-flex;align-items:center;gap:7px;
}
.btn-primary{
  background:linear-gradient(135deg,var(--cc),color-mix(in srgb,var(--cc) 65%,white));
  color:#fff;
  box-shadow:0 2px 16px var(--cc-glow),inset 0 1px 0 rgba(255,255,255,.2);
  text-shadow:0 1px 3px rgba(0,0,0,.4);
}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 5px 24px var(--cc-glow);filter:brightness(1.1)}
.btn-primary:active{transform:none;filter:brightness(.94)}
.btn-primary:disabled{opacity:.5;cursor:not-allowed;transform:none;filter:none}
.btn-ghost{background:transparent;color:var(--t3);border-color:rgba(255,255,255,.09)}
.btn-ghost:hover{background:rgba(255,255,255,.05);color:var(--t2);border-color:rgba(255,255,255,.14)}
.btn-xs{
  padding:3px 9px;border-radius:6px;font-size:11px;font-weight:600;
  cursor:pointer;border:1px solid rgba(255,255,255,.1);
  background:rgba(255,255,255,.05);color:var(--t3);
  transition:all .14s;font-family:'JetBrains Mono',monospace;
}
.btn-xs:hover{color:var(--t1);border-color:rgba(255,255,255,.18);background:rgba(255,255,255,.08)}
.btn-xs.ok{color:var(--green);border-color:rgba(6,214,160,.3);background:rgba(6,214,160,.08)}

/* ── RESULT ── */
.result-block{
  background:linear-gradient(135deg,rgba(14,8,32,.95),var(--surf));
  border:1px solid var(--cc);border-radius:12px;
  padding:14px 16px;margin-top:12px;display:none;
  animation:fadeUp .25s cubic-bezier(.22,1,.36,1);
  box-shadow:0 0 30px var(--cc-glow),inset 0 0 20px rgba(0,0,0,.2);
  position:relative;overflow:hidden;
}
.result-block::after{content:'';position:absolute;inset:0;background:linear-gradient(135deg,var(--cc-dim),transparent 55%);pointer-events:none}
.result-block.show{display:block}
.result-lbl{font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.8px;color:var(--cc);margin-bottom:7px;font-family:'JetBrains Mono',monospace;text-shadow:0 0 8px var(--cc)}
.result-row{display:flex;align-items:flex-start;gap:9px;position:relative;z-index:1}
.result-val{font-family:'JetBrains Mono',monospace;font-size:18px;font-weight:700;color:var(--t1);word-break:break-all;flex:1;line-height:1.5;text-shadow:0 0 20px rgba(255,255,255,.2)}
@keyframes fadeUp{from{opacity:0;transform:translateY(8px)}to{opacity:1;transform:none}}

/* ── CESAR VIZ ── */
.alph-row{display:flex;flex-wrap:wrap;gap:3px}
.alph-cell{
  width:24px;height:24px;border-radius:5px;
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.11);
  display:flex;align-items:center;justify-content:center;
  font-family:'JetBrains Mono',monospace;font-size:10px;font-weight:700;
  color:var(--t3);transition:all .15s;
}
.alph-cell.hi{background:var(--cc-dim);border-color:var(--cc);color:var(--cc);box-shadow:0 0 7px var(--cc-glow)}
.shift-box{display:flex;align-items:center;gap:11px;margin:9px 0;padding:9px 14px;border-radius:9px;background:var(--cc-dim);border:1px solid rgba(var(--gr),.25)}
.shift-num{font-family:'JetBrains Mono',monospace;font-size:30px;font-weight:800;color:var(--cc);text-shadow:0 0 18px var(--cc);min-width:48px;text-align:center;line-height:1}
.shift-txt{font-size:11px;color:var(--t3);line-height:1.6}
.alph-lbl{font-size:9px;font-weight:700;color:var(--t3);text-transform:uppercase;letter-spacing:.8px;margin-bottom:3px;font-family:'JetBrains Mono',monospace}
.arrow-row{font-size:10px;color:var(--t4);letter-spacing:4px;margin:2px 0}

/* ── VIGENERE VIZ ── */
.vig-scroll{overflow-x:auto;margin-top:7px}
.vig-tbl{border-collapse:separate;border-spacing:3px;font-size:11px}
.vig-tbl td{border-radius:5px;padding:4px;text-align:center;font-family:'JetBrains Mono',monospace;font-weight:700}
.vtd-lbl{color:var(--t3)!important;font-weight:500!important;font-family:'Space Grotesk',sans-serif!important;text-align:left!important;padding-right:9px!important;font-size:10px!important;white-space:nowrap;text-transform:uppercase;letter-spacing:.4px}
.vtd-t{background:rgba(255,255,255,.09);border:1px solid rgba(255,255,255,.14);color:var(--t1)}
.vtd-k{background:rgba(76,201,240,.12);border:1px solid rgba(76,201,240,.28);color:var(--cyan)}

/* ── PLAYFAIR VIZ ── */
.matrix{display:grid;grid-template-columns:repeat(5,1fr);gap:5px}
.cell{
  aspect-ratio:1;border-radius:8px;
  background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.13);
  display:flex;align-items:center;justify-content:center;
  font-family:'JetBrains Mono',monospace;font-size:15px;font-weight:700;
  color:var(--t2);transition:all .22s;
}
.cell.hi{background:var(--cc-dim);border-color:var(--cc);color:var(--cc);box-shadow:0 0 12px var(--cc-glow);transform:scale(1.05)}
.viz-desc{font-size:12px;color:var(--t3);line-height:1.65;margin-bottom:11px}

/* ── COMPARACION ── */
.cmp-grid{display:grid;grid-template-columns:repeat(3,1fr);gap:10px;margin-top:4px}
.cmp-card{background:var(--surf);border:1px solid var(--b);border-radius:12px;overflow:hidden}
.cmp-hd{padding:11px 13px 0;font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.2px;font-family:'JetBrains Mono',monospace;display:flex;align-items:center;gap:6px}
.cmp-body{padding:9px 13px 13px}
.cmp-out{
  font-family:'JetBrains Mono',monospace;font-size:12px;word-break:break-all;
  min-height:46px;line-height:1.6;
  background:rgba(255,255,255,.07);border:1px solid rgba(255,255,255,.11);
  border-radius:7px;padding:8px 10px;color:var(--t1);
}
.cmp-out.err{color:var(--red)}
.cmp-out.muted{color:var(--t3);font-family:'Space Grotesk',sans-serif;font-size:11px}

/* ── HISTORIAL ── */
.hist-item{
  background:var(--surf);border:1px solid var(--b);border-radius:11px;
  padding:11px 14px;animation:fadeUp .15s ease;
}
.hist-hd{display:flex;align-items:center;gap:7px;margin-bottom:5px;font-size:10px;font-weight:700;font-family:'JetBrains Mono',monospace}
.hist-alg-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0}
.hist-time{color:var(--t4);font-weight:400;margin-left:auto}
.hist-body{font-family:'JetBrains Mono',monospace;font-size:12px;color:var(--t2);display:flex;align-items:center;gap:8px;flex-wrap:wrap}
.hist-res{font-weight:700}
.hist-sep{color:var(--t4);font-size:16px}
#hist-empty{text-align:center;padding:44px;color:var(--t3);font-size:13px;display:flex;flex-direction:column;align-items:center;gap:10px}

/* ── TICKER ── */
#ticker-bar{
  flex-shrink:0;height:28px;
  border-top:1px solid rgba(var(--gr),.1);
  background:rgba(14,8,32,.9);backdrop-filter:blur(12px);
  display:flex;align-items:center;overflow:hidden;position:relative;z-index:10;
}
.ticker-label{
  flex-shrink:0;padding:0 11px;height:100%;display:flex;align-items:center;
  font-size:9px;font-weight:800;text-transform:uppercase;letter-spacing:1.8px;
  color:var(--pink);font-family:'JetBrains Mono',monospace;
  border-right:1px solid rgba(247,37,133,.12);background:rgba(247,37,133,.05);
  text-shadow:0 0 7px var(--pink);
}
.ticker-track{flex:1;overflow:hidden;height:100%;position:relative}
.ticker-inner{
  display:flex;align-items:center;height:100%;gap:24px;
  padding:0 14px;white-space:nowrap;
  animation:tickerScroll 35s linear infinite;
}
.ticker-inner:hover{animation-play-state:paused}
.ticker-item{display:inline-flex;align-items:center;gap:7px;font-family:'JetBrains Mono',monospace;font-size:11px}
.tick-arr{color:rgba(255,255,255,.2)}
.tick-sep{color:rgba(247,37,133,.2);font-size:14px}
.ticker-empty{font-size:10px;color:var(--t4);font-family:'JetBrains Mono',monospace;padding:0 14px}
@keyframes tickerScroll{0%{transform:translateX(0)}100%{transform:translateX(-50%)}}

/* ── MISC ── */
.hidden{display:none!important}
.page-hd{margin-bottom:2px}
.page-hd h2{font-size:17px;font-weight:800;letter-spacing:-.4px;margin-bottom:2px}
.page-hd p{font-size:12px;color:var(--t3)}
</style>
</head>
<body>

<header>
  <div class="hrow">
    <span class="hlogo">Cifrado Clásico</span>
    <span class="hpill hpill-c">SWI-Prolog</span>
    <span class="hpill hpill-p">Obligatorio Lógica</span>
  </div>
  <div class="htabs">
    <div class="ctab active" data-c="cesar" onclick="switchCipher(this,'cesar')">
      <span class="cdot"></span> César
    </div>
    <div class="ctab" data-c="vigenere" onclick="switchCipher(this,'vigenere')">
      <span class="cdot"></span> Vigenère
    </div>
    <div class="ctab" data-c="playfair" onclick="switchCipher(this,'playfair')">
      <span class="cdot"></span> Playfair
    </div>
    <div class="tab-divider"></div>
    <div class="ctab" data-c="cmp" onclick="switchPage('cmp',this)" id="tab-cmp">
      <span class="cdot"></span> Comparar
    </div>
    <div class="ctab" data-c="hist" onclick="switchPage('hist',this)" id="tab-hist">
      <span class="cdot"></span> Historial
      <span class="hist-badge" id="hist-badge">0</span>
    </div>
  </div>
</header>

<div class="layout">
<main>

  <!-- ── CIFRADOR ── -->
  <div id="page-cipher" class="page active">
    <div class="two-col">

      <!-- Left: controls -->
      <div style="display:flex;flex-direction:column;gap:11px">
        <div class="card">
          <div class="card-hd">
            <span class="card-ico">⬡</span>
            <span id="alg-label">Cifrado César</span>
          </div>
          <div class="card-body">
            <div class="row2" style="margin-bottom:10px">
              <div class="field">
                <label>Operación</label>
                <select id="op"><option>cifrar</option><option>descifrar</option></select>
              </div>
              <div id="idioma-f" class="field">
                <label>Idioma</label>
                <select id="idioma">
                  <option value="espanol">Español</option>
                  <option value="ingles">Inglés</option>
                </select>
              </div>
            </div>
            <div class="field">
              <label id="key-lbl">Desplazamiento</label>
              <input id="key" type="text" placeholder="ej: 3"
                     oninput="onKeyInput(this)" autocomplete="off">
              <div id="key-note" class="note">Número entero (ej: 3, -5, 13)</div>
            </div>
            <div class="field">
              <label>Texto</label>
              <textarea id="texto" placeholder="Ingresa el texto a cifrar..."
                        oninput="onTextoInput()"></textarea>
            </div>
            <div class="btns">
              <button id="proc-btn" class="btn btn-primary" onclick="procesar()">
                &#9654; Procesar
              </button>
              <button class="btn btn-ghost" onclick="limpiar()">Limpiar</button>
            </div>
            <div id="err" class="err-box"><span>&#9888;</span><span id="err-txt"></span></div>
          </div>
        </div>

        <div id="result-block" class="result-block">
          <div class="result-lbl">&#9642; Resultado</div>
          <div class="result-row">
            <span id="result-val" class="result-val"></span>
            <button class="btn-xs" onclick="copyId('result-val',this)">Copiar</button>
          </div>
        </div>
      </div>

      <!-- Right: visualizations -->
      <div>
        <!-- CESAR -->
        <div id="viz-cesar" class="card">
          <div class="card-hd"><span class="card-ico">&#9711;</span> Desplazamiento del Alfabeto</div>
          <div class="card-body">
            <div class="viz-desc">Cada letra corre <em>n</em> posiciones. Con n=3: A→D, Z→C.</div>
            <div class="shift-box">
              <div class="shift-num" id="shift-val">0</div>
              <div class="shift-txt">posiciones de<br>desplazamiento</div>
            </div>
            <div class="alph-lbl" style="margin-top:6px">Original</div>
            <div id="alpha-orig" class="alph-row"></div>
            <div class="arrow-row">↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓↓</div>
            <div class="alph-lbl">Cifrado</div>
            <div id="alpha-enc" class="alph-row"></div>
          </div>
        </div>

        <!-- VIGENERE -->
        <div id="viz-vigenere" class="card hidden">
          <div class="card-hd"><span class="card-ico">&#9632;</span> Mapeo Clave → Texto</div>
          <div class="card-body">
            <div class="viz-desc">La clave se repite cíclicamente. Cada posición tiene su propio desplazamiento.</div>
            <div id="vig-empty" style="font-size:11.5px;color:var(--t3);font-family:'JetBrains Mono',monospace">
              Ingresa texto y clave para ver el mapeo →
            </div>
            <div id="vig-map" class="hidden">
              <div class="vig-scroll">
                <table class="vig-tbl"><tbody id="vig-tbody"></tbody></table>
              </div>
            </div>
          </div>
        </div>

        <!-- PLAYFAIR -->
        <div id="viz-playfair" class="card hidden">
          <div class="card-hd"><span class="card-ico">&#9635;</span> Matriz 5×5</div>
          <div class="card-body">
            <div class="viz-desc">La clave define el orden. I/J comparten celda. Cifrado por pares de letras.</div>
            <div id="matrix" class="matrix">
              <div style="grid-column:span 5;font-size:11px;color:var(--t3);
                          font-family:'JetBrains Mono',monospace;padding:20px 0;text-align:center">
                Ingresa una clave para ver la matriz →
              </div>
            </div>
            <div style="margin-top:8px;display:flex;align-items:center;justify-content:space-between">
              <div class="note">Resaltado = letras de la clave</div>
              <button class="btn-xs" onclick="updateMatrix()">&#8635; Actualizar</button>
            </div>
          </div>
        </div>
      </div>

    </div>
  </div>

  <!-- ── COMPARAR ── -->
  <div id="page-cmp" class="page">
    <div class="page-hd">
      <h2>Comparación</h2>
      <p>El mismo texto procesado con los 3 algoritmos.</p>
    </div>
    <div class="card" style="--cc:var(--purple);--cc-glow:rgba(177,74,237,.3);--cc-dim:rgba(177,74,237,.1)">
      <div class="card-hd"><span class="card-ico">&#9145;</span> Configuración</div>
      <div class="card-body">
        <div class="row2" style="margin-bottom:10px">
          <div class="field"><label>Operación</label>
            <select id="cmp-op"><option>cifrar</option><option>descifrar</option></select></div>
          <div class="field"><label>Idioma (César y Vigenère)</label>
            <select id="cmp-idioma">
              <option value="espanol">Español</option>
              <option value="ingles">Inglés</option>
            </select></div>
        </div>
        <div class="field"><label>Texto</label>
          <textarea id="cmp-texto" placeholder="Texto a comparar..."></textarea></div>
        <div class="row3" style="margin-bottom:12px">
          <div class="field"><label>Desp. César</label>
            <input id="cmp-key-cesar" value="3" oninput="filterNum(this)"></div>
          <div class="field"><label>Clave Vigenère</label>
            <input id="cmp-key-vigenere" placeholder="clave" oninput="filterLetters(this)"></div>
          <div class="field"><label>Clave Playfair</label>
            <input id="cmp-key-playfair" placeholder="clave" oninput="filterLetters(this)"></div>
        </div>
        <button class="btn btn-primary" onclick="comparar()"
          style="--cc:var(--purple);--cc-glow:rgba(177,74,237,.3);--cc-dim:rgba(177,74,237,.1)">
          &#9654; Comparar los 3 cifrados
        </button>
        <div id="cmp-err" class="err-box" style="margin-top:9px">
          <span>&#9888;</span><span id="cmp-err-txt"></span>
        </div>
      </div>
    </div>
    <div class="cmp-grid">
      <div class="cmp-card" style="border-color:rgba(247,37,133,.2)">
        <div class="cmp-hd" style="color:var(--pink)">
          <span style="width:6px;height:6px;border-radius:50%;background:var(--pink);box-shadow:0 0 6px var(--pink)"></span>
          César
        </div>
        <div class="cmp-body">
          <div id="cmp-res-cesar" class="cmp-out muted">Sin calcular</div>
          <button class="btn-xs" style="margin-top:7px" onclick="copyId('cmp-res-cesar',this)">Copiar</button>
        </div>
      </div>
      <div class="cmp-card" style="border-color:rgba(76,201,240,.2)">
        <div class="cmp-hd" style="color:var(--cyan)">
          <span style="width:6px;height:6px;border-radius:50%;background:var(--cyan);box-shadow:0 0 6px var(--cyan)"></span>
          Vigenère
        </div>
        <div class="cmp-body">
          <div id="cmp-res-vigenere" class="cmp-out muted">Sin calcular</div>
          <button class="btn-xs" style="margin-top:7px" onclick="copyId('cmp-res-vigenere',this)">Copiar</button>
        </div>
      </div>
      <div class="cmp-card" style="border-color:rgba(248,201,39,.2)">
        <div class="cmp-hd" style="color:var(--yellow)">
          <span style="width:6px;height:6px;border-radius:50%;background:var(--yellow);box-shadow:0 0 6px var(--yellow)"></span>
          Playfair
        </div>
        <div class="cmp-body">
          <div id="cmp-res-playfair" class="cmp-out muted">Sin calcular</div>
          <button class="btn-xs" style="margin-top:7px" onclick="copyId('cmp-res-playfair',this)">Copiar</button>
        </div>
      </div>
    </div>
  </div>

  <!-- ── HISTORIAL ── -->
  <div id="page-hist" class="page">
    <div class="page-hd" style="display:flex;align-items:flex-start;justify-content:space-between">
      <div>
        <h2>Historial</h2>
        <p>Operaciones realizadas en esta sesión.</p>
      </div>
      <button class="btn btn-ghost" style="margin-top:2px" onclick="clearHist()">Limpiar</button>
    </div>
    <div id="hist-list">
      <div id="hist-empty">
        <span style="font-size:26px">&#9783;</span>
        Sin operaciones todavía.
      </div>
    </div>
  </div>

</main>

<!-- TICKER -->
<div id="ticker-bar">
  <div class="ticker-label">⬡ LOG</div>
  <div class="ticker-track">
    <div class="ticker-empty" id="ticker-empty">Sin operaciones — procesá algo para ver el log en vivo</div>
    <div class="ticker-inner hidden" id="ticker-inner"></div>
  </div>
</div>
</div>

<script>
const ABC='ABCDEFGHIJKLMNOPQRSTUVWXYZ';
const CC={
  cesar:   {hex:'#f72585',glow:'rgba(247,37,133,.35)',dim:'rgba(247,37,133,.12)',rgb:'247,37,133',name:'César'},
  vigenere:{hex:'#4cc9f0',glow:'rgba(76,201,240,.35)', dim:'rgba(76,201,240,.12)', rgb:'76,201,240', name:'Vigenère'},
  playfair:{hex:'#f8c927',glow:'rgba(248,201,39,.35)', dim:'rgba(248,201,39,.12)', rgb:'248,201,39', name:'Playfair'},
};
const LABELS={
  cesar:   ['Desplazamiento','Número entero, puede ser negativo (ej: 3, -5, 13)'],
  vigenere:['Clave','Solo letras, se repite cíclicamente'],
  playfair:['Clave','Solo letras A-Z (I y J comparten posición)'],
};
let cur='cesar';
const LOG=[];

function setTheme(c){
  const r=document.documentElement;
  r.style.setProperty('--cc',CC[c].hex);
  r.style.setProperty('--cc-glow',CC[c].glow);
  r.style.setProperty('--cc-dim',CC[c].dim);
  r.style.setProperty('--gr',CC[c].rgb);
}

function switchCipher(el,c){
  document.querySelectorAll('.ctab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  cur=c; setTheme(c);
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.getElementById('page-cipher').classList.add('active');
  document.getElementById('alg-label').textContent='Cifrado '+CC[c].name;
  document.getElementById('key-lbl').textContent=LABELS[c][0];
  document.getElementById('key-note').textContent=LABELS[c][1];
  document.getElementById('key').placeholder=c==='cesar'?'ej: 3':'ej: clave';
  document.getElementById('key').value='';
  setErr('');
  document.getElementById('result-block').classList.remove('show');
  document.getElementById('idioma-f').classList.toggle('hidden',c==='playfair');
  ['cesar','vigenere','playfair'].forEach(a=>{
    document.getElementById('viz-'+a).classList.toggle('hidden',a!==c);
  });
  if(c==='cesar') updateCesarViz();
}

function switchPage(page,el){
  document.querySelectorAll('.ctab').forEach(t=>t.classList.remove('active'));
  el.classList.add('active');
  document.querySelectorAll('.page').forEach(p=>p.classList.remove('active'));
  document.getElementById('page-'+page).classList.add('active');
}

// Guards
function filterLetters(el){el.value=el.value.replace(/[^a-zA-Z]/g,'')}
function filterNum(el){el.value=el.value.replace(/[^0-9\-]/g,'')}
function onKeyInput(el){
  if(cur==='cesar'){filterNum(el);updateCesarViz();}
  else if(cur==='vigenere'){filterLetters(el);updateVigMap();}
  else filterLetters(el);
}
function onTextoInput(){if(cur==='vigenere') updateVigMap();}

function setErr(msg){
  const b=document.getElementById('err');
  document.getElementById('err-txt').textContent=msg;
  msg?b.classList.add('show'):b.classList.remove('show');
}

// Cesar viz
function updateCesarViz(){
  const s=parseInt(document.getElementById('key').value)||0;
  document.getElementById('shift-val').textContent=s;
  const orig=document.getElementById('alpha-orig');
  const enc=document.getElementById('alpha-enc');
  orig.innerHTML='';enc.innerHTML='';
  for(let i=0;i<26;i++){
    const c1=document.createElement('div');
    c1.className='alph-cell';c1.textContent=ABC[i];orig.appendChild(c1);
    const j=((i+s)%26+26)%26;
    const c2=document.createElement('div');
    c2.className='alph-cell'+(s!==0?' hi':'');
    c2.textContent=ABC[j];enc.appendChild(c2);
  }
}
updateCesarViz();

// Vigenere viz
function updateVigMap(){
  const txt=document.getElementById('texto').value.replace(/[^a-zA-Z]/g,'').toUpperCase().slice(0,24);
  const cla=document.getElementById('key').value.toUpperCase();
  const empty=document.getElementById('vig-empty');
  const map=document.getElementById('vig-map');
  if(!txt||!cla){empty.classList.remove('hidden');map.classList.add('hidden');return;}
  empty.classList.add('hidden');map.classList.remove('hidden');
  let k='';for(let i=0;i<txt.length;i++) k+=cla[i%cla.length];
  document.getElementById('vig-tbody').innerHTML=
    [['Texto',txt.split(''),'vtd-t'],['Clave',k.split(''),'vtd-k']].map(([l,cs,cls])=>
      `<tr><td class="vtd-lbl">${l}</td>${cs.map(c=>`<td class="${cls}">${c}</td>`).join('')}</tr>`
    ).join('');
}

// Playfair matrix
async function updateMatrix(){
  const key=document.getElementById('key').value.trim();
  if(!key)return;
  const res=await api('/matriz',{key});
  if(res.error||!res.letters)return;
  const mat=document.getElementById('matrix');
  const ks=new Set(key.toUpperCase().replace(/J/g,'I').split(''));
  mat.innerHTML=res.letters.map(l=>`<div class="cell${ks.has(l)?' hi':''}">${l}</div>`).join('');
}

// Process
async function procesar(){
  const op=document.getElementById('op').value;
  const idioma=document.getElementById('idioma').value;
  const key=document.getElementById('key').value.trim();
  const texto=document.getElementById('texto').value.trim();
  setErr('');
  if(!texto){setErr('El texto no puede estar vacío.');return;}
  if(!key){setErr('Ingresa la clave / desplazamiento.');return;}
  if(cur==='cesar'&&isNaN(parseInt(key))){setErr('El desplazamiento debe ser un número entero.');return;}
  const btn=document.getElementById('proc-btn');
  btn.disabled=true;btn.innerHTML='&#9680; Procesando...';
  const res=await api('/procesar',{alg:cur,op,idioma,key,texto});
  btn.disabled=false;btn.innerHTML='&#9654; Procesar';
  if(res.error){
    setErr(res.error);
    document.getElementById('result-block').classList.remove('show');
  }else{
    document.getElementById('result-val').textContent=res.result;
    document.getElementById('result-block').classList.add('show');
    addLog(cur,op,texto,res.result);
    if(cur==='playfair') updateMatrix();
    if(cur==='vigenere') updateVigMap();
  }
}

// Compare
async function comparar(){
  const texto=document.getElementById('cmp-texto').value.trim();
  const op=document.getElementById('cmp-op').value;
  const idioma=document.getElementById('cmp-idioma').value;
  const cmpErr=document.getElementById('cmp-err');
  document.getElementById('cmp-err-txt').textContent='';
  cmpErr.classList.remove('show');
  if(!texto){document.getElementById('cmp-err-txt').textContent='El texto no puede estar vacío.';cmpErr.classList.add('show');return;}
  const keys={
    cesar:document.getElementById('cmp-key-cesar').value.trim()||'3',
    vigenere:document.getElementById('cmp-key-vigenere').value.trim(),
    playfair:document.getElementById('cmp-key-playfair').value.trim(),
  };
  ['cesar','vigenere','playfair'].forEach(a=>{
    const el=document.getElementById('cmp-res-'+a);
    el.textContent='calculando...';el.className='cmp-out muted';
  });
  const res=await api('/comparar',{texto,op,idioma,keys});
  for(const a of['cesar','vigenere','playfair']){
    const el=document.getElementById('cmp-res-'+a);
    if(res[a].error){el.textContent=res[a].error;el.className='cmp-out err';}
    else{el.textContent=res[a].result;el.className='cmp-out';}
  }
}

// Limpiar
function limpiar(){
  document.getElementById('texto').value='';
  document.getElementById('key').value='';
  setErr('');
  document.getElementById('result-block').classList.remove('show');
  document.getElementById('matrix').innerHTML=`<div style="grid-column:span 5;font-size:11px;color:var(--t3);font-family:'JetBrains Mono',monospace;padding:20px 0;text-align:center">Ingresa una clave para ver la matriz →</div>`;
  document.getElementById('vig-empty').classList.remove('hidden');
  document.getElementById('vig-map').classList.add('hidden');
  updateCesarViz();
}

// Copy
function copyId(id,btn){
  const t=document.getElementById(id).textContent;
  if(!t||t==='Sin calcular'||t==='calculando...')return;
  navigator.clipboard.writeText(t).catch(()=>{});
  btn.textContent='✓ Copiado';btn.classList.add('ok');
  setTimeout(()=>{btn.textContent='Copiar';btn.classList.remove('ok');},1400);
}

// Historial
function addLog(alg,op,texto,res){
  LOG.unshift({alg,op,texto,res,t:new Date().toLocaleTimeString()});
  renderHist();
  renderTicker();
  const badge=document.getElementById('hist-badge');
  badge.textContent=LOG.length;
  badge.classList.add('show');
}
function renderHist(){
  const list=document.getElementById('hist-list');
  document.getElementById('hist-empty').style.display=LOG.length?'none':'flex';
  list.querySelectorAll('.hist-item').forEach(i=>i.remove());
  const sh=t=>t.length>36?t.slice(0,36)+'…':t;
  LOG.forEach(h=>{
    const col=CC[h.alg].hex;
    const d=document.createElement('div');
    d.className='hist-item';
    d.innerHTML=`
      <div class="hist-hd" style="color:${col}">
        <span class="hist-alg-dot" style="background:${col};box-shadow:0 0 5px ${col}"></span>
        ${CC[h.alg].name}&nbsp;·&nbsp;${h.op}
        <span class="hist-time">${h.t}</span>
      </div>
      <div class="hist-body">
        <span>"${sh(h.texto)}"</span>
        <span class="hist-sep">→</span>
        <span class="hist-res" style="color:${col}">${sh(h.res)}</span>
      </div>`;
    list.appendChild(d);
  });
}
function clearHist(){
  LOG.length=0;
  renderHist();
  renderTicker();
  const badge=document.getElementById('hist-badge');
  badge.classList.remove('show');
}

// Ticker
function renderTicker(){
  const empty=document.getElementById('ticker-empty');
  const inner=document.getElementById('ticker-inner');
  if(!LOG.length){empty.classList.remove('hidden');inner.classList.add('hidden');return;}
  empty.classList.add('hidden');inner.classList.remove('hidden');
  const sh=t=>t.length>20?t.slice(0,20)+'…':t;
  const items=LOG.map(l=>`
    <span class="ticker-item">
      <span style="color:${CC[l.alg].hex};text-shadow:0 0 7px ${CC[l.alg].hex};font-weight:700">${CC[l.alg].name}</span>
      <span class="tick-arr">›</span>
      <span style="color:rgba(255,255,255,.6)">"${sh(l.texto)}"</span>
      <span class="tick-arr">→</span>
      <span style="color:${CC[l.alg].hex};font-weight:600">${sh(l.res)}</span>
    </span><span class="tick-sep">◆</span>`).join('');
  inner.innerHTML=items+items;
}

// API
async function api(path,body){
  try{
    const r=await fetch(path,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
    return await r.json();
  }catch(e){return{error:'Error: '+e.message};}
}

setTheme('cesar');
</script>
</body>
</html>"""


# ── HTTP Handler ────────────────────────────────────────────────────
class Handler(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.end_headers()
        self.wfile.write(HTML.encode())

    def do_POST(self):
        length = int(self.headers.get("Content-Length", 0))
        data   = json.loads(self.rfile.read(length))
        path   = self.path

        if path == "/procesar":
            resp = self._procesar(data)
        elif path == "/comparar":
            resp = self._comparar(data)
        elif path == "/matriz":
            resp = self._matriz(data)
        else:
            resp = {"error": "ruta desconocida"}

        body = json.dumps(resp).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _validar(self, alg, key, texto):
        """Valida y normaliza inputs. Retorna (key, texto, error) o (k, t, None)."""
        import re as _re
        if not texto:
            return None, None, "El texto no puede estar vacio."
        if len(texto) > 2000:
            return None, None, "El texto es demasiado largo (max 2000 caracteres)."
        if not key:
            return None, None, "Ingresa la clave / desplazamiento."

        if alg == "cesar":
            try: int(key)
            except ValueError:
                return None, None, "El desplazamiento debe ser un numero entero."
            # Solo letras (y ñ) para el texto; ignorar el resto
            texto_clean = _re.sub(r"[^a-zA-ZñÑ ]", "", texto).strip()
            if not texto_clean:
                return None, None, "El texto no contiene letras validas."
            return key, texto_clean, None

        elif alg == "vigenere":
            if not _re.match(r"^[a-zA-Z]+$", key):
                return None, None, "La clave solo puede contener letras."
            texto_clean = _re.sub(r"[^a-zA-ZñÑ ]", "", texto).strip()
            if not texto_clean:
                return None, None, "El texto no contiene letras validas."
            return key, texto_clean, None

        elif alg == "playfair":
            if not _re.match(r"^[a-zA-Z]+$", key):
                return None, None, "La clave solo puede contener letras A-Z."
            texto_clean = _re.sub(r"[^a-zA-Z]", "", texto).upper()
            if not texto_clean:
                return None, None, "El texto no contiene letras validas para Playfair."
            if len(texto_clean) < 2:
                return None, None, "El texto debe tener al menos 2 letras para Playfair."
            return key, texto_clean, None

        return key, texto, None

    def _procesar(self, d):
        alg    = d.get("alg","")
        op     = d.get("op","cifrar")
        idioma = d.get("idioma","espanol")
        key    = d.get("key","").strip()
        texto  = d.get("texto","").strip()

        if alg not in ("cesar","vigenere","playfair"):
            return {"error": "Algoritmo desconocido."}
        if idioma not in ("espanol","ingles"):
            idioma = "espanol"

        key, texto, err = self._validar(alg, key, texto)
        if err:
            return {"error": err}
        try:
            files, g = make_goal(alg, op, texto, key, idioma)
            r, e = run_prolog(files, g)
            return {"error": e} if e else {"result": r}
        except Exception as ex:
            return {"error": str(ex)}

    def _comparar(self, d):
        texto  = d.get("texto","").strip()
        op     = d.get("op","cifrar")
        idioma = d.get("idioma","espanol")
        keys   = d.get("keys", {})
        resp   = {}
        for alg in ["cesar","vigenere","playfair"]:
            key = keys.get(alg,"").strip()
            k, t, err = self._validar(alg, key, texto)
            if err:
                resp[alg] = {"error": err}
                continue
            try:
                files, g = make_goal(alg, op, t, k, idioma)
                r, e = run_prolog(files, g)
                resp[alg] = {"error": e} if e else {"result": r}
            except Exception as ex:
                resp[alg] = {"error": str(ex)}
        return resp

    def _matriz(self, d):
        key = d.get("key","").strip()
        r, e = run_prolog([ALFA, PLAYFAIR],
                          f"construir_matriz('{esc(key)}',M),write(M)")
        if e: return {"error": e}
        letters = re.findall(r"[A-Z]", r)
        if len(letters) != 25:
            return {"error": f"Matriz invalida ({len(letters)} letras)"}
        return {"letters": letters}

    def log_message(self, *_):
        pass  # Silenciar logs del servidor

# ── Main ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    PORT = 5001
    url  = f"http://localhost:{PORT}"
    server = HTTPServer(("localhost", PORT), Handler)
    # Abrir browser después de 400ms para que el server esté listo
    threading.Timer(0.4, lambda: webbrowser.open(url)).start()
    print(f"Sistema de Criptografia corriendo en {url}")
    print("Cerrá esta terminal para detener el servidor.")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")