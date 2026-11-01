/* OmniDispatch —— 一页一棵树。数据全部来自本机 /api，界面只有树。 */
(() => {
'use strict';
const UI_ICONS={"panels-top-left": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-panels-top-left\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" />\n  <path d=\"M3 9h18\" />\n  <path d=\"M9 21V9\" />\n</svg>\n", "send": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-send\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M14.536 21.686a.5.5 0 0 0 .937-.024l6.5-19a.496.496 0 0 0-.635-.635l-19 6.5a.5.5 0 0 0-.024.937l7.93 3.18a2 2 0 0 1 1.112 1.11z\" />\n  <path d=\"m21.854 2.147-10.94 10.939\" />\n</svg>\n", "image": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-image\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <rect width=\"18\" height=\"18\" x=\"3\" y=\"3\" rx=\"2\" ry=\"2\" />\n  <circle cx=\"9\" cy=\"9\" r=\"2\" />\n  <path d=\"m21 15-3.086-3.086a2 2 0 0 0-2.828 0L6 21\" />\n</svg>\n", "users-round": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-users-round\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M18 21a8 8 0 0 0-16 0\" />\n  <circle cx=\"10\" cy=\"8\" r=\"5\" />\n  <path d=\"M22 20c0-3.37-2-6.5-4-8a5 5 0 0 0-.45-8.3\" />\n</svg>\n", "monitor": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-monitor\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <rect width=\"20\" height=\"14\" x=\"2\" y=\"3\" rx=\"2\" />\n  <line x1=\"8\" x2=\"16\" y1=\"21\" y2=\"21\" />\n  <line x1=\"12\" x2=\"12\" y1=\"17\" y2=\"21\" />\n</svg>\n", "refresh-cw": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-refresh-cw\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M3 12a9 9 0 0 1 9-9 9.75 9.75 0 0 1 6.74 2.74L21 8\" />\n  <path d=\"M21 3v5h-5\" />\n  <path d=\"M21 12a9 9 0 0 1-9 9 9.75 9.75 0 0 1-6.74-2.74L3 16\" />\n  <path d=\"M8 16H3v5\" />\n</svg>\n", "scroll-text": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-scroll-text\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M15 12h-5\" />\n  <path d=\"M15 8h-5\" />\n  <path d=\"M19 17V5a2 2 0 0 0-2-2H4\" />\n  <path d=\"M8 21h12a2 2 0 0 0 2-2v-1a1 1 0 0 0-1-1H11a1 1 0 0 0-1 1v1a2 2 0 1 1-4 0V5a2 2 0 1 0-4 0v2a1 1 0 0 0 1 1h3\" />\n</svg>\n", "settings-2": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-settings-2\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M20 7h-9\" />\n  <path d=\"M14 17H5\" />\n  <circle cx=\"17\" cy=\"17\" r=\"3\" />\n  <circle cx=\"7\" cy=\"7\" r=\"3\" />\n</svg>\n", "search": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-search\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <circle cx=\"11\" cy=\"11\" r=\"8\" />\n  <path d=\"m21 21-4.3-4.3\" />\n</svg>\n", "arrow-up-right": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-arrow-up-right\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M7 7h10v10\" />\n  <path d=\"M7 17 17 7\" />\n</svg>\n", "plus": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-plus\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M5 12h14\" />\n  <path d=\"M12 5v14\" />\n</svg>\n", "chevron-right": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-chevron-right\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"m9 18 6-6-6-6\" />\n</svg>\n", "command": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-command\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M15 6v12a3 3 0 1 0 3-3H6a3 3 0 1 0 3 3V6a3 3 0 1 0-3 3h12a3 3 0 1 0-3-3\" />\n</svg>\n", "sprout": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-sprout\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M7 20h10\" />\n  <path d=\"M10 20c5.5-2.5.8-6.4 3-10\" />\n  <path d=\"M9.5 9.4c1.1.8 1.8 2.2 2.3 3.7-2 .4-3.5.4-4.8-.3-1.2-.6-2.3-1.9-3-4.2 2.8-.5 4.4 0 5.5.8z\" />\n  <path d=\"M14.1 6a7 7 0 0 0-1.1 4c1.9-.1 3.3-.6 4.3-1.4 1-1 1.6-2.3 1.7-4.6-2.7.1-4 1-4.9 2z\" />\n</svg>\n", "shield-check": "<!-- @license lucide-static v0.468.0 - ISC -->\n<svg\n  class=\"lucide lucide-shield-check\"\n  xmlns=\"http://www.w3.org/2000/svg\"\n  width=\"20\"\n  height=\"20\"\n  viewBox=\"0 0 24 24\"\n  fill=\"none\"\n  stroke=\"currentColor\"\n  stroke-width=\"1.7\"\n  stroke-linecap=\"round\"\n  stroke-linejoin=\"round\"\n>\n  <path d=\"M20 13c0 5-3.5 7.5-7.66 8.95a1 1 0 0 1-.67-.01C7.5 20.5 4 18 4 13V6a1 1 0 0 1 1-1c2 0 4.5-1.2 6.24-2.72a1.17 1.17 0 0 1 1.52 0C14.51 3.81 17 5 19 5a1 1 0 0 1 1 1z\" />\n  <path d=\"m9 12 2 2 4-4\" />\n</svg>\n"};
const icon=name=>UI_ICONS[name]||'';
function mountIcons(host=document){host.querySelectorAll('[data-icon]').forEach(e=>{if(e.matches('a')){if(e.querySelector('.nav-icon'))return;const holder=document.createElement('span');holder.className='nav-icon';holder.innerHTML=icon(e.dataset.icon);holder.setAttribute('aria-hidden','true');e.prepend(holder);}else{e.innerHTML=icon(e.dataset.icon);e.setAttribute('aria-hidden','true');}});}
mountIcons();
let expandedNetwork=false;


const PLATFORMS = [
  ['xiaohongshu', '小红书'],
  ['bilibili',    'B 站'],
  ['tencent',     '视频号'],
  ['youtube',     'YouTube'],
  ['x',           'X']
];

const NAME = {
  sau:'social-auto-upload', xhsmcp:'xiaohongshu-mcp', biliup:'biliup',
  ytuploader:'youtubeuploader', spreado:'spreado', postiz:'postiz',
  mixpost:'mixpost', matrixmedia:'matrix-media', postbot:'postbot',
  resin:'resin', tweepy:'tweepy', patchright:'patchright',
  xapi:'x · 官方 API', xbrowser:'x · 浏览器', desktopweb:'本机桌面确认'
};

const $ = s => document.querySelector(s);
const el = (t, cls) => { const e = document.createElement(t); if (cls) e.className = cls; return e; };

let CSRF = '';
let viewRequests=new AbortController();
const DAY = 864e5;

function ago(dateStr, ms) {
  const t = ms || (dateStr ? Date.parse(dateStr) : 0);
  if (!t) return '';
  const n = Math.round((Date.now() - t) / DAY);
  if (n <= 0) return '今天';
  if (n === 1) return '昨天';
  if (n < 30) return n + ' 天前';
  if (n < 365) return Math.round(n / 30) + ' 个月前';
  return Math.round(n / 365) + ' 年前';
}

/* ── 取数 ─────────────────────────────────────────────────── */
async function api(path, method = 'GET', body) {
  const signal=method==='GET'?viewRequests.signal:undefined;
  const res = await fetch('/api' + path, {
    method,
    credentials: 'same-origin',
    signal,
    headers: { 'Content-Type': 'application/json', ...(method === 'GET' ? {} : { 'X-CSRF-Token': CSRF }) },
    body: body === undefined ? undefined : JSON.stringify(body)
  });
  const data = await res.json().catch(error => {if(error.name==='AbortError')throw error;return {};});
  if(signal?.aborted)throw new DOMException('View changed','AbortError');
  if (!res.ok) {
    const detail=Array.isArray(data.detail)?data.detail.map(x=>x.msg).join('；'):data.detail;
    const err = new Error(detail || ('HTTP ' + res.status));
    err.status = res.status;
    throw err;
  }
  return data;
}

async function bootstrap() {
  try {
    const r = await fetch('/api/bootstrap', { method: 'POST', credentials: 'same-origin' });
    if (!r.ok) return false;
    CSRF = (await r.json()).csrf || '';
    return true;
  } catch { return false; }
}

/* ── 百分比：最大余数法，合计精确 100.0 ───────────────────── */
function shares(ws) {
  const t = ws.reduce((a, b) => a + b, 0) || 1;
  const raw = ws.map(w => w / t * 100);
  const out = raw.map(x => Math.floor(x * 10) / 10);
  let drift = Math.round((100 - out.reduce((a, b) => a + b, 0)) * 10);
  const ord = raw.map((x, i) => [x - out[i], i]).sort((a, b) => b[0] - a[0]).map(x => x[1]);
  let i = 0;
  while (drift > 0) { out[ord[i % ord.length]] = +(out[ord[i % ord.length]] + 0.1).toFixed(1); drift--; i++; }
  return out;
}

/* ── 数据 → 树 ────────────────────────────────────────────── */
function latestByEngine(updates) {
  const best = {};
  for (const u of updates) {
    const t = Date.parse((u.data && u.data.published_at) || '') || (u.created ? u.created * 1000 : 0);
    if (!best[u.engine] || t > best[u.engine].t)
      best[u.engine] = { version: u.version, t, date: u.data && u.data.published_at, state: u.state, source: u.source };
  }
  return best;
}

const PLATFORM_GROUPS=[
 {id:'core',label:'原有平台',ids:['xiaohongshu','bilibili','tencent','youtube','x']},
 {id:'short',label:'短视频',ids:['douyin','kuaishou','xigua','haokan','weibo']},
 {id:'long',label:'长视频',ids:['tencentvideo','youku','iqiyi','sohuvideo']},
 {id:'community',label:'文字社区',ids:['tieba','zhihu','douban','weibo','weixin']},
 {id:'writing',label:'写作平台',ids:['toutiao','jianshu','juejin','csdn','baijiahao']}
];
function platformGroup(){const id=new URLSearchParams((location.hash.split('?')[1]||'')).get('group')||sessionStorage.getItem('omni-group')||'core';const group=PLATFORM_GROUPS.find(g=>g.id===id)||PLATFORM_GROUPS[0];sessionStorage.setItem('omni-group',group.id);return group;}
function buildModel(channels, updates, ov) {
  const latest = latestByEngine(updates);
  const isCand = id => (id || '').endsWith('--canary');
  const live = channels.filter(c => !isCand(c.id) && !(c.capabilities && c.capabilities.is_canary));

  const engines = new Set([...live.map(c => c.engine), ...updates.map(u => u.engine)]);

  /* 来源权重：平台数×2 ＋ 已实现通道×3 ＋ 有上游版本×6 ＋ 已配版本×2 */
  const engineWeight = {};
  for (const e of engines) {
    const chs = live.filter(c => c.engine === e);
    const plats = new Set(chs.map(c => c.platform)).size;
    const impl = chs.filter(c => c.capabilities && c.capabilities.implemented).length;
    const ver = chs.filter(c => c.version && c.version !== 'unconfigured').length;
    engineWeight[e] = plats * 2 + impl * 3 + (latest[e] ? 6 : 0) + ver * 2;
  }

  function entry(c) {
    const cap = (c && c.capabilities) || {};
    const sibs = c ? live.filter(x => x.engine === c.engine) : [];
    return {
      engine: c ? c.engine : '',
      platform: c ? c.platform : null,
      channelId: c ? c.id : '',
      implemented: !!cap.implemented,
      version: c && c.version && c.version !== 'unconfigured' ? c.version : '',
      health: c ? (c.health || 'unverified') : 'available',
      enabled: !!(c && c.enabled),
      priority: c ? (c.priority ?? 50) : 50,
      implN: sibs.filter(x => x.capabilities && x.capabilities.implemented).length,
      chanN: sibs.length,
      latest: latest[c ? c.engine : ''] || null
    };
  }

  const group=platformGroup();
  const regions = PLATFORMS.filter(([id])=>group.ids.includes(id)).map(([id, name]) => ({
    id, name,
    entries: live.filter(c => c.platform === id && (expandedNetwork || c.capabilities?.implemented)).map(entry)
  }));

  /* 出口与支撑：没有任何平台通道的来源 */
  const withChannel = new Set(live.map(c => c.engine));
  const support = [...engines].filter(e => !withChannel.has(e)).sort((a, b) => engineWeight[b] - engineWeight[a]);
  if(expandedNetwork)regions.push({
    id: 'support', name: '出口与支撑',
    entries: support.map(e => ({
      engine: e, platform: null, channelId: '', implemented: false, version: '',
      health: 'available', enabled: false, priority: 50, implN: 0, chanN: 0, latest: latest[e] || null
    }))
  });

  for(const region of regions){
    region.channelTotal=region.entries.length;
    region.readyTotal=region.entries.filter(e=>e.enabled&&['healthy','degraded'].includes(e.health)).length;
    if(!expandedNetwork){
      const configured=region.entries.some(e=>e.version);
      region.entries=[{engine:'platform-summary',displayName:region.readyTotal?'查看发布通道':'设置发布通道',summary:true,route:'#/p/'+region.id,platform:region.id,implemented:region.channelTotal>0,version:configured?'configured':'',enabled:region.readyTotal>0,health:region.readyTotal?'healthy':'unverified',latest:null,chanN:region.channelTotal,implN:region.channelTotal,priority:50,statusText:region.readyTotal?region.readyTotal+' 条通道已就绪':region.channelTotal+' 条通道 · 待核验'}];
    }
  }

  const byChannel = {};
  for (const r of regions) for (const x of r.entries) if (x.channelId) byChannel[x.channelId] = x;

  /* 区域权重：通道×1 ＋ 已实现×4 ＋ 有上游版本×3 ＋ 已配版本×2 */
  for (const r of regions) {
    r.weight = r.entries.length
      + 4 * r.entries.filter(x => x.implemented).length
      + 3 * r.entries.filter(x => x.latest).length
      + 2 * r.entries.filter(x => x.version).length;
    r.entries.sort((a, b) => engineWeight[b.engine] - engineWeight[a.engine]);
  }

  const regShareAll = shares([...regions.map(r => r.weight), 1]);
  regions.forEach((r, i) => { r.share = regShareAll[i]; });
  const uiShare = regShareAll[regions.length];

  const engList = [...engines].filter(e => engineWeight[e] > 0);
  const engShareMap = {};
  shares(engList.map(e => engineWeight[e])).forEach((s, i) => { engShareMap[engList[i]] = s; });

  return { regions, uiShare, engineWeight, engShareMap, latest,
           engineCount: engines.size, channelCount: live.length, updateCount: updates.length,
           ov: ov || {}, byChannel };
}

/* ── 渲染 ─────────────────────────────────────────────────── */
const ROSE = [232,124,141], AMBER = [249,203,142], INK = [46,27,25];
const mix = (t, a = .14) => `rgb(${ROSE.map((v, i) =>
  Math.round((v + (AMBER[i] - v) * t) * (1 - a) + INK[i] * a)).join(',')})`;
const DOT = { ok: 'rgba(46,27,25,.40)', na: 'rgba(46,27,25,.12)', warn: '#E87C8D' };

const SVGNS = 'http://www.w3.org/2000/svg';
const canvas = $('#canvas');
const root = document.documentElement;
const K = () => parseFloat(getComputedStyle(root).getPropertyValue('--k')) || 1;

let MODEL = null;

function layout(k, M) {
  const W = canvas.clientWidth || 1272;
  const N = M.regions.length, colW = W / N, cx = W / 2;
  const compact=innerHeight<760;
  const yFork = 18 * k, yRegA = (compact?54:70) * k, droop = 12 * k;
  const ySrc0 = (compact?34:46) * k;
  const rMax = Math.max(...M.regions.map(r => r.share)) || 1;

  const regs = M.regions.map((r, i) => {
    const t = (i - (N - 1) / 2) / ((N - 1) / 2 || 1);
    return { ...r, i, x: colW * (i + .5), y: yRegA + droop * t * t };
  });

  /* 位置不在这里定：块的高度要实测，paint() 里顺序排 */
  return { W, N, colW, cx, yFork, ySrc0, regs, k, rMax, gap: 10 * k };
}

function paint() {
  if (!MODEL) return;
  const k = K();
  const L = layout(k, MODEL);
  canvas.innerHTML = '';

  const svg = document.createElementNS(SVGNS, 'svg');
  svg.setAttribute('class', 'wire');
  svg.setAttribute('viewBox', `0 0 ${L.W} 1000`);
  canvas.appendChild(svg);
  const path = (d, stroke, w, op, dash) => {
    const p = document.createElementNS(SVGNS, 'path');
    p.setAttribute('d', d); p.setAttribute('fill', 'none');
    p.setAttribute('stroke', stroke); p.setAttribute('stroke-width', w);
    p.setAttribute('stroke-opacity', op); p.setAttribute('stroke-linecap', 'round');
    if (dash) p.setAttribute('stroke-dasharray', dash);
    svg.appendChild(p);
  };

  /* 区域节点 */
  L.regs.forEach(rg => {
    const node = el('div', 'node');
    node.style.cssText = `left:${rg.x}px;top:${rg.y + 5 * k}px`;
    const nm = el('span', 'nm');
    nm.style.fontSize = '17px';
    nm.textContent = rg.name;
    const pc = el('span', 'pc');
    pc.style.cssText = `font-size:${9.5 * k}px;margin-top:${1 * k}px`;
    pc.textContent = rg.readyTotal ? rg.readyTotal+' 条已就绪' : (rg.channelTotal||0)+' 条发布通道';
    node.append(nm, pc);
    canvas.appendChild(node);

    const m = el('i', 'mark');
    const r = (3.2 + 5.4 * Math.sqrt(rg.share / L.rMax)) * k;
    m.style.cssText = `left:${rg.x}px;top:${rg.y - 5 * k}px;width:${r * 2}px;height:${r * 2}px;`
      + `background:${mix(rg.i / (L.N - 1), .1)};box-shadow:0 0 0 ${3 * k}px rgba(255,249,245,.95)`;
    canvas.appendChild(m);
  });

  /* 来源叶块：一个器官 + 名字。位置按上一块实测高度顺排，绝不重叠 */
  const placed = [];
  const seen = new Set();
  let phase = 0;
  const maxW = Math.max(...Object.values(MODEL.engShareMap), 1);

  L.regs.forEach(rg => {
    let yy = rg.y + L.ySrc0;
    rg.entries.forEach(e => {
      const first = !seen.has(e.engine); seen.add(e.engine);
      const w = MODEL.engShareMap[e.engine] || 0;
      const kind = organOf(e);
      const fs = 14 * k;

      const box = el('div', 'leaf' + (kind === 'fruit' ? ' ripe' : kind === 'bare' ? ' dim' : ''));
      box.style.cssText = `left:${rg.x}px;top:${yy}px;font-size:${8.4 * k}px`;
      box.dataset.engine = e.engine;
      if (e.channelId) box.dataset.channel = e.channelId;
      if(e.route)box.dataset.route=e.route;
      box.style.width=Math.max(100,L.colW-24)+'px';
      box.tabIndex=0;box.setAttribute('role','link');
      box.addEventListener('keydown',event=>{if(event.key==='Enter'||event.key===' '){event.preventDefault();box.click();}});
      box.title=(e.displayName||NAME[e.engine]||e.engine)+(e.version&&!e.summary?' · '+e.version:'')+' · '+(e.statusText||STATE_WORD[kind]);

      const og = organNode(kind, 19 * k, phase);
      box.appendChild(og);
      phase += 0.07;

      const nm = el('span', 'nm');
      nm.style.fontSize = fs.toFixed(2) + 'px';
      nm.textContent = e.displayName || ({sau:'SAU 社区发布',xhsmcp:'小红书发布',biliup:'B站发布',ytuploader:'YouTube 发布',xapi:'X 官方接口',desktopweb:'网页确认',spreado:'Spreado 发布'}[e.engine]) || NAME[e.engine] || e.engine;
      box.appendChild(nm);

      if (first) {
        const pc = el('span', 'meta');
        pc.textContent = w.toFixed(1) + '%' + (e.chanN ? ' · ' + e.implN + '/' + e.chanN : '');
        box.appendChild(pc);
        if (e.latest) {
          const v = el('span', 'meta');
          v.textContent = e.latest.version + (e.latest.t ? ' · ' + ago(null, e.latest.t) : '');
          if (e.version && e.latest.version !== e.version) {
            const bud = el('span', 'newbud');
            bud.innerHTML = budSVG(10 * k);
            bud.title = '上游 ' + e.latest.version + '，本地 ' + e.version;
            v.appendChild(bud);
          }
          box.appendChild(v);
        }
      }

      const word = STATE_WORD[kind];
      if (word) {
        const s = el('span', 'state');
        s.style.color = kindColor(kind);
        s.textContent = e.statusText || word;
        box.appendChild(s);
      }

      canvas.appendChild(box);
      const h = box.offsetHeight;
      placed.push({ rg, e, yy, h, first, w, box });
      yy += h + L.gap;
    });
  });

  const H = (placed.length ? Math.max(...placed.map(n => n.yy + n.h)) : 180) + (innerHeight<760?24:40) * k;
  canvas.style.height = H + 'px';
  svg.setAttribute('viewBox', `0 0 ${L.W} ${H}`);

  /* 量位置：细枝接到器官上 */
  const cbox = canvas.getBoundingClientRect();
  const viewScale=parseFloat(getComputedStyle(root).getPropertyValue('--ui-scale'))||1;
  placed.forEach(nd => {
    const r = nd.box.getBoundingClientRect();
    nd.anchorY = nd.yy - 7 * k;
    nd.bottom = (r.bottom - cbox.top)/viewScale;
    const og = nd.box.querySelector('.organ svg');
    const or_ = og.getBoundingClientRect();
    const p = { x: (or_.left - cbox.left + or_.width / 2)/viewScale, y: (or_.top - cbox.top + or_.height / 2)/viewScale };
    path(`M${nd.rg.x} ${nd.anchorY} C${nd.rg.x} ${nd.anchorY + 6 * k}, ${p.x} ${p.y - 5 * k}, ${p.x} ${p.y - 3 * k}`,
      e_soft(nd), .7 * k, 1);
  });

  /* 中枝 */
  L.regs.forEach(rg => {
    const mine = placed.filter(n => n.rg === rg);
    if (!mine.length) return;
    const col = 'rgba(46,27,25,.26)';
    path(`M${rg.x} ${rg.y + 26 * k} L${rg.x} ${mine[0].anchorY}`, col, 1 * k, 1);
    for (let i = 1; i < mine.length; i++) {
      const from = mine[i - 1].bottom + 2 * k, to = mine[i].anchorY;
      if (to > from) path(`M${rg.x} ${from} L${rg.x} ${to}`, col, 1 * k, 1);
    }
    mine.forEach(nd => {
      const m = el('i', 'mark');
      m.style.cssText = `left:${rg.x}px;top:${nd.anchorY}px;width:${3.4 * k}px;height:${3.4 * k}px;`
        + `background:${nd.e.implemented ? 'rgba(46,27,25,.42)' : 'rgba(46,27,25,.18)'}`;
      canvas.appendChild(m);
    });
  });

  /* 主干 */
  const defs = document.createElementNS(SVGNS, 'defs');
  defs.innerHTML = `<linearGradient id="tg" x1="0" y1="0" x2="0" y2="${H}" gradientUnits="userSpaceOnUse">
    <stop offset="0" stop-color="#E87C8D" stop-opacity=".85"/>
    <stop offset=".5" stop-color="#EE9A87" stop-opacity=".5"/>
    <stop offset="1" stop-color="#F9CB8E" stop-opacity=".16"/></linearGradient>`;
  svg.appendChild(defs);
  path(`M${L.cx} 0 L${L.cx} ${L.yFork}`, 'url(#tg)', 3 * k, 1);

  /* 大枝 */
  L.regs.forEach(rg => {
    const mx = (L.cx + rg.x) / 2;
    path(`M${L.cx} ${L.yFork} C${L.cx} ${rg.y * .5}, ${mx} ${rg.y * .8}, ${rg.x} ${rg.y - 14 * k}`,
      mix(rg.i / (L.N - 1), .1), (1.1 + 1.1 * Math.sqrt(rg.share / L.rMax)) * k, .62);
  });

  /* 根系入口：账号是种子，节点是蜂。两个都带呼吸圈，都能点 */
  {
    const mk = (side, href, col, glyph, label) => {
      const a = el('a', 'root ' + side);
      a.href = href;
      const sp = el('span', 'organ');
      sp.style.color = col;
      sp.innerHTML = `<i class="ring" style="animation-delay:-.35s"></i>` + glyph;
      a.append(sp, document.createTextNode(label));
      canvas.appendChild(a);
    };
    const accN = MODEL.ov.accounts || 0;
    const agN = MODEL.ov.agents_online || 0;
    mk('l', '#/accounts', accN ? TR.wait : TR.stop, seedSVG(accN ? TR.wait : TR.stop, 15 * k), '账号 ' + accN);
    mk('r', '#/agents', agN ? TR.go : TR.stop, beeSVG(agN ? TR.go : TR.stop, 18 * k), '节点 ' + agN);
  }

  /* 树下的工具栏：任务 / 素材 / 更新 / 审计 / 安全，一件不落 */
  {
    const J = MODEL.ov.jobs || {};
    const sum = ks => ks.reduce((a, s) => a + (J[s] || 0), 0);
    const attn = sum(['needs_verify', 'needs_action', 'failed']);
    const pend = sum(['queued', 'preparing', 'submitting', 'retry_wait']);
    const items = [
      ['任务', '#/jobs', attn ? TR.stop : pend ? TR.wait : TR.go, basketSVG, sum(Object.keys(J))],
      ['素材', '#/assets', MODEL.assetsCount ? TR.go : TR.stop, dropSVG, MODEL.assetsCount],
      ['更新', '#/updates', (MODEL.updates || []).some(u => u.state === 'available') ? TR.wait : TR.go,
        sproutSVG, (MODEL.updates || []).length],
      ['审计', '#/audit', TR.go, ringsSVG, 0],
      ['安全', '#/settings', (MODEL.me && MODEL.me.totp_enabled) ? TR.go : TR.wait, rootSVG, 0]
    ];

    const rail = el('div', 'tools');
    rail.style.top = (H - 30 * k) + 'px';
    items.forEach(([label, href, col, glyph, n]) => {
      const a = el('a', 'tool');
      a.href = href;
      const sp = el('span', 'organ');
      sp.style.color = col;
      sp.innerHTML = `<i class="ring" style="animation-delay:-.2s"></i>` + glyph(col, 15 * k);
      a.appendChild(sp);
      const t = el('span', 'tool-n');
      t.textContent = label + (n ? ' ' + n : '');
      a.appendChild(t);
      rail.appendChild(a);
    });
    const ui = el('span', 'tool-n');
    ui.style.color = 'rgba(43,26,23,.30)';
    ui.textContent = '界面 ' + MODEL.uiShare.toFixed(1) + '%';
    rail.appendChild(ui);
    canvas.appendChild(rail);
  }
}

const e_soft = nd => nd.e.implemented ? 'rgba(46,27,25,.20)' : 'rgba(46,27,25,.10)';

/* ── 器官：树不止有枝干 ───────────────────────────────────
   叶 implemented、未配版本   —— 长叶了，还没挂果
   花 已配版本、未启用       —— 开花了，等授粉
   果 已启用且健康           —— 结果了，能摘
   枯 熔断                   —— 枯死
   —  未接入的候选           —— 光枝
   芽 上游版本越过本地       —— 枝头新冒的芽（单独一个记号）

   颜色按红绿灯三色：绿＝通，黄＝差一步，红＝通不了。 */
const STATE_WORD = {
  fruit: '已就绪', flower: '待核验',
  leaf: '待配置', bare: '候选工具', withered: '暂不可用'
};
const TR = { go: '#4C7A4F', wait: '#C9963C', stop: '#C0504A' };
const kindColor = k => k === 'fruit' ? TR.go
  : (k === 'flower' || k === 'leaf') ? TR.wait : TR.stop;

function organOf(e){
  if (e.health === 'broken') return 'withered';
  if (e.enabled) return (e.health === 'healthy' || e.health === 'degraded') ? 'fruit' : 'flower';
  if (e.implemented && e.version) return 'flower';
  if (e.implemented) return 'leaf';
  return 'bare';
}

function organSVG(kind, col, s){
  const box = `width="${s}" height="${s}" viewBox="0 0 20 20"`;
  const paper = 'rgba(255,249,245,.9)';

  if (kind === 'fruit')
    return `<svg ${box}>`
      + `<path d="M10 6.2c2.9-1.7 6.3.2 6.3 4.2 0 4.2-3 7.6-6.3 7.6S3.7 14.6 3.7 10.4c0-4 3.4-5.9 6.3-4.2Z" fill="${col}"/>`
      + `<ellipse cx="7.5" cy="9.3" rx="1.6" ry="1.1" fill="rgba(255,255,255,.5)" transform="rotate(-22 7.5 9.3)"/>`
      + `<path d="M10 6V2.9" stroke="#8A6A48" stroke-width="1.3" stroke-linecap="round"/>`
      + `<path d="M10.2 4.4c1.7-.5 3 .3 3.4 1.9-1.7.5-3-.3-3.4-1.9Z" fill="${col}" opacity=".55"/></svg>`;

  if (kind === 'flower')
    return `<svg ${box}>`
      + [0, 72, 144, 216, 288].map(a =>
          `<ellipse cx="10" cy="4.9" rx="2.35" ry="3.5" fill="${col}" transform="rotate(${a} 10 10)"/>`).join('')
      + `<circle cx="10" cy="10" r="2.05" fill="${paper}"/></svg>`;

  if (kind === 'leaf')
    return `<svg ${box}>`
      + `<path d="M10 2.8c5 1.9 6.8 5.6 6.8 9.2 0 3.2-3.1 6-6.8 6s-6.8-2.8-6.8-6C3.2 8.4 5 4.7 10 2.8Z" fill="${col}"/>`
      + `<path d="M10 5.6v11.6" stroke="${paper}" stroke-width="1.2" stroke-linecap="round"/>`
      + `<path d="M10 9.6 13.1 7.1M10 12.6 6.9 10.1" stroke="${paper}" stroke-width=".9" stroke-linecap="round"/></svg>`;

  if (kind === 'withered')
    return `<svg ${box}>`
      + `<path d="M10 3.2c4.6 1.8 6.2 5.3 6.2 8.6 0 2.7-2.3 5-4.9 5.6" fill="none" stroke="${col}" stroke-width="1.5" stroke-linecap="round"/>`
      + `<path d="M10 3.2C5.4 5 3.8 8.5 3.8 11.8c0 2.7 2.3 5 4.9 5.6" fill="none" stroke="${col}" stroke-width="1.5" stroke-linecap="round"/>`
      + `<path d="M10 6v7" stroke="${col}" stroke-width="1.1" stroke-linecap="round"/></svg>`;

  /* bare：一小截光枝 */
  return `<svg ${box}><path d="M10 3v13" stroke="${col}" stroke-width="1.5" stroke-linecap="round"/>`
    + `<path d="M10 7.5 14.2 4.6M10 12 5.8 9.1" stroke="${col}" stroke-width="1" stroke-linecap="round"/></svg>`;
}

/* 带呼吸圈的可点器官 */
function organNode(kind, size, phase){
  const col = kindColor(kind);
  const sp = el('span', 'organ');
  sp.style.color = col;
  sp.innerHTML = `<i class="ring" style="animation-delay:${(-(phase % 1)).toFixed(2)}s"></i>`
    + organSVG(kind, col, size);
  return sp;
}

/* 种子＝账号，蜂＝节点：供养与授粉的东西 */
function seedSVG(col, s){
  return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
    + `<ellipse cx="10" cy="10.4" rx="4.6" ry="6.1" transform="rotate(20 10 10.4)" fill="${col}"/>`
    + `<path d="M7.6 8.4c.9-.9 2.2-1.2 3.3-.8" stroke="rgba(255,249,245,.85)" stroke-width="1.1" stroke-linecap="round"/></svg>`;
}
function beeSVG(col, s){
  return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
    + `<ellipse cx="7.4" cy="6.6" rx="3.1" ry="2" fill="rgba(255,249,245,.85)" stroke="${col}" stroke-width=".8" transform="rotate(-24 7.4 6.6)"/>`
    + `<ellipse cx="12.6" cy="6.6" rx="3.1" ry="2" fill="rgba(255,249,245,.85)" stroke="${col}" stroke-width=".8" transform="rotate(24 12.6 6.6)"/>`
    + `<ellipse cx="10" cy="11.6" rx="5.2" ry="3.5" fill="${col}"/>`
    + `<path d="M7.6 9.2v4.8M12.4 9.2v4.8" stroke="rgba(255,249,245,.9)" stroke-width="1.1" stroke-linecap="round"/></svg>`;
}

/* 枝头新芽：上游已经越过本地版本 */
function budSVG(s){
  return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
    + `<path d="M10 3.4c3.2 2.2 4.5 4.9 4.5 7.1 0 2.5-2 4.5-4.5 4.5S5.5 13 5.5 10.5c0-2.2 1.3-4.9 4.5-7.1Z" fill="#C99A3E"/></svg>`;
}

/* All routes share one viewport scale; content density never changes typography. */
let pageTreeState = null;
function updateViewScale(){
  const scale=1;
  root.style.setProperty('--ui-scale',scale.toFixed(4));
  root.style.setProperty('--k','1');
}
function fit(){
  updateViewScale();
  if(document.body.classList.contains('onpage')){
    if(pageTreeState && pageTreeState.host.isConnected)drawPageTree(pageTreeState.host,pageTreeState.groups);
  }else if(MODEL)paint();
}
updateViewScale();

/* ── 启动 ─────────────────────────────────────────────────── */
function setStamp() {
  $('#stamp').textContent = new Intl.DateTimeFormat('zh-CN', {
    timeZone: 'Asia/Shanghai', month: '2-digit', day: '2-digit',
    hour: '2-digit', minute: '2-digit', hour12: false
  }).format(new Date());
}

async function load() {
  const nav=$('#platform-groups');if(nav){nav.innerHTML='';for(const group of PLATFORM_GROUPS){const a=el('a','act');a.href='#/?group='+group.id;a.textContent=group.label;a.setAttribute('aria-current',platformGroup().id===group.id?'page':'false');nav.appendChild(a);}}
  const [channels, updates, ov, assets, me, accounts] = await Promise.all([
    api('/channels'), api('/updates'), api('/overview'), api('/assets'), api('/me'), api('/accounts')
  ]);
  MODEL = buildModel(channels, updates, ov);
  MODEL.assetsCount = assets.length;
  MODEL.updates = updates;
  MODEL.me = me;

  const all = MODEL.regions.flatMap(r => r.entries);
  const impl = all.filter(e => e.implemented).length;
  const ver = all.filter(e => e.version).length;
  const up = new Set(all.filter(e => e.latest).map(e => e.engine)).size;

  const jobs=ov.jobs||{};
  const count=states=>states.reduce((n,key)=>n+(jobs[key]||0),0);
  const attention=count(['needs_verify','needs_action','failed']);
  const running=count(['queued','preparing','submitting','submitted','retry_wait']);
  const ready=channels.filter(c=>c.enabled&&['healthy','degraded'].includes(c.health)).length;
  $('#scale').innerHTML=[['待处理',running,'#/jobs'],['已完成',jobs.succeeded||0,'#/jobs'],['需要关注',attention,'#/jobs'],['发布账号',accounts.length,'#/accounts'],['就绪通道',ready,'#/']].map(([label,value,href])=>`<a class="workspace-metric ${label==='需要关注'&&value?'has-attention':''}" href="${href}"><span>${label}</span><strong>${value}<small>${label==='发布账号'?'个':label==='就绪通道'?'条':'项'}</small></strong></a>`).join('');
  $('#network-count').textContent=channels.length?' / '+PLATFORMS.length+' 个平台':'';
  const authorized=accounts.some(a=>a.credentials?.length);
  const next=attention?['有 '+attention+' 项任务需要确认','查看结果后再继续，避免重复发布。','查看任务','#/jobs']:!accounts.length?['从连接第一个账号开始','账号、素材与发布记录会保存在这台电脑。','添加账号','#/accounts']:!authorized?['下一步，完成账号授权','你已添加 '+accounts.length+' 个账号。选择一个账号，连接对应平台。','管理账号','#/accounts']:!ready?['账号准备好了，验证第一条发布通道','完成一次真实核验后，就可以用于日常发布。','查看通道','#/']:['工作空间已准备就绪','新建任务，选择账号与素材，按你的节奏发布。','新建发布','#/jobs?compose=1'];
  $('#next-step').innerHTML=`<span class="step-icon">${icon('sprout')}</span><div><strong>${esc(next[0])}</strong><span>${esc(next[1])}</span></div><a href="${next[3]}">${esc(next[2])}${icon('arrow-up-right')}</a>`;
  $('#footnote').textContent='内容与授权始终保存在本机';
  document.querySelector('.connection-state').classList.add('is-connected');
  document.querySelector('.connection-state').innerHTML='<i></i>本机已连接';

  fit();
}

async function start() {
  setStamp();
  const ok = await bootstrap();
  if (!ok) { $('#unlock').hidden = false; return; }
  try {
    const platforms=await api('/platforms');
    for(const p of platforms)if(!PLATFORMS.some(x=>x[0]===p.id))PLATFORMS.push([p.id,p.label]);
    await load();
    await route();
  } catch (err) {
    if (err.status === 401) { $('#unlock').hidden = false; return; }
    $('#scale').textContent = err.message;
  }
}

$('#unlock-form').addEventListener('submit', async ev => {
  ev.preventDefault();
  const f = ev.target;
  $('#unlock-err').textContent = '';
  try {
    const r = await fetch('/api/login', {
      method: 'POST', credentials: 'same-origin',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        username: f.username.value, password: f.password.value, totp: f.totp.value
      })
    });
    const d = await r.json().catch(() => ({}));
    if (!r.ok) throw new Error(d.detail || '口令错误');
    CSRF = d.csrf || '';
    $('#unlock').hidden = true;
    await load();
  } catch (e) { $('#unlock-err').textContent = e.message; }
});

/* 点一片叶 → 二级页。器官只是状态，管理都在那一页里做。 */
canvas.addEventListener('click', ev => {
  const box = ev.target.closest('.leaf');
  if (!box) return;
  const id = box.dataset.channel;
  location.hash = box.dataset.route || (id ? '#/c/' + encodeURIComponent(id) : '#/');
});

/* ── 二级页 ───────────────────────────────────────────────── */
const pageEl = $('#page');
const esc = s => String(s == null ? '' : s).replace(/[&<>"]/g, c =>
  ({ '&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;' }[c]));

const ORGAN_NAME = STATE_WORD;

function orgOfChannel(c){
  if (!c) return 'bare';
  return organOf({
    health: c.health, enabled: c.enabled, version: c.version === 'unconfigured' ? '' : c.version,
    implemented: !!((c.capabilities || {}).implemented)
  });
}

function ledger(rows){
  return `<div class="led">${rows.filter(Boolean).map(([k, v]) =>
    `<div class="row"><span class="k">${k}</span><span class="v">${v}</span></div>`).join('')}</div>`;
}

function usePage(html){
  document.body.classList.add('onpage');
  updateViewScale();
  pageTreeState=null;
  canvas.hidden = true;
  pageEl.hidden = false;
  pageEl.classList.remove('wide');
  pageEl.innerHTML = html;
  pageEl.querySelectorAll('.p-msg').forEach(e=>{e.setAttribute('role','status');e.setAttribute('aria-live','polite');});
  pageEl.dataset.route=location.hash;
  window.scrollTo(0, 0);
}

async function showChannel(id){
  const [channels, updates, accounts, agents] = await Promise.all([
    api('/channels'), api('/updates'), api('/accounts'), api('/agents')
  ]);
  const c = channels.find(x => x.id === id);
  if (!c){ showMissing('通道不存在'); return; }
  const cap = c.capabilities || {};
  const latest = latestByEngine(updates)[c.engine];
  const kind = orgOfChannel(c);
  const platform = (PLATFORMS.find(p => p[0] === c.platform) || [c.platform, c.platform])[1];

  /* 发出去要过的四关：版本 / 节点 / 凭证 / 核验 */
  const inst = {};
  agents.filter(a => a.enabled && a.last_seen > Date.now()/1000-90).forEach(a => Object.assign(inst, (a.capabilities || {}).channels || {}));
  const nodeReady = !!(inst[c.id] && inst[c.id].ready && inst[c.id].version === c.version);
  const credN = accounts.reduce((n, a) => n + (a.credentials || []).filter(x => a.state === 'active' && x.state === 'active' && x.channel_id === c.id).length, 0);
  const hasVer = c.version !== 'unconfigured';
  const verified = c.health !== 'unverified';

  const pq = (ok, text, hint) =>
    `<div class="pq ${ok ? 'ok' : 'no'}"><i>${ok ? '✓' : '✗'}</i><span>${text}</span>${hint ? `<em>${hint}</em>` : ''}</div>`;
  let next = '可以启用了';
  if (!hasVer) next = '先填通道版本，要和节点里装的那个版本一致';
  else if (!nodeReady) next = '节点尚未就绪，请在下方接入已安装引擎，稍后刷新';
  else if (!credN) next = '还没有凭证：去「账号」页点那片叶，选这条通道贴登录态';
  else if (!verified) next = '还差一次真实核验：创建首次核验任务，成功后即可启用';
  else if (!c.enabled) next = '四关都过了，点「启用通道」';

  const upstream = latest
    ? `<a href="${esc(latest.source)}" target="_blank" rel="noopener noreferrer">${esc(latest.version)}</a>`
      + (latest.t ? ` <em>· ${ago(null, latest.t)}</em>` : '')
      + (c.version !== 'unconfigured' && latest.version !== c.version ? ' <em>· 上游已越过本地</em>' : '')
    : '<em>没有上游记录</em>';

  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title"><span class="p-organ">${organSVG(kind, kindColor(kind), 26)}</span>${esc(NAME[c.engine] || c.engine)}</h2>
    <p class="p-sub">${esc(platform)} · ${esc(c.id)}</p>
    ${ledger([
      ['通道状态', esc(ORGAN_NAME[kind])],
      ['版本', c.version === 'unconfigured' ? '<em>未配置</em>' : `<em>${esc(c.version)}</em>`],
      ['健康', esc(c.health) + (c.failures ? ` <em>· 失败 ${c.failures}</em>` : '')],
      ['上游', upstream],
      ['故障域', `<em>${esc(cap.fault_domain || '—')}</em>`],
      ['媒体', `<em>${esc((cap.media || []).join(' / ') || '—')}</em>`],
      ['执行', esc(cap.execution_mode==='desktop_confirmation'?'桌面填写 · 由你确认发布':'引擎执行 · 需账号和真实核验')],
      ['动作', esc((cap.actions||['publish']).map(x=>({publish:'发内容',comment:'评论',reply:'回复'}[x]||x)).join(' / '))],
      ['出口', `<em>${esc((cap.egress_modes || []).join(' / ') || '—')}</em>`],
      ['优先级', `<em>${c.priority}</em>`],
      c.evidence && c.evidence.remote_id
        ? ['核验作品', `<em>${esc(c.evidence.remote_id)}</em>`]
        : null
    ])}
    <div class="prereq">
      <div class="pq-title">发出去要过四关</div>
      ${pq(hasVer, hasVer ? '版本 ' + esc(c.version) : '版本未配置', hasVer ? '' : '必填')}
      ${pq(nodeReady, nodeReady ? '节点已上报并检查通过' : '节点未上报这个版本', '')}
      ${pq(credN > 0, credN ? '凭证 ' + credN + ' 份' : '没有凭证', '')}
      ${pq(verified, verified ? '已核验' : '未核验', '')}
      <div class="pq-next">下一步：${esc(next)}</div>
    </div>
    <div class="acts" id="acts"></div>
    <div class="p-form" id="form"></div>
    <div class="p-msg" id="msg"></div>
  `);

  const acts = $('#acts'), form = $('#form'), msg = $('#msg');
  const btn = (label, fn, mute) => {
    const b = el('button', 'act' + (mute ? ' mute' : ''));
    b.type = 'button'; b.textContent = label;
    b.addEventListener('click', fn);
    acts.appendChild(b);
    return b;
  };

  /* 登录入口：每个通道都有，能自己扫的直接扫，不能的写清楚要什么 */
  const LOGIN_HINT = {
    ytuploader: '需要 Google OAuth：client_secrets.json + token + 目标频道 ID',
    xapi: '需要 X 官方 API 的 access_token（开发者后台创建应用）',
    spreado: '需要浏览器 Cookie 状态（spreado 的登录态）',
    sau: '先用 sau 自带的登录流程生成 cookie 文件，再把内容贴进来',
    postiz: '需要 Postiz API key + 固定 integration ID',
    matrixmedia: '需要 MatrixMedia 手机号分组凭证'
  };
  const canScan = ['biliup', 'xhsmcp', 'spreado','desktopweb','sau'].includes(c.engine);
  const loginBox = el('div', 'loginbox');
  loginBox.innerHTML = '<div class="lb-title">登录这个通道</div>';
  const lbActs = el('div', 'acts');
  lbActs.style.marginTop = '0';
  loginBox.appendChild(lbActs);
  const accountChoice = el('select');
  accountChoice.setAttribute('aria-label','选择登录账号');
  accounts.filter(a=>a.platform===c.platform).forEach(a=>{const o=el('option');o.value=a.id;o.textContent=a.label;accountChoice.appendChild(o);});
  if(canScan) lbActs.appendChild(accountChoice);
  if (canScan){
    const s = el('button', 'act'); s.type = 'button'; s.textContent = '扫码登录';
    s.addEventListener('click', async () => {
      msg.textContent = '正在本机拉起登录窗口…';
      try {
        const r = await api('/channels/' + encodeURIComponent(c.id) + '/login', 'POST', {account_id:accountChoice.value});
        if(r.desktop_required){
          if(window.chrome && window.chrome.webview)window.chrome.webview.postMessage({type:'login',engine:r.engine,channel:c.id,account:accountChoice.value});
          else throw new Error('请从本机 OmniDispatch 桌面软件进行扫码登录');
        }
        msg.textContent = r.output || '已拉起登录窗口';
      } catch (e) { msg.textContent = e.message; }
    });
    const p = el('button', 'act mute'); p.type = 'button'; p.textContent = '导入登录态';
    p.addEventListener('click', async () => {
      if(['desktopweb','sau'].includes(c.engine)){await route();return;}
      msg.textContent = '正在读取引擎写下的登录态…';
      try {
        await api('/channels/' + encodeURIComponent(c.id) + '/import-login', 'POST', {account_id:accountChoice.value});
        await route();
      } catch (e) { msg.textContent = e.message; }
    });
    lbActs.append(s, p);
  } else {
    const hint = el('span', 'lb-hint');
    hint.textContent = (LOGIN_HINT[c.engine] || '需要这个引擎的登录态') + '。';
    const go = el('a', 'act'); go.href = '#/accounts'; go.textContent = '去账号页补凭证 →';
    lbActs.append(hint, go);
  }
  const trial = el('a','act');trial.href='#/jobs?verify='+encodeURIComponent(c.id);trial.textContent='首次核验发布 →';lbActs.appendChild(trial);
  const actsEl = $('#acts');
  if (actsEl && actsEl.parentNode) actsEl.parentNode.insertBefore(loginBox, actsEl);

  if(cap.implemented){
    try {
      const installed=(await api('/local/channels')).filter(x=>x.engine===c.engine);
      if(installed.length){
        const row=el('div','p-form'), select=el('select');
        installed.forEach(item=>{const o=el('option');o.value=item.version;o.textContent='本机 '+item.version;select.appendChild(o);});
        const attach=el('button','act');attach.textContent='接入本机引擎';attach.type='button';
        const ack=el('label');const check=el('input');check.type='checkbox';
        if(c.engine==='biliup'){ack.append(check,document.createTextNode('已阅读 biliup 上游用途限制'));row.appendChild(ack);}
        attach.onclick=async()=>{attach.disabled=true;try{const r=await api('/local/channels/'+encodeURIComponent(c.id),'POST',{version:select.value,usage_acknowledged:check.checked});msg.textContent=r.note;}catch(e){msg.textContent=e.message;}finally{attach.disabled=false;}};
        row.append(select,attach);loginBox.appendChild(row);
      }
    }catch(e){if(e.status!==403)msg.textContent=e.message;}
  }
  const field = (ph, value) => {
    const i = el('input'); i.placeholder = ph; i.value = value || '';
    form.appendChild(i); return i;
  };
  const submit = (label, fn) => {
    const b = el('button', 'act'); b.type = 'button'; b.textContent = label;
    b.addEventListener('click', fn); form.appendChild(b); return b;
  };

  if (kind === 'leaf' || kind === 'flower' || kind === 'fruit'){
    if (c.version === 'unconfigured'){
      const v = field('版本号，例如 v1.3.4');
      submit('保存版本', async () => {
        try {
          await api('/channels/' + encodeURIComponent(c.id), 'POST',
            { version: v.value.trim(), priority: c.priority, enabled: false });
          await route();
        } catch (e) { msg.textContent = e.message; }
      });
    }
    if (kind === 'bare'){
      /* 未接入：没有可改的，说清原因 */
    } else {
      const pr = field('优先级 0–100', String(c.priority));
      submit('保存优先级', async () => {
        try {
          await api('/channels/' + encodeURIComponent(c.id), 'POST',
            { version: c.version, priority: Number(pr.value) || c.priority, enabled: !!c.enabled });
          await route();
        } catch (e) { msg.textContent = e.message; }
      });
    }
    if (kind === 'flower'){
      const rid = field('已核验的作品 ID');
      submit('记录核验', async () => {
        try {
          await api('/channels/' + encodeURIComponent(c.id) + '/verify', 'POST',
            { action: 'attest_live', remote_id: rid.value.trim() });
          await route();
        } catch (e) { msg.textContent = e.message; }
      });
      btn('启用通道', async () => {
        try {
          await api('/channels/' + encodeURIComponent(c.id), 'POST',
            { version: c.version, priority: c.priority, enabled: true });
          await route();
        } catch (e) { msg.textContent = e.message; }
      });
    }
    if (kind === 'fruit'){
      btn('停用通道', async () => {
        try {
          await api('/channels/' + encodeURIComponent(c.id), 'POST',
            { version: c.version, priority: c.priority, enabled: false });
          await route();
        } catch (e) { msg.textContent = e.message; }
      }, true);
    }
  } else {
    btn('这条通道还没接入', () => {}, true).disabled = true;
  }
}

function showMissing(text){
  usePage(`<a class="back" href="#/">← 工作台</a><h2 class="p-title">${esc(text)}</h2>`);
}

async function showAccounts(){
  const [accs, channels] = await Promise.all([api('/accounts'), api('/channels')]);
  const items = accs.map(a => {
    const col = a.state === 'active' ? TR.go : TR.stop;
    return sp({
      color: col, glyph: seedSVG(col, 17 * K()),
      title: esc(a.label),
      meta: `${esc((PLATFORMS.find(p => p[0] === a.platform) || [a.platform, a.platform])[1])}`
        + ` · 出口 ${esc(a.egress && a.egress.mode || 'direct')}`
        + ` · 授权 ${a.credentials.length} 份`
        + (a.credentials.length ? '（' + a.credentials.map(c => esc(c.channel_id)).join(' / ') + '）' : '')
        + ' · ' + esc(a.state),
      actions: [btn(a.state === 'active' ? '暂停' : '恢复', 'toggle', `data-id="${esc(a.id)}"`)],
      note: a.credentials.length ? '' : '没有授权＝通道拿不到凭证，花永远开不成果。'
    });
  });

  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">账号</h2>
    <p class="p-sub">种子。没有账号，通道就长不出果实。</p>
    ${accs.length ? spineOf(items) : '<div class="empty">还没有账号。</div>'}
    <div class="slot"><div class="p-form" id="form"></div></div>
    <div class="p-msg" id="msg"></div>
  `);
  onAct(async (doWhat, id) => {
    const a = accs.find(x => x.id === id);
    await api('/accounts/' + encodeURIComponent(id) + '/state', 'POST',
      { action: a && a.state === 'active' ? 'cooling' : 'active' });
    await route();
  });
  const form = $('#form'), msg = $('#msg');
  const label = el('input'); label.placeholder = '账号名称';
  const plat = el('select');
  PLATFORMS.forEach(([id, n]) => { const o = el('option'); o.value = id; o.textContent = n; plat.appendChild(o); });
  const preferredPlatform=new URLSearchParams(location.hash.split('?')[1]||'').get('platform');if(PLATFORMS.some(([id])=>id===preferredPlatform))plat.value=preferredPlatform;
  const eg = el('select');
  [['direct', '直连'], ['trusted-static', '可信静态代理'], ['resin', 'Resin 粘性代理']]
    .forEach(([v, t]) => { const o = el('option'); o.value = v; o.textContent = t; eg.appendChild(o); });
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '添加账号';
  go.addEventListener('click', async () => {
    if (!label.value.trim()) { msg.textContent = '账号名称不能为空'; return; }
    try {
      await api('/accounts', 'POST', {
        label: label.value.trim(), platform: plat.value, min_interval: 60,
        egress: { mode: eg.value, ...(eg.value==='direct'?{}:{proxy:proxy.value.trim()}) }, canary_allowed: false
      });
      await route();
    } catch (e) { msg.textContent = e.message; }
  });
  const proxy=el('input');proxy.placeholder='代理地址（非直连时必填）';proxy.type='password';proxy.autocomplete='off';
  form.append(label, plat, eg, proxy, go);

  if (accs.length){
    const who = el('select');
    accs.forEach(a => { const o = el('option'); o.value = a.id; o.textContent = a.label; who.appendChild(o); });
    const chn = el('select');
    const sync = () => {
      chn.innerHTML = '';
      const p = (accs.find(a => a.id === who.value) || {}).platform;
      channels.filter(c => c.platform === p).forEach(c => {
        const o = el('option'); o.value = c.id; o.textContent = c.id; chn.appendChild(o);
      });
    };
    who.addEventListener('change', sync); sync();
    const cred = el('input'); cred.placeholder = '凭证 JSON';
    const save = el('button', 'act'); save.type = 'button'; save.textContent = '保存授权';
    save.addEventListener('click', async () => {
      try {
        await api('/accounts/' + encodeURIComponent(who.value) + '/credentials', 'POST',
          { channel_id: chn.value, value: JSON.parse(cred.value || '{}') });
        await route();
      } catch (e) { msg.textContent = e.message; }
    });
    form.append(who, chn, cred, save);
  }
}

async function showAgents(){
  const agents = await api('/agents');
  const online = a => a.enabled && a.last_seen > Date.now() / 1000 - 90;
  const items = agents.map(a => {
    const col = !a.enabled ? TR.stop : online(a) ? TR.go : TR.wait;
    return sp({
      color: col, glyph: beeSVG(col, 19 * K()),
      title: esc(a.label),
      meta: `最后心跳 ${a.last_seen ? esc(ago(null, a.last_seen * 1000)) : '—'}`
        + ` · 上报通道 ${Object.keys((a.capabilities || {}).channels || {}).length}`
        + ` · ${!a.enabled ? '已撤销' : online(a) ? '在线' : '离线'}`,
      actions: a.enabled ? [btn('撤销', 'revoke', `data-id="${esc(a.id)}"`)] : []
    });
  });

  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">执行节点</h2>
    <p class="p-sub">蜂。节点决定一朵花能不能被核验、能不能真的发出去。</p>
    ${agents.length ? spineOf(items) : '<div class="empty">还没有节点。</div>'}
    <div class="slot"><div class="p-form" id="form"></div><div class="p-form" id="tokenbox"></div></div>
    <div class="p-msg" id="msg"></div>
  `);
  onAct(async (doWhat, id) => {
    await api('/agents/' + encodeURIComponent(id) + '/revoke', 'POST', {});
    await route();
  });
  const form = $('#form'), msg = $('#msg');
  const label = el('input'); label.placeholder = '节点名称';
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '创建节点授权';
  go.addEventListener('click', async () => {
    try {
      const r = await api('/agents', 'POST', { label: label.value.trim() || '本机节点' });
      const box = $('#tokenbox');
      box.innerHTML = '';
      const t = el('input'); t.value = r.token; t.readOnly = true; t.style.minWidth = '420px';
      box.appendChild(t);
      msg.textContent = '令牌只显示这一次，存进节点的 agent.json。';
    } catch (e) { msg.textContent = e.message; }
  });
  form.append(label, go);
}

/* ── 其余功能：一件不落，全部挂在树下的工具栏里 ───────────── */
function basketSVG(c, s){ return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
  + `<path d="M3.4 8h13.2l-1.5 7.2a1.6 1.6 0 0 1-1.6 1.3H6.5a1.6 1.6 0 0 1-1.6-1.3Z" fill="none" stroke="${c}" stroke-width="1.5" stroke-linejoin="round"/>`
  + `<path d="M7 8c0-2.6 1.3-4.6 3-4.6S13 5.4 13 8" fill="none" stroke="${c}" stroke-width="1.4" stroke-linecap="round"/></svg>`; }
function dropSVG(c, s){ return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
  + `<path d="M10 2.8c3.2 3.4 5 6.3 5 8.6a5 5 0 0 1-10 0c0-2.3 1.8-5.2 5-8.6Z" fill="${c}"/>`
  + `<ellipse cx="7.9" cy="11" rx="1.2" ry="1.7" fill="rgba(255,249,245,.7)"/></svg>`; }
function sproutSVG(c, s){ return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
  + `<path d="M10 17V9" stroke="${c}" stroke-width="1.5" stroke-linecap="round"/>`
  + `<path d="M10 9.4C10 6 7.8 4.2 4.6 4.2c0 3.4 2.2 5.2 5.4 5.2Z" fill="${c}"/>`
  + `<path d="M10 11.4c0-2.6 1.8-4.2 4.6-4.2 0 2.6-1.8 4.2-4.6 4.2Z" fill="${c}" opacity=".72"/></svg>`; }
function ringsSVG(c, s){ return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
  + `<circle cx="10" cy="10" r="7" fill="none" stroke="${c}" stroke-width="1.1" opacity=".45"/>`
  + `<circle cx="10" cy="10" r="4.6" fill="none" stroke="${c}" stroke-width="1.2" opacity=".7"/>`
  + `<circle cx="10" cy="10" r="2.1" fill="${c}"/></svg>`; }
function rootSVG(c, s){ return `<svg width="${s}" height="${s}" viewBox="0 0 20 20">`
  + `<path d="M10 3v6" stroke="${c}" stroke-width="1.5" stroke-linecap="round"/>`
  + `<path d="M10 9 5 16M10 9l5 7M10 9v8" stroke="${c}" stroke-width="1.2" stroke-linecap="round" fill="none"/></svg>`; }

/* ── 二级页也是一棵树：根 → 分组枝 → 叶 ─────────────────── */
function drawPageTree(host, groups, nested=false){
  if(!nested)pageTreeState={host,groups};
  const expanded=groups.flatMap(group=>{
    if(group.leaves.length<=36)return [group];
    return Array.from({length:Math.ceil(group.leaves.length/36)},(_,i)=>({...group,name:group.name+' · '+(i+1),leaves:group.leaves.slice(i*36,(i+1)*36)}));
  });
  const bands=[];let band=[],count=0;
  for(const group of expanded){const units=Math.max(1,Math.ceil(group.leaves.length/6));if(count+units>6&&band.length){bands.push(band);band=[];count=0;}band.push(group);count+=units;}
  if(band.length)bands.push(band);
  if(bands.length>1){
    host.innerHTML='';host.style.height='auto';
    for(const groups of bands){const child=el('div','ptree tree-band');host.appendChild(child);drawPageTree(child,groups,true);}
    return;
  }
  groups=expanded;
  const k = K();
  host.innerHTML = '';
  host.classList.toggle('is-empty',!groups.some(group=>group.leaves.length));
  if(!groups.some(group=>group.leaves.length)){
    const route=location.hash.split('?')[0];
    const copy={'#/jobs':['send','第一条发布，从这里开始','准备好账号与内容，创建一个任务，发布进度会在这里呈现。'],'#/assets':['image','素材库还是空的','上传图片或视频，发布时就能直接选择。'],'#/accounts':['users-round','连接你的第一个账号','从下方添加账号开始，再完成对应平台的授权。'],'#/audit':['scroll-text','每一步，都有迹可循','新的工作空间操作会记录在这里。'],'#/updates':['refresh-cw','暂时没有待处理的更新','发现新版本后，你可以在这里查看与核验。']}[route]||['monitor','这里还没有内容','完成设置后，相关状态会在这里呈现。'];
    host.innerHTML=`<div class="empty-state"><span class="empty-illustration">${icon(copy[0])}</span><h3>${copy[1]}</h3><p>${copy[2]}</p></div>`;host.style.height='180px';return;
  }
  const W = host.clientWidth || 1200;
  const ROWS = 6;                                  // 一行最多六片叶，多了就分小列
  const units = groups.map(g => Math.max(1, Math.ceil(g.leaves.length / ROWS)));
  const totalU = units.reduce((a, b) => a + b, 0) || 1;
  const unitW = W / totalU;
  const cx = W / 2;
  const yFork = 22 * k, yG = 74 * k, yL0 = 122 * k, gap = 27 * k;

  let acc = 0;
  const cols = groups.map((g, i) => {
    const w = unitW * units[i];
    const c = { x: acc + w / 2, w, left: acc };
    acc += w;
    return c;
  });

  const rows = Math.max(1, Math.min(ROWS, Math.max(...groups.map(g => g.leaves.length))));
  const H = yL0 + (rows - 1) * gap + 46 * k;
  host.style.height = H + 'px';

  const svg = document.createElementNS(SVGNS, 'svg');
  svg.setAttribute('class', 'wire');
  svg.setAttribute('viewBox', `0 0 ${W} ${H}`);
  host.appendChild(svg);
  const path = (d, stroke, w, op) => {
    const p = document.createElementNS(SVGNS, 'path');
    p.setAttribute('d', d); p.setAttribute('fill', 'none');
    p.setAttribute('stroke', stroke); p.setAttribute('stroke-width', w);
    p.setAttribute('stroke-opacity', op); p.setAttribute('stroke-linecap', 'round');
    svg.appendChild(p);
  };

  path(`M${cx} 0 L${cx} ${yFork}`, 'rgba(232,124,141,.55)', 2.4 * k, 1);

  groups.forEach((g, i) => {
    const { x, w, left } = cols[i];
    const col = g.color || 'rgba(43,26,23,.5)';
    const mx = (cx + x) / 2;
    path(`M${cx} ${yFork} C${cx} ${yG * .5}, ${mx} ${yG * .8}, ${x} ${yG - 10 * k}`, col, 1.5 * k, .55);

    const node = el('div', 'node');
    node.style.cssText = `left:${x}px;top:${yG + 2 * k}px`;
    const nm = el('span', 'nm');
    nm.style.fontSize = (13 + 4 * Math.min(1, g.leaves.length / 3)) * k + 'px';
    nm.textContent = g.name;
    const pc = el('span', 'pc');
    pc.style.cssText = `font-size:${9.5 * k}px`;
    pc.textContent = g.leaves.length ? g.leaves.length + ' 项' : '空';
    node.append(nm, pc);
    host.appendChild(node);

    const m = el('i', 'mark');
    m.style.cssText = `left:${x}px;top:${yG - 6 * k}px;width:${6 * k}px;height:${6 * k}px;`
      + `background:${col};box-shadow:0 0 0 ${3 * k}px rgba(255,249,245,.95)`;
    host.appendChild(m);

    const per = Math.max(1, Math.ceil(g.leaves.length / units[i]));
    g.leaves.forEach((l, j) => {
      const sub = Math.floor(j / ROWS), row = j % ROWS;
      const lx = left + unitW * (sub + .5);
      const y = yL0 + row * gap;

      const li = el(l.href?'a':'div', 'pleaf');
      li.style.cssText = `left:${lx}px;top:${y - 9 * k}px;width:${Math.max(64, unitW - 12)}px`;
      const title=el('span','pl-t');title.textContent=l.t;li.appendChild(title);
      if(l.m){const meta=el('span','pl-m');meta.textContent=l.m;li.appendChild(meta);}
      if(l.href){li.href=l.href;li.style.cursor='pointer';}
      if(l.on){li.style.cursor='pointer';li.setAttribute('role','button');li.tabIndex=0;li.addEventListener('click',l.on);li.addEventListener('keydown',e=>{if(e.key==='Enter'||e.key===' '){e.preventDefault();l.on();}});}
      host.appendChild(li);
    });

    /* 每个小列一根短茎，从枝头垂到最后一叶 */
    const nSub = units[i];
    for (let s = 0; s < nSub; s++){
      const cnt = Math.min(ROWS, g.leaves.length - s * ROWS);
      if (cnt <= 0) continue;
      const lx = left + unitW * (s + .5);
      const yEnd = yL0 + (cnt - 1) * gap - 10 * k;
      path(`M${lx} ${yG + 22 * k} L${lx} ${yEnd}`, col, 1 * k, .3);
    }
  });
}

function pageShell(back, title, sub, extra){
  usePage(`
    <a class="back" href="${back}">← 工作台</a>
    <h2 class="p-title">${title}</h2>
    ${sub ? `<p class="p-sub">${sub}</p>` : ''}
    <div class="ptree" id="ptree"></div>
    ${extra || ''}
    <div class="p-msg" id="msg"></div>`);
  pageEl.classList.add('wide');
  return $('#ptree');
}
function sp(o){
  return `<div class="sp">
    <span class="sp-organ" style="color:${o.color}"><i class="ring" style="animation-delay:-.3s"></i>${o.glyph}</span>
    <div class="sp-body">
      <div class="sp-t">${o.title}${o.ver ? `<em>${o.ver}</em>` : ''}</div>
      ${o.meta ? `<div class="sp-m">${o.meta}</div>` : ''}
      ${o.actions && o.actions.length ? `<div class="sp-a">${o.actions.join('')}</div>` : ''}
    </div>
  </div>${o.note ? `<div class="sp-note">${o.note}</div>` : ''}`;
}
const spineOf = items => `<div class="spine">${items.join('')}</div>`;
const btn = (label, doAttr, extra = '') => `<button class="act" type="button" data-do="${doAttr}" ${extra}>${label}</button>`;
const link = (label, href) => `<a class="act" href="${href}">${label}</a>`;

function onAct(fn){
  pageEl.addEventListener('click', async ev => {
    const b = ev.target.closest('[data-do]');
    if (!b) return;
    try { await fn(b.dataset.do, b.dataset.id, b); } catch (e) { const m = $('#msg'); if (m) m.textContent = e.message; }
  });
}

/* 任务状态 → 器官 */
function jobOrgan(state){
  if (state === 'succeeded') return { k: 'fruit', c: TR.go };
  if (['needs_verify', 'needs_action', 'failed', 'cancelled'].includes(state)) return { k: 'withered', c: TR.stop };
  return { k: 'leaf', c: TR.wait };
}

/* ── 任务：发布队列 ───────────────────────────────────────── */
async function showJob(id){
  const j = await api('/jobs/' + encodeURIComponent(id));
  window.__jobView={id,state:j.state,reason:j.reason,attempts:j.attempts.length};
  const p = j.payload || {};
  usePage(`
    <a class="back" href="#/jobs">← 任务</a>
    <h2 class="p-title">${esc(p.title || '未命名')}</h2>
    <p class="p-sub">${esc(j.state)} · ${esc((PLATFORMS.find(x => x[0] === j.platform) || [j.platform, j.platform])[1])}</p>
    ${ledger([
      ['状态', esc(j.state)],
      ['正文', esc(p.description || '—')],
      ['类型', esc(p.kind || '—')],
      ['动作', esc(({publish:'发布内容',comment:'评论原帖',reply:'回复评论'})[p.action||'publish'])],
      p.target_url?['目标',`<a href="${esc(p.target_url)}" target="_blank" rel="noopener">${esc(p.target_url)}</a>`]:null,
      p.target_comment_id?['目标评论',esc(p.target_comment_id)]:null,
      ['固定版本', `<em>${esc(j.engine_version || '未固定')}</em>`],
      ['计划', j.due ? new Date(j.due * 1000).toLocaleString('zh-CN') : '<em>立即</em>'],
      ['说明', esc(j.reason || '—')],
      j.remote_id ? ['平台作品', `<em>${esc(j.remote_id)}</em>`] : null
    ])}
    <div class="led" style="margin-top:18px">${(j.attempts || []).map(a => `
      <div class="row"><span class="k">第 ${a.generation} 次</span>
      <span class="v">${esc(a.channel_id)} <em>· ${esc(a.version)} · ${esc(a.state)}</em></span></div>`).join('')
      || '<div class="row"><span class="k">尝试</span><span class="v"><em>还没领取执行</em></span></div>'}</div>
    <div class="acts" id="acts"></div>
    <div class="p-form" id="form"></div>
    <div class="p-msg" id="msg"></div>`);

  const acts = $('#acts'), form = $('#form'), msg = $('#msg');
  const doAct = async (action, remote_id) => {
    try { await api('/jobs/' + encodeURIComponent(id) + '/action', 'POST', { action, remote_id }); await route(); }
    catch (e) { msg.textContent = e.message; }
  };
  const btn = (label, fn, mute) => {
    const b = el('button', 'act' + (mute ? ' mute' : '')); b.type = 'button'; b.textContent = label;
    b.addEventListener('click', fn); acts.appendChild(b);
  };
  if(['queued','needs_action','retry_wait','drafted'].includes(j.state)&&(j.channel_id||p.verification_channel||'').startsWith('desktopweb-')){
    btn(j.state==='drafted'?'继续编辑这份草稿':'在桌面继续',()=>{if(window.chrome&&window.chrome.webview)window.chrome.webview.postMessage({type:'browser-job',job:j.id});else msg.textContent='请从本机桌面软件打开任务';});
  }
  if (j.state === 'needs_verify'){
    btn('确认已发布', () => {
      const i = el('input'); i.placeholder = '平台作品 ID';
      form.innerHTML = ''; form.appendChild(i);
      const b = el('button', 'act'); b.type = 'button'; b.textContent = '提交';
      b.addEventListener('click', () => doAct('confirm_published', i.value.trim()));
      form.appendChild(b);
    });
    btn('确认未发布并重试', () => doAct('confirm_not_published'));
  }
  if (['needs_action', 'failed', 'retry_wait'].includes(j.state)) btn('恢复排队', () => doAct('retry'));
  if (['queued', 'needs_action', 'retry_wait'].includes(j.state)) btn('取消任务', () => doAct('cancel'), true);
}

/* ── 素材库 ───────────────────────────────────────────────── */
async function showAssets(){
  const assets = await api('/assets');
  const maxSize = Math.max(1, ...assets.map(a => a.size));
  const items = assets.map(a => {
    const col = TR.go;
    return sp({
      color: col, glyph: dropSVG(col, (8 + 9 * Math.sqrt(a.size / maxSize)).toFixed(1) * KUnit()),
      title: esc(a.name),
      meta: `${esc(a.kind)} · ${(a.size / 1048576).toFixed(2)} MB · ${esc(ago(null, (a.created || 0) * 1000))}`,
      actions: [link('下载', '/api/assets/' + encodeURIComponent(a.id) + '/file')]
    });
  });
  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">素材</h2>
    <p class="p-sub">水滴越大，文件越大。分块上传，断了能续。</p>
    ${assets.length ? spineOf(items) : '<div class="empty">素材库是空的。</div>'}
    <div class="slot"><div class="p-form" id="form"></div></div>
    <div class="p-msg" id="msg"></div>`);

  const form = $('#form'), msg = $('#msg');
  const file = el('input'); file.type = 'file'; file.multiple = true;
  file.addEventListener('change', async () => {
    for (const f of Array.from(file.files || [])){
      try {
        msg.textContent = '上传 ' + f.name + ' …';
        const task = await api('/assets/uploads', 'POST', { name: f.name, size: f.size });
        for (let i = 0; i < task.chunks; i++){
          if ((task.present || []).includes(i)) continue;
          const chunk = f.slice(i * task.chunk_size, Math.min(f.size, (i + 1) * task.chunk_size));
          const r = await fetch('/api/assets/uploads/' + task.id + '/' + i, {
            method: 'PUT', credentials: 'same-origin',
            headers: { 'Content-Type': 'application/octet-stream', 'X-CSRF-Token': CSRF },
            body: chunk
          });
          if (!r.ok) throw new Error('分块上传失败');
        }
        await api('/assets/uploads/' + task.id + '/complete', 'POST', {});
        localStorage.removeItem(resumeKey);
      } catch (e) { msg.textContent = e.message; return; }
    }
    await route();
  });
  form.append(file);
}
const KUnit = () => K();

/* ── 版本与更新 ───────────────────────────────────────────── */
async function showUpdates(){
  const ups = await api('/updates');
  const colOf = s => (s === 'active') ? TR.go
    : (s === 'rolled_back') ? TR.stop
    : (s === 'available' || s === 'staged' || s === 'canary') ? TR.wait : TR.go;

  const items = ups.map(u => {
    const col = colOf(u.state);
    const acts = [];
    if (u.state === 'staged') acts.push(btn('启动灰度', 'canary', `data-id="${esc(u.id)}"`));
    if (u.state === 'canary') acts.push(btn('提升版本', 'promote', `data-id="${esc(u.id)}"`));
    if (u.state === 'active' || u.state === 'canary') acts.push(btn('回滚', 'rollback', `data-id="${esc(u.id)}"`));
    if (u.source) acts.push(`<a class="act" href="${esc(u.source)}" target="_blank" rel="noopener noreferrer">发行页 ↗</a>`);
    return sp({
      color: col, glyph: sproutSVG(col, 17 * K()),
      title: esc(u.engine), ver: esc(u.version),
      meta: esc(u.state) + (u.data && u.data.published_at ? ' · 上游 ' + new Date(u.data.published_at).toLocaleDateString('zh-CN') : ''),
      actions: acts
    });
  });

  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">更新</h2>
    <p class="p-sub">上游只产生候选。装包要签名，提升要满 24 小时和真实样本。</p>
    <div class="sp-a" style="margin-top:18px;padding-left:38px">${btn('检查上游', 'check')}</div>
    ${ups.length ? spineOf(items) : '<div class="empty">还没有更新记录。</div>'}
    <div class="slot"><div class="p-form" id="form"></div></div>
    <div class="p-msg" id="msg"></div>`);

  onAct(async (doWhat, id) => {
    if (doWhat === 'check') { await api('/updates/check', 'POST', {}); return route(); }
    await api('/updates/' + encodeURIComponent(id) + '/action', 'POST', { action: doWhat });
    await route();
  });

  const avail = ups.filter(u => u.state === 'available');
  if (!avail.length) return;
  const form = $('#form');
  const sel = el('select');
  avail.forEach(u => { const o = el('option'); o.value = u.id; o.textContent = u.engine + ' ' + u.version; sel.appendChild(o); });
  const file = el('input'); file.type = 'file'; file.accept = '.zip';
  const sig = el('input'); sig.placeholder = 'Ed25519 签名 Base64';
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '验签并隔离安装';
  go.addEventListener('click', async () => {
    if (!file.files[0]) { $('#msg').textContent = '先选安装包'; return; }
    const fd = new FormData(); fd.append('file', file.files[0]);
    try {
      const r = await fetch('/api/updates/' + encodeURIComponent(sel.value) + '/stage', {
        method: 'POST', credentials: 'same-origin', body: fd,
        headers: { 'X-CSRF-Token': CSRF, 'X-Update-Signature': sig.value.trim() }
      });
      const d = await r.json().catch(() => ({}));
      if (!r.ok) throw new Error(d.detail || '安装失败');
      await route();
    } catch (e) { $('#msg').textContent = e.message; }
  });
  form.append(sel, file, sig, go);
}

/* ── 审计记录：年轮 ───────────────────────────────────────── */
async function showAudit(){
  const rows = await api('/audit');
  const items = rows.slice(0, 200).map(r => sp({
    color: 'rgba(43,26,23,.42)',
    glyph: ringsSVG('rgba(43,26,23,.42)', 15 * K()),
    title: `<span style="font-family:var(--mono);font-size:.86em">${esc(r.event)}</span>`,
    meta: esc(r.subject) + (r.detail && Object.keys(r.detail).length
      ? ' · ' + esc(JSON.stringify(r.detail)) : '')
      + ' · ' + esc(ago(null, (r.created || 0) * 1000))
  }));
  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">审计</h2>
    <p class="p-sub">每一圈都是一次状态改变，从里往外长。</p>
    ${rows.length ? spineOf(items) : '<div class="empty">还没有记录。</div>'}`);
}

/* ── 安全设置 ─────────────────────────────────────────────── */
async function showSettingsLegacy(){
  const me = await api('/me');
  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">安全</h2>
    <p class="p-sub">${esc(me.username)} · 本机直连免口令，隧道访问需要口令${me.totp_enabled ? ' + 动态码' : ''}。</p>
    <div class="p-form" id="pw"></div>
    <div class="p-form" id="totp"></div>
    <div class="p-msg" id="msg"></div>`);
  const msg = $('#msg');
  const pw = $('#pw');
  const cur = el('input'); cur.type = 'password'; cur.placeholder = '当前口令';
  const nw = el('input'); nw.type = 'password'; nw.placeholder = '新口令（至少 12 位）';
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '改口令';
  go.addEventListener('click', async () => {
    try { await api('/password', 'POST', { current_password: cur.value, password: nw.value }); await route(); }
    catch (e) { msg.textContent = e.message; }
  });
  pw.append(cur, nw, go);

  const tp = $('#totp');
  if (!me.totp_enabled){
    const p = el('input'); p.type = 'password'; p.placeholder = '当前口令';
    const gen = el('button', 'act'); gen.type = 'button'; gen.textContent = '生成验证器密钥';
    const code = el('input'); code.placeholder = '验证器当前验证码'; code.style.display = 'none';
    const ok = el('button', 'act'); ok.type = 'button'; ok.textContent = '确认启用'; ok.style.display = 'none';
    const secret = el('input'); secret.readOnly = true; secret.style.display = 'none'; secret.style.minWidth = '300px';
    gen.addEventListener('click', async () => {
      try {
        const r = await api('/totp/setup', 'POST', { password: p.value, code: '' });
        secret.value = r.secret; secret.style.display = '';
        code.style.display = ''; ok.style.display = '';
        msg.textContent = '把它加进验证器，再填当前验证码。';
      } catch (e) { msg.textContent = e.message; }
    });
    ok.addEventListener('click', async () => {
      try {
        const r = await api('/totp/confirm', 'POST', { password: p.value, code: code.value.trim() });
        usePage(`<a class="back" href="#/settings">← 安全</a><h2 class="p-title">恢复码</h2>
          <p class="p-sub">只显示这一次，离线保存。</p>
          <div class="led">${r.recovery_codes.map(c => `<div class="row"><span class="k">恢复码</span><span class="v"><em>${esc(c)}</em></span></div>`).join('')}</div>`);
      } catch (e) { msg.textContent = e.message; }
    });
    tp.append(p, gen, secret, code, ok);
  } else {
    tp.innerHTML = '<span class="empty">双因素认证已启用。</span>';
  }
}

/* ── 安全：根 ─────────────────────────────────────────────── */
async function showSettings(){
  const me = await api('/me');
  const c1 = me.totp_enabled ? TR.go : TR.wait;
  usePage(`
    <a class="back" href="#/">← 工作台</a>
    <h2 class="p-title">安全</h2>
    <p class="p-sub">根。本机直连免口令；走隧道才需要口令${me.totp_enabled ? ' 与动态码' : ''}。</p>
    ${spineOf([
      sp({ color: TR.go, glyph: rootSVG(TR.go, 17 * K()), title: '口令',
        meta: '至少 12 位。改完所有会话失效，需要重新进入。',
        actions: [
          `<input class="inline" id="cur" type="password" placeholder="当前口令">`,
          `<input class="inline" id="nw" type="password" placeholder="新口令（≥12 位）">`,
          btn('改口令', 'pw') ] }),
      sp({ color: c1, glyph: rootSVG(c1, 17 * K()), title: '双因素',
        meta: me.totp_enabled ? '已启用' : '未启用。启用后进隧道要额外一枚动态码，恢复码只显示一次。',
        actions: me.totp_enabled ? [] : [
          `<input class="inline" id="tp" type="password" placeholder="当前口令">`,
          btn('生成验证器密钥', 'totpgen') ] })
    ])}
    <div class="p-msg" id="msg"></div>`);

  onAct(async doWhat => {
    const msg = $('#msg');
    if (doWhat === 'pw'){
      await api('/password', 'POST', { current_password: $('#cur').value, password: $('#nw').value });
      msg.textContent = '口令已改。';
      return;
    }
    if (doWhat === 'totpgen'){
      const r = await api('/totp/setup', 'POST', { password: $('#tp').value, code: '' });
      const box = el('div', 'slot');
      box.innerHTML = `<div class="p-form">
        <input class="inline" readonly value="${esc(r.secret)}" style="min-width:300px">
        <input class="inline" id="tcode" placeholder="验证器当前验证码">
        <button class="act" type="button" data-do="totpok">确认启用</button></div>`;
      pageEl.appendChild(box);
      msg.textContent = '把这串密钥加进验证器，再填当前验证码。';
      return;
    }
    if (doWhat === 'totpok'){
      const r = await api('/totp/confirm', 'POST', { password: $('#tp').value, code: $('#tcode').value.trim() });
      usePage(`
        <a class="back" href="#/settings">← 安全</a>
        <h2 class="p-title">恢复码</h2>
        <p class="p-sub">只显示这一次。离线保存，每枚只能用一次。</p>
        <div class="spine">${r.recovery_codes.map(c => sp({
          color: TR.go, glyph: ringsSVG(TR.go, 15 * K()),
          title: `<span style="font-family:var(--mono)">${esc(c)}</span>`
        })).join('')}</div>`);
    }
  });
}

/* ── 二级页全部改成小树：根 → 分组枝 → 叶 ───────────────── */
async function pageUpdates(){
  const ups = await api('/updates');
  const BUCKETS = [
    ['available', '候选', TR.wait],
    ['staged', '已隔离', TR.wait],
    ['canary', '灰度中', TR.wait],
    ['active', '已激活', TR.go],
    ['rolled_back', '已回滚', TR.stop]
  ];
  const groups = BUCKETS.map(([st, name, col]) => ({
    name, color: col,
    leaves: ups.filter(u => u.state === st).map(u => ({
      t: u.engine + ' ' + u.version,
      m: u.data && u.data.published_at ? new Date(u.data.published_at).toLocaleDateString('zh-CN') : '',
      on: st === 'staged' ? () => actUpdate(u.id, 'canary')
        : st === 'canary' ? () => actUpdate(u.id, 'promote')
        : (st === 'active' || st === 'rolled_back') ? () => actUpdate(u.id, 'rollback')
        : null
    }))
  }));
  const host = pageShell('#/', '更新', '查看社区引擎的新版本，核验后再升级正在使用的通道。');
  drawPageTree(host, groups);

  const box = el('div', 'p-form');
  box.style.marginTop = '10px';
  const check = el('button', 'act'); check.type = 'button'; check.textContent = '检查上游';
  check.addEventListener('click', async () => {
    try { await api('/updates/check', 'POST', {}); await route(); } catch (e) { $('#msg').textContent = e.message; }
  });
  box.appendChild(check);

  const avail = ups.filter(u => u.state === 'available');
  if (avail.length){
    const sel = el('select');
    avail.forEach(u => { const o = el('option'); o.value = u.id; o.textContent = u.engine + ' ' + u.version; sel.appendChild(o); });
    const file = el('input'); file.type = 'file'; file.accept = '.zip';
    const sig = el('input'); sig.placeholder = 'Ed25519 签名 Base64';
    const go = el('button', 'act'); go.type = 'button'; go.textContent = '验签安装';
    go.addEventListener('click', async () => {
      if (!file.files[0]) { $('#msg').textContent = '先选安装包'; return; }
      const fd = new FormData(); fd.append('file', file.files[0]);
      try {
        const r = await fetch('/api/updates/' + encodeURIComponent(sel.value) + '/stage', {
          method: 'POST', credentials: 'same-origin', body: fd,
          headers: { 'X-CSRF-Token': CSRF, 'X-Update-Signature': sig.value.trim() }
        });
        const d = await r.json().catch(() => ({}));
        if (!r.ok) throw new Error(d.detail || '安装失败');
        await route();
      } catch (e) { $('#msg').textContent = e.message; }
    });
    box.append(sel, file, sig, go);
  }
  $('#page').appendChild(box);
}
async function actUpdate(id, action){
  try { await api('/updates/' + encodeURIComponent(id) + '/action', 'POST', { action }); await route(); }
  catch (e) { $('#msg').textContent = e.message; }
}

const jobDrafts=new Map();
async function pageJobs(){
  const draftParams=new URLSearchParams(location.hash.split('?')[1]||'');draftParams.delete('compose');
  const draftKey='#/jobs'+(draftParams.size?'?'+draftParams.toString():'');
  const draft=jobDrafts.get(draftKey);
  const [jobs, accounts, assets, channels] = await Promise.all([api('/jobs'), api('/accounts'), api('/assets'), api('/channels')]);
  const BUCKETS = [
    ['已发布', TR.go, j => j.state === 'succeeded'],
    ['草稿', TR.wait, j=>j.state==='drafted'],
    ['进行中', TR.wait, j => ['queued', 'preparing', 'submitting', 'submitted', 'retry_wait'].includes(j.state)],
    ['待确认', TR.stop, j => ['needs_verify', 'needs_action'].includes(j.state)],
    ['已失败', TR.stop, j => ['failed', 'cancelled'].includes(j.state)]
  ];
  const groups = BUCKETS.map(([name, col, pick]) => ({
    name, color: col,
    leaves: jobs.filter(pick).map(j => ({
      t: (j.payload && j.payload.title) || '未命名',
      m: `${(PLATFORMS.find(p => p[0] === j.platform) || [j.platform, j.platform])[1]} · ${j.state}`,
      href: '#/j/' + encodeURIComponent(j.id)
    }))
  }));
  const host = pageShell('#/', '任务',
    accounts.length ? '安排发布、跟进结果，让内容按计划抵达。' : '先添加一个账号，再开始你的第一条发布。');
  drawPageTree(host, groups);
  const requestedPlatform=new URLSearchParams(location.hash.split('?')[1]||'').get('platform');
  if (!accounts.length || (requestedPlatform&&!accounts.some(a=>a.platform===requestedPlatform))){
    const slot0 = el('div', 'slot');
    slot0.innerHTML = `<div class="p-form">
      <a class="act" href="#/accounts">先去建一个账号 →</a>
      <span class="sp-m" style="align-self:center">任务必须挂在账号下，没有账号就投不出去。</span>
    </div>`;
    $('#page').appendChild(slot0);
    return;
  }

  const slot = el('div', 'slot');
  const form = el('div', 'p-form');
  const who = el('select');
  accounts.forEach(a => { const o = el('option'); o.value = a.id; o.textContent = a.label; who.appendChild(o); });
  const title = el('input'); title.placeholder = '标题';
  const desc = el('textarea'); desc.placeholder = '正文';
  const kind = el('select');
  [['video', '视频'], ['images', '图文'], ['text', '纯文本']].forEach(([v, t]) => {
    const o = el('option'); o.value = v; o.textContent = t; kind.appendChild(o);
  });
  const action=el('select');[['publish','发布到自己的账号'],['comment','评论指定帖子'],['reply','回复指定评论']].forEach(([v,t])=>{const o=el('option');o.value=v;o.textContent=t;action.appendChild(o);});
  const targetURL=el('input');targetURL.placeholder='原帖 HTTPS 链接';targetURL.type='url';
  const commentID=el('input');commentID.placeholder='目标评论 ID / 楼层';
  const replyUser=el('input');replyUser.placeholder='被回复用户 ID（小红书）';
  const delivery=el('select');[['published','正式发布'],['draft','仅保存草稿']].forEach(([v,t])=>{const o=el('option');o.value=v;o.textContent=t;delivery.appendChild(o);});
  const due = el('input'); due.type = 'datetime-local';
  const media=el('select');media.multiple=true;media.setAttribute('aria-label','选择素材');
  const options=el('textarea');options.placeholder='平台参数 JSON（可选）';options.setAttribute('aria-label','平台参数');
  const tid=el('input');tid.placeholder='B站分区 ID（必填）';tid.type='number';tid.min='1';
  const tags=el('input');tags.placeholder='标签，用逗号分隔';
  const visibility=el('select');[['private','YouTube · 私密'],['unlisted','YouTube · 不公开'],['public','YouTube · 公开']].forEach(([v,t])=>{const o=el('option');o.value=v;o.textContent=t;visibility.appendChild(o);});
  const trial=el('select');const normal=el('option');normal.value='';normal.textContent='正常发布';trial.appendChild(normal);
  const verification=new URLSearchParams((location.hash.split('?')[1]||'')).get('verify')||'';
  const refreshInputs=()=>{
    const account=accounts.find(a=>a.id===who.value);if(account.platform==='x'||action.value!=='publish'||['tieba','jianshu','juejin','csdn','weixin'].includes(account.platform))kind.value='text';media.innerHTML='';
    if(action.value!=='publish')delivery.value='published';title.placeholder=action.value==='publish'?'标题':'任务备注（可选）';
    targetURL.hidden=action.value==='publish';commentID.hidden=action.value!=='reply';replyUser.hidden=!(action.value==='reply'&&account.platform==='xiaohongshu');commentID.placeholder=account.platform==='x'?'要回复的实际帖子 ID（不是楼层）':'目标评论 ID / 楼层';delivery.hidden=action.value!=='publish';
    assets.filter(a=>a.kind===kind.value).forEach(a=>{const o=el('option');o.value=a.id;o.textContent=a.name;media.appendChild(o);});
    if(!media.options.length){const empty=el('option');empty.value='';empty.disabled=true;empty.textContent='暂无匹配素材，请先到素材库导入';media.appendChild(empty);}
    media.hidden=kind.value==='text';tid.hidden=action.value!=='publish'||account.platform!=='bilibili';visibility.hidden=action.value!=='publish'||account.platform!=='youtube';
    trial.innerHTML='';trial.appendChild(normal);
    channels.filter(c=>c.platform===account.platform&&c.capabilities.implemented&&(c.capabilities.actions||['publish']).includes(action.value)&&(delivery.value!=='draft'||c.engine==='desktopweb')).forEach(c=>{const o=el('option');o.value=c.id;o.textContent='首次核验 · '+(NAME[c.engine]||c.engine);trial.appendChild(o);});
    if(verification)trial.value=verification;
    tags.hidden=action.value!=='publish'||account.platform==='x';
    const titleCaption=title.closest('.field')?.querySelector('.field-label');if(titleCaption)titleCaption.textContent=action.value==='publish'?'标题':'任务备注（可选）';
    const bodyCaption=desc.closest('.field')?.querySelector('.field-label');if(bodyCaption)bodyCaption.textContent=action.value==='publish'?'正文':'评论内容';
  };
  const preferred=new URLSearchParams(location.hash.split('?')[1]||'').get('platform');const preferredAccount=accounts.find(a=>a.platform===preferred);if(preferredAccount)who.value=preferredAccount.id;
  const target=channels.find(c=>c.id===verification);if(target){const a=accounts.find(a=>a.platform===target.platform);if(a)who.value=a.id;}
  who.onchange=refreshInputs;kind.onchange=refreshInputs;action.onchange=refreshInputs;delivery.onchange=refreshInputs;refreshInputs();
  let intent=draft?.intent||crypto.randomUUID(),lastPayload=draft?.lastPayload||'';
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '加入队列';
  go.addEventListener('click', async () => {
    go.disabled=true;
    let submitted=false;
    try {
      const account=accounts.find(a=>a.id===who.value);
      const platformOptions=JSON.parse(options.value.trim()||'{}');
      if(action.value==='reply'&&account.platform==='xiaohongshu'&&replyUser.value.trim())platformOptions.target_user_id=replyUser.value.trim();
      if(!platformOptions||Array.isArray(platformOptions)||typeof platformOptions!=='object')throw new Error('平台参数必须是 JSON 对象');
      if(action.value==='publish'&&account.platform==='bilibili'&&!(trial.value||'').startsWith('desktopweb-'))platformOptions.tid=Number(tid.value);
      if(action.value==='publish'&&account.platform==='youtube')platformOptions.visibility=visibility.value;
      if(action.value==='publish'&&account.platform!=='x'&&tags.value.trim())platformOptions.tags=tags.value.split(/[,，]/).map(t=>t.trim()).filter(Boolean);
      const payload={account_id:who.value,title:title.value.trim()||(action.value!=='publish'?desc.value.trim().slice(0,30):''),description:desc.value.trim(),kind:kind.value,action:action.value,target_url:targetURL.value.trim(),target_comment_id:commentID.value.trim(),delivery:delivery.value,
        assets:kind.value==='text'?[]:Array.from(media.selectedOptions).map(o=>o.value),
        due:due.value?Date.parse(due.value)/1000:null,options:platformOptions,canary:false,verification_channel:trial.value||null};
      if(!payload.title)throw new Error('请填写标题');
      if(account.platform==='xiaohongshu'&&!payload.description)throw new Error('请填写小红书正文');
      if(action.value==='publish'&&account.platform==='xiaohongshu'&&payload.title.length>20)throw new Error('小红书标题最多 20 字');
      if(kind.value!=='text'&&!payload.assets.length)throw new Error('请先去素材页上传，并在这里选择素材');
      if(kind.value==='video'&&payload.assets.length!==1)throw new Error('视频任务请选择一个素材');
      if(action.value==='publish'&&account.platform==='bilibili'&&!platformOptions.tid&&!(trial.value||'').startsWith('desktopweb-'))throw new Error('请填写 B站分区 ID');
      const fingerprint=JSON.stringify(payload);if(lastPayload&&lastPayload!==fingerprint)intent=crypto.randomUUID();lastPayload=fingerprint;
      const job=await api('/jobs','POST',{...payload,idempotency_key:intent});submitted=true;jobDrafts.delete(draftKey);location.hash='#/j/'+job.id;
    } catch(e){$('#msg').textContent=e.message;}finally{if(!submitted)remember();go.disabled=false;}
  });
  slot.classList.add('composer-section');slot.id='job-compose';
  const composeHeading=el('div','composer-heading');composeHeading.innerHTML='<span class="section-kicker">COMPOSE</span><h3>新建发布</h3><p>先选择账号，再准备内容与发布方式。</p>';slot.appendChild(composeHeading);
  form.classList.add('job-composer');
  const field=(text,control,wide=false)=>{const label=el('label','field'+(wide?' field-wide':''));const caption=el('span','field-label');caption.textContent=text;label.append(caption,control);return label;};
  form.append(field('发布账号',who),field('任务类型',action),field('标题',title,true),field('正文',desc,true),field('原帖链接',targetURL,true),field('目标评论',commentID),field('被回复用户',replyUser),field('内容格式',kind),field('发布素材',media,true),field('内容标签',tags),field('B站分区',tid),field('可见范围',visibility),field('保存方式',delivery),field('发布时间',due),field('发布通道',trial));
  const advanced=el('details','composer-advanced field-wide');const summary=el('summary');summary.textContent='高级平台参数';advanced.append(summary,field('平台参数 JSON',options,true));form.appendChild(advanced);
  const submitRow=el('div','composer-submit field-wide');go.classList.add('primary');go.textContent='加入发布队列';const submitHint=el('span');submitHint.textContent='提交前会检查账号授权与通道状态。';submitRow.append(submitHint,go);form.appendChild(submitRow);

  const controls=[...form.querySelectorAll('input,textarea,select')];
  const restore=(control,values)=>{
    if(control.tagName==='SELECT'){
      for(const option of control.options)option.selected=values.includes(option.value);
      if(!control.multiple&&control.selectedIndex<0)control.selectedIndex=0;
    }else control.value=values[0]||'';
  };
  if(draft){
    for(const control of [who,action,kind,delivery]){const i=controls.indexOf(control);if(draft.values[i])restore(control,draft.values[i]);}
    refreshInputs();
    controls.forEach((control,i)=>{if(draft.values[i])restore(control,draft.values[i]);});
    refreshInputs();
    for(const control of [media,trial]){const i=controls.indexOf(control);if(draft.values[i])restore(control,draft.values[i]);}
  }
  const remember=()=>jobDrafts.set(draftKey,{intent,lastPayload,values:controls.map(control=>control.tagName==='SELECT'?[...control.selectedOptions].map(x=>x.value):[control.value])});
  form.addEventListener('input',remember);form.addEventListener('change',remember);

  slot.appendChild(form);
  $('#page').appendChild(slot);
  if(new URLSearchParams(location.hash.split('?')[1]||'').has('compose')){slot.scrollIntoView({block:'start'});title.focus({preventScroll:true});}
}

async function pageAssets(){
  const assets = await api('/assets');
  const groups = ['video', 'images'].map(kind => ({
    name: kind === 'video' ? '视频' : '图片',
    color: TR.go,
    leaves: assets.filter(a => a.kind === kind).map(a => ({
      t: a.name, m: (a.size / 1048576).toFixed(1) + ' MB · 点下载',
      href: '/api/assets/' + encodeURIComponent(a.id) + '/file'
    }))
  }));
  const host = pageShell('#/', '素材', '把图片与视频整理在一起，发布时随时取用。');
  drawPageTree(host, groups);

  const slot = el('div', 'slot');
  slot.innerHTML = `<div class="p-form">
    <input type="file" multiple accept=".mp4,.mov,.webm,.mkv,.jpg,.jpeg,.png,.webp">
  </div>`;
  $('#page').appendChild(slot);
  const input = slot.querySelector('input');
  input.addEventListener('change', async () => {
    const msg = $('#msg');
    for (const f of Array.from(input.files || [])){
      try {
        msg.textContent = '上传 ' + f.name + ' …';
        const resumeKey='omni-upload:'+f.name+':'+f.size+':'+f.lastModified;
        let task;
        try{const saved=JSON.parse(localStorage.getItem(resumeKey)||'null');if(saved)task=await api('/assets/uploads/'+saved.id);}catch{}
        if(!task||task.state==='completed')task=await api('/assets/uploads','POST',{name:f.name,size:f.size});
        localStorage.setItem(resumeKey,JSON.stringify({id:task.id}));
        for (let i = 0; i < task.chunks; i++){
          if ((task.present || []).includes(i)) continue;
          const chunk = f.slice(i * task.chunk_size, Math.min(f.size, (i + 1) * task.chunk_size));
          const r = await fetch('/api/assets/uploads/' + task.id + '/' + i, {
            method: 'PUT', credentials: 'same-origin',
            headers: { 'Content-Type': 'application/octet-stream', 'X-CSRF-Token': CSRF },
            body: chunk
          });
          if (!r.ok) throw new Error('分块上传失败');
        }
        await api('/assets/uploads/' + task.id + '/complete', 'POST', {});
        localStorage.removeItem(resumeKey);
      } catch (e) { msg.textContent = e.message; return; }
    }
    await route();
  });
}

async function pageAudit(){
  const rows = await api('/audit');
  const KEY = [['auth', '认证'], ['channel', '通道'], ['account', '账号'], ['job', '任务'],
               ['update', '更新'], ['agent', '节点'], ['asset', '素材']];
  const groups = KEY.map(([pre, name]) => {
    const mine = rows.filter(r => (r.event || '').startsWith(pre));
    return {
      name, color: 'rgba(43,26,23,.45)',
      leaves: mine.slice(0, 4).map(r => ({
        t: (r.event || '').replace(new RegExp('^' + pre + '\\.'), ''),
        m: (r.subject || '').slice(0, 10) + ' · ' + ago(null, (r.created || 0) * 1000),
        on: () => showRecord(r)
      })).concat(mine.length > 4 ? [{ t: '还有 ' + (mine.length - 4) + ' 条', m: '点枝保留全部', on: () => filterAudit(rows, pre) }] : [])
    };
  });
  const host = pageShell('#/', '审计', '每一步操作都有记录，方便追溯与核对。');
  drawPageTree(host, groups);

  const rec = el('div', 'slot');
  rec.id = 'recdetail';
  $('#page').appendChild(rec);
  window.showRecord = showRecord;
}

function showRecord(r){
  const box = $('#recdetail');
  if (!box) return;
  box.innerHTML = `<div class="sp-body" style="padding-left:0">
    <div class="sp-t" style="font-family:var(--mono);font-size:14px">${esc(r.event)}</div>
    <div class="sp-m">${esc(new Date((r.created || 0) * 1000).toLocaleString('zh-CN'))} · ${esc(r.subject)}</div>
    <div class="sp-m" style="margin-top:6px;white-space:pre-wrap;word-break:break-all">${esc(JSON.stringify(r.detail || {}, null, 2))}</div>
    <div class="sp-a"><button class="act" type="button" id="closeRec">收起</button></div>
  </div>`;
  box.querySelector('#closeRec').addEventListener('click', () => { box.innerHTML = ''; });
}

async function filterAudit(rows, pre){
  const mine = rows.filter(r => (r.event || '').startsWith(pre));
  const box = $('#recdetail');
  if (!box) return;
  box.innerHTML = `<div class="led">${mine.map(r => `
    <div class="row"><span class="k">${esc(ago(null, (r.created || 0) * 1000))}</span>
    <span class="v"><em>${esc(r.event)}</em> ${esc(r.subject)}</span></div>`).join('')}</div>
    <div class="sp-a"><button class="act" type="button" id="closeRec">收起</button></div>`;
  box.querySelector('#closeRec').addEventListener('click', () => { box.innerHTML = ''; });
}

async function pageAccounts(){
  const [accs, channels] = await Promise.all([api('/accounts'), api('/channels')]);
  const groups = PLATFORMS.map(([id, name]) => ({
    name,
    color: accs.some(a => a.platform === id) ? TR.go : TR.stop,
    leaves: accs.filter(a => a.platform === id).map(a => ({
      t: a.label, m: a.state + ' · 授权 ' + a.credentials.length,
      on: () => accountPanel(a, channels)
    }))
  })).filter(group=>group.leaves.length);
  const host = pageShell('#/', '账号',
    '集中管理发布身份与平台授权。每个账号独立保存登录状态。');
  drawPageTree(host, groups.length?groups:[{name:'尚无账号',color:TR.wait,leaves:[]}]);

  const slot = el('div', 'slot');
  const form = el('div', 'p-form');
  const label = el('input'); label.placeholder = '账号名称';
  const plat = el('select');
  PLATFORMS.forEach(([id, n]) => { const o = el('option'); o.value = id; o.textContent = n; plat.appendChild(o); });
  const preferredPlatform=new URLSearchParams(location.hash.split('?')[1]||'').get('platform');if(PLATFORMS.some(([id])=>id===preferredPlatform))plat.value=preferredPlatform;
  const eg = el('select');
  [['direct', '直连'], ['trusted-static', '可信静态代理'], ['resin', 'Resin 粘性代理']]
    .forEach(([v, t]) => { const o = el('option'); o.value = v; o.textContent = t; eg.appendChild(o); });
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '添加账号';
  go.addEventListener('click', async () => {
    if (!label.value.trim()) { $('#msg').textContent = '账号名称不能为空'; return; }
    try {
      await api('/accounts', 'POST', {
        label: label.value.trim(), platform: plat.value, min_interval: 60,
        egress: { mode: eg.value, ...(eg.value==='direct'?{}:{proxy:proxy.value.trim()}) }, canary_allowed: false
      });
      await route();
    } catch (e) { $('#msg').textContent = e.message; }
  });
  const proxy=el('input');proxy.placeholder='代理地址（非直连时必填）';proxy.type='password';proxy.autocomplete='off';
  form.append(label, plat, eg, proxy, go);
  slot.appendChild(form);
  const panel = el('div'); panel.id = 'recpanel';
  $('#page').append(slot, panel);
}

function accountPanel(a, channels){
  const panel = $('#recpanel');
  if (!panel) return;
  const mine = channels.filter(c => c.platform === a.platform);
  panel.innerHTML = `<div class="sp-body" style="padding-left:0">
    <div class="sp-t">${esc(a.label)}</div>
    <div class="sp-m">${esc(a.platform)} · 出口 ${esc(a.egress && a.egress.mode || 'direct')} · ${esc(a.state)}
      · 授权 ${a.credentials.length} 份</div>
    <div class="sp-a">
      <button class="act" type="button" id="toggleAcc">${a.state === 'active' ? '暂停账号' : '恢复账号'}</button>
      <button class="act" type="button" id="closeAcc">收起</button>
    </div>
    <div class="p-form" id="credForm"></div>
  </div>`;
  panel.querySelector('#closeAcc').addEventListener('click', () => { panel.innerHTML = ''; });
  panel.querySelector('#toggleAcc').addEventListener('click', async () => {
    try {
      await api('/accounts/' + encodeURIComponent(a.id) + '/state', 'POST',
        { action: a.state === 'active' ? 'cooling' : 'active' });
      await route();
    } catch (e) { $('#msg').textContent = e.message; }
  });

  const cf = panel.querySelector('#credForm');
  if (!mine.length) { cf.innerHTML = '<span class="empty">这个平台还没有通道，先给通道配版本。</span>'; return; }
  const chn = el('select');
  mine.forEach(c => { const o = el('option'); o.value = c.id; o.textContent = c.id; chn.appendChild(o); });
  const fields=el('div','p-form');
  let collect=()=>({});
  const field=(label,type='text')=>{const i=el('input');i.placeholder=label;i.type=type;i.autocomplete='off';fields.appendChild(i);return i;};
  const jsonFile=(label)=>{const wrap=el('label');wrap.textContent=label;const input=el('input');input.type='file';input.accept='.json';wrap.appendChild(input);fields.appendChild(wrap);return async()=>{if(!input.files[0])throw new Error('请选择'+label);return JSON.parse(await input.files[0].text());};};
  const refresh=()=>{
    fields.innerHTML='';const channel=mine.find(c=>c.id===chn.value);
    if(channel.engine==='xapi'){
      const token=field('用户 OAuth Access Token','password'),user=field('固定的 X 用户 ID');
      collect=async()=>{if(!token.value.trim()||!user.value.trim())throw new Error('请填写令牌和用户 ID');return {access_token:token.value.trim(),user_id:user.value.trim()};};
    }else if(channel.engine==='ytuploader'){
      const secret=jsonFile('Google OAuth 客户端 JSON'),token=jsonFile('Google OAuth 登录令牌 JSON'),id=field('固定的 YouTube 频道 ID');
      collect=async()=>{if(!id.value.trim())throw new Error('请填写频道 ID');return {client_secrets:await secret(),token:await token(),channel_id:id.value.trim()};};
    }else if(['biliup','spreado'].includes(channel.engine)){
      const file=jsonFile('该引擎导出的登录态 JSON');collect=async()=>({cookies:await file()});
      const link=el('a','act');link.href='#/c/'+encodeURIComponent(channel.id);link.textContent='在桌面扫码登录 →';fields.appendChild(link);
    }else if(['desktopweb','sau'].includes(channel.engine)){
      const link=el('a','act');link.href='#/c/'+encodeURIComponent(channel.id);link.textContent='在本机浏览器登录并绑定账号 →';fields.appendChild(link);collect=async()=>{throw new Error('请进入通道页登录，登录态会加密保存');};
    }else if(channel.engine==='xhsmcp'){
      const link=el('a','act');link.href='#/c/'+encodeURIComponent(channel.id);link.textContent='创建此账号的专属扫码会话 →';fields.appendChild(link);
      collect=async()=>{throw new Error('小红书请从通道页扫码并导入，软件会自动绑定专属会话');};
    }else{
      const val=el('textarea');val.placeholder='此引擎的凭证 JSON';fields.appendChild(val);collect=async()=>JSON.parse(val.value||'{}');
    }
  };
  chn.onchange=refresh;refresh();
  const save=el('button','act');save.type='button';save.textContent='保存授权';
  save.onclick=async()=>{save.disabled=true;try{const value=await collect();await api('/accounts/'+encodeURIComponent(a.id)+'/credentials','POST',{channel_id:chn.value,value});await route();}catch(e){$('#msg').textContent=e.message;}finally{save.disabled=false;}};
  cf.append(chn,fields,save);

}

async function pageAgents(){
  const agents = await api('/agents');
  const online = a => a.enabled && a.last_seen > Date.now() / 1000 - 90;
  const groups = [
    { name: '在线', color: TR.go, leaves: agents.filter(online).map(a => ({ t: a.label, m: '心跳 ' + ago(null, a.last_seen * 1000), on: () => agentPanel(a) })) },
    { name: '离线', color: TR.wait, leaves: agents.filter(a => a.enabled && !online(a)).map(a => ({ t: a.label, m: a.last_seen ? ago(null, a.last_seen * 1000) : '从未心跳', on: () => agentPanel(a) })) },
    { name: '已撤销', color: TR.stop, leaves: agents.filter(a => !a.enabled).map(a => ({ t: a.label, m: '已撤销', on: () => agentPanel(a) })) }
  ];
  const host = pageShell('#/', '执行节点',
    '查看执行设备的在线状态与发布能力。');
  drawPageTree(host, groups);

  const slot = el('div', 'slot');
  const form = el('div', 'p-form');
  const label = el('input'); label.placeholder = '节点名称';
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '签发节点授权';
  go.addEventListener('click', async () => {
    try {
      const r = await api('/agents', 'POST', { label: label.value.trim() || '本机节点' });
      const tok = el('input'); tok.value = r.token; tok.readOnly = true;
      tok.style.minWidth = '420px';
      form.appendChild(tok);
      $('#msg').textContent = '令牌只显示这一次，存进节点的 agent.json。';
    } catch (e) { $('#msg').textContent = e.message; }
  });
  form.append(label, go);
  slot.appendChild(form);
  const panel = el('div'); panel.id = 'recpanel';
  $('#page').append(slot, panel);
}

function agentPanel(a){
  const panel = $('#recpanel');
  if (!panel) return;
  const chs = Object.keys((a.capabilities || {}).channels || {});
  panel.innerHTML = `<div class="sp-body" style="padding-left:0">
    <div class="sp-t">${esc(a.label)}</div>
    <div class="sp-m">最后心跳 ${a.last_seen ? esc(ago(null, a.last_seen * 1000)) : '—'}
      · 状态 ${a.enabled ? '启用' : '已撤销'} · 上报通道 ${chs.length}</div>
    ${chs.length ? `<div class="sp-m">${chs.map(c => esc(c)).join(' · ')}</div>` : ''}
    <div class="sp-a">
      ${a.enabled ? '<button class="act" type="button" id="revokeAgent">撤销节点</button>' : ''}
      <button class="act" type="button" id="closeAgent">收起</button>
    </div>
  </div>`;
  panel.querySelector('#closeAgent').addEventListener('click', () => { panel.innerHTML = ''; });
  const rv = panel.querySelector('#revokeAgent');
  if (rv) rv.addEventListener('click', async () => {
    try { await api('/agents/' + encodeURIComponent(a.id) + '/revoke', 'POST', {}); await route(); }
    catch (e) { $('#msg').textContent = e.message; }
  });
}

async function pageSettings(){
  const me = await api('/me');
  const host = pageShell('#/', '安全',
    '根。本机直连免口令；走隧道才需要口令' + (me.totp_enabled ? ' 与动态码' : '') + '。');
  drawPageTree(host, [
    { name: '口令', color: TR.go,   leaves: [{ t: '已设置', m: '至少 12 位' }] },
    { name: '双因素', color: me.totp_enabled ? TR.go : TR.wait,
      leaves: [{ t: me.totp_enabled ? '已启用' : '未启用', m: me.totp_enabled ? '' : '建议启用' }] }
  ]);

  const box = el('div', 'p-form');
  box.style.marginTop = '10px';
  const cur = el('input'); cur.type = 'password'; cur.placeholder = '当前口令';
  const nw = el('input'); nw.type = 'password'; nw.placeholder = '新口令（≥12 位）';
  const go = el('button', 'act'); go.type = 'button'; go.textContent = '改口令';
  go.addEventListener('click', async () => {
    try { await api('/password', 'POST', { current_password: cur.value, password: nw.value }); $('#msg').textContent = '口令已改。'; }
    catch (e) { $('#msg').textContent = e.message; }
  });
  box.append(cur, nw, go);
  if (!me.totp_enabled){
    const p = el('input'); p.type = 'password'; p.placeholder = '当前口令';
    const gen = el('button', 'act'); gen.type = 'button'; gen.textContent = '生成验证器密钥';
    gen.addEventListener('click', async () => {
      try {
        const r = await api('/totp/setup', 'POST', { password: p.value, code: '' });
        const extra = el('div', 'p-form');
        extra.innerHTML = `<input class="inline" readonly value="${esc(r.secret)}" style="min-width:280px">
          <input class="inline" id="tcode" placeholder="验证器当前验证码">
          <button class="act" type="button" id="totpok">确认启用</button>`;
        $('#page').appendChild(extra);
        extra.querySelector('#totpok').addEventListener('click', async () => {
          try {
            const rr = await api('/totp/confirm', 'POST', { password: p.value, code: extra.querySelector('#tcode').value.trim() });
            $('#msg').textContent = '已启用。恢复码：' + rr.recovery_codes.join('  ');
          } catch (e) { $('#msg').textContent = e.message; }
        });
      } catch (e) { $('#msg').textContent = e.message; }
    });
    box.append(p, gen);
  }
  $('#page').appendChild(box);
}

function showTree(){
  document.body.classList.remove('onpage');
  pageEl.hidden = true;
  canvas.hidden = false;
  load().catch(e => { if(e.name!=='AbortError')$('#scale').textContent = e.message; });
}

function updateAppNav(h){
  const active=h.startsWith('#/j/')?'#/jobs':(h.startsWith('#/c/')||h.startsWith('#/p/'))?'#/':h.split('?')[0];
  $('#app-crumb').textContent=h.startsWith('#/p/')?'平台通道':h.startsWith('#/c/')?'通道设置':h.startsWith('#/j/')?'任务详情':({'#/':'工作台','#/jobs':'发布任务','#/assets':'素材库','#/accounts':'账号','#/agents':'执行节点','#/updates':'通道更新','#/audit':'操作记录','#/settings':'设置'}[active]||'工作台');
  document.querySelectorAll('#app-nav a').forEach(a=>{if(a.getAttribute('href')===active)a.setAttribute('aria-current','page');else a.removeAttribute('aria-current');});
}
addEventListener('keydown',event=>{
  if(event.altKey&&!event.ctrlKey&&!event.metaKey&&/^[1-8]$/.test(event.key)){
    const link=document.querySelectorAll('#app-nav a')[Number(event.key)-1];
    if(link){event.preventDefault();location.hash=link.getAttribute('href');}
  }
});
async function route(){
  viewRequests.abort();viewRequests=new AbortController();
  const h = location.hash || '#/';
  updateAppNav(h);
  if (h.startsWith('#/p/'))return pagePlatform(decodeURIComponent(h.slice(4)));
  if (h.startsWith('#/c/')) return showChannel(decodeURIComponent(h.slice(4)));
  if (h.startsWith('#/j/')) return showJob(decodeURIComponent(h.slice(4)));
  if (h === '#/accounts'||h.startsWith('#/accounts?')) return pageAccounts();
  if (h === '#/agents')   return pageAgents();
  if (h === '#/jobs' || h.startsWith('#/jobs?'))     return pageJobs();
  if (h === '#/assets')   return pageAssets();
  if (h === '#/updates')  return pageUpdates();
  if (h === '#/audit')    return pageAudit();
  if (h === '#/settings') return pageSettings();
  showTree();
}
addEventListener('hashchange', () => route().catch(e => {if(e.name!=='AbortError')showMissing(e.message);}));

let rt;
addEventListener('resize', () => { clearTimeout(rt); rt = setTimeout(fit, 150); });

if (location.hash === '#dbg') {
  const d = el('div');
  d.style.cssText = 'position:fixed;left:8px;bottom:8px;z-index:9;font:11px monospace;padding:4px 7px;background:#000;color:#0f0';
  const u = () => d.textContent = 'view=' + innerHeight + ' scroll=' + root.scrollHeight
    + ' k=' + getComputedStyle(root).getPropertyValue('--k').trim()
    + ' nodes=' + document.querySelectorAll('.leaf').length;
  u(); setTimeout(u, 500); document.body.appendChild(d);
}

async function pagePlatform(id){
  const platform=PLATFORMS.find(([key])=>key===id);if(!platform){showMissing('平台不存在');return;}
  const [channels,accounts]=await Promise.all([api('/channels'),api('/accounts')]);
  const mine=channels.filter(c=>c.platform===id);const implemented=mine.filter(c=>c.capabilities?.implemented);const candidates=mine.filter(c=>!c.capabilities?.implemented);
  const state=c=>c.enabled&&['healthy','degraded'].includes(c.health)?'已就绪':c.health==='broken'?'暂不可用':c.version==='unconfigured'?'待配置':'待核验';
  const row=c=>`<a class="channel-option" href="#/c/${encodeURIComponent(c.id)}"><span class="channel-option-icon">${icon(c.engine==='desktopweb'?'monitor':'send')}</span><span class="channel-option-copy"><strong>${esc(NAME[c.engine]||c.engine)}</strong><span>${c.capabilities?.execution_mode==='desktop_confirmation'?'辅助填写内容，由你在平台页面确认发布':'使用本机引擎执行，需完成账号授权和真实核验'}</span></span><span class="status-badge ${state(c)==='已就绪'?'is-ready':''}">${state(c)}</span><span class="channel-arrow">${icon('chevron-right')}</span></a>`;
  usePage(`<a class="back" href="#/">← 工作台</a><div class="platform-page-heading"><div><p class="eyebrow">PLATFORM CHANNELS</p><h2 class="p-title">${esc(platform[1])}</h2><p class="p-sub">选择适合这次内容的发布方式。</p></div><a class="act primary" href="#/jobs?platform=${encodeURIComponent(id)}&compose=1">${icon('plus')}新建发布</a></div><div class="platform-summary"><span><b>${accounts.filter(a=>a.platform===id).length}</b> 个账号</span><span><b>${implemented.length}</b> 条可选通道</span><a href="#/accounts?platform=${encodeURIComponent(id)}">管理平台账号 ${icon('arrow-up-right')}</a></div><section class="channel-options" aria-label="可用发布方式">${implemented.map(row).join('')}</section>${candidates.length?`<details class="candidate-tools"><summary>查看 ${candidates.length} 个候选工具</summary><p>以下工具尚未集成为可执行通道，保留用于选型与后续接入。</p>${candidates.map(row).join('')}</details>`:''}<p class="platform-note">通道完成真实核验后，才会用于日常自动路由。网页确认通道始终需要你在平台页面确认。</p>`);
}
document.querySelector('.skip-link').addEventListener('click',event=>{event.preventDefault();$('#main-content').focus({preventScroll:true});});
const networkToggle=$('#network-detail-toggle');networkToggle.addEventListener('click',()=>{expandedNetwork=!expandedNetwork;networkToggle.setAttribute('aria-pressed',String(expandedNetwork));networkToggle.textContent=expandedNetwork?'收起通道':'展开通道';load().catch(error=>{if(error.name!=='AbortError')$('#scale').textContent=error.message;});});
const commandDialog=$('#command-palette'),commandInput=$('#command-search');let commandIndex=0;
const commands=[...document.querySelectorAll('#app-nav a')].map((a,i)=>({label:a.getAttribute('aria-label'),href:a.getAttribute('href'),glyph:a.dataset.icon,shortcut:'Alt '+(i+1)}));commands.unshift({label:'新建发布',href:'#/jobs?compose=1',glyph:'plus',shortcut:''});
function renderCommands(){const query=commandInput.value.trim().toLowerCase();const matches=commands.filter(c=>c.label.toLowerCase().includes(query));commandIndex=Math.min(commandIndex,Math.max(0,matches.length-1));if(matches.length)commandInput.setAttribute('aria-activedescendant','command-option-'+commandIndex);else commandInput.removeAttribute('aria-activedescendant');$('#command-results').innerHTML=matches.length?matches.map((c,i)=>`<a id="command-option-${i}" role="option" aria-selected="${i===commandIndex}" href="${c.href}" data-command-index="${i}">${icon(c.glyph)}<span>${c.label}</span><kbd>${c.shortcut}</kbd></a>`).join(''):'<p class="command-empty">没有匹配的页面或操作</p>';}
commandDialog.addEventListener('close',()=>commandInput.setAttribute('aria-expanded','false'));
function openCommands(){commandInput.setAttribute('aria-expanded','true');commandInput.value='';commandIndex=0;renderCommands();commandDialog.showModal();commandInput.focus();}
document.querySelectorAll('[data-open-command]').forEach(button=>button.addEventListener('click',openCommands));commandInput.addEventListener('input',()=>{commandIndex=0;renderCommands();});commandDialog.addEventListener('click',e=>{if(e.target.closest('[data-command-index]'))commandDialog.close();if(e.target===commandDialog)commandDialog.close();});
commandInput.addEventListener('keydown',e=>{const options=[...$('#command-results').querySelectorAll('a')];if(e.key==='ArrowDown'||e.key==='ArrowUp'){e.preventDefault();commandIndex=(commandIndex+(e.key==='ArrowDown'?1:options.length-1))%Math.max(1,options.length);renderCommands();}if(e.key==='Enter'&&options[commandIndex]){e.preventDefault();location.hash=options[commandIndex].getAttribute('href');commandDialog.close();}});
addEventListener('keydown',e=>{if((e.ctrlKey||e.metaKey)&&e.key.toLowerCase()==='k'){e.preventDefault();if(commandDialog.open)commandDialog.close();else openCommands();}});

start();
setInterval(async()=>{if(document.hidden||!CSRF)return;try{if(!location.hash||location.hash==='#/'||location.hash.startsWith('#/?'))await load();else if(location.hash.startsWith('#/j/')&&window.__jobView){const prev=window.__jobView;const j=await api('/jobs/'+encodeURIComponent(prev.id));if((j.state!==prev.state||j.reason!==prev.reason||j.attempts.length!==prev.attempts)&&!(document.activeElement&&document.activeElement.matches('input,textarea,select')))await route();}}catch(e){if(e.status===401){const ok=await bootstrap();if(!ok)$('#unlock').hidden=false;}}},10000);
/* 自检钩子：?audit=1 时把 #page 内的可控件数量写进标题，供无人值守核对 */
if (location.search.indexOf('audit=1') >= 0) {
  setTimeout(() => {
    const p = document.querySelector('#page');
    const n = sel => (p ? p.querySelectorAll(sel).length : 0);
    document.title = 'AUDIT in=' + n('input') + ' sel=' + n('select') + ' btn=' + n('button')
      + ' leaf=' + n('.pleaf') + ' click=' + n('[style*="pointer"]')
      + ' slot=' + n('.slot') + ' hidden=' + (p ? (p.hidden ? 1 : 0) : -1);
  }, 1200);
}

if(window.chrome && window.chrome.webview){
  window.chrome.webview.addEventListener('message',async e=>{
    if(e.data.type==='browser-job-finished'){await route();return;}
    if(e.data.type==='login-finished'){
      const msg=$('#msg');if(msg)msg.textContent='登录窗口已结束。浏览器通道会保存账号授权；其他通道请点击「导入登录态」。';
    }else if(e.data.type==='login-error'){const msg=$('#msg');if(msg)msg.textContent='登录未完成，请重新扫码。';}
  });
}
})();
