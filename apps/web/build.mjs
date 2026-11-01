// 免构建：把 apps/web 的三个静态文件同步到 omnidispatch/static。
// 用法：node build.mjs
// 每次构建会给 index.html 里的 ?__V__ 打上新时间戳，浏览器不会吃到旧 app.js。
import { readFileSync, writeFileSync, mkdirSync, rmSync, existsSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { dirname, join } from 'node:path';

const here = dirname(fileURLToPath(import.meta.url));
const out = join(here, '..', '..', 'omnidispatch', 'static');
const stamp = Date.now().toString(36);

mkdirSync(out, { recursive: true });
// 旧的 Vite 产物不再使用，清掉避免混淆
for (const stale of ['assets']) {
  const p = join(out, stale);
  if (existsSync(p)) rmSync(p, { recursive: true, force: true });
}

for (const f of ['index.html', 'app.css', 'app.js']) {
  let buf = readFileSync(join(here, f));
  if (f === 'index.html') {
    buf = Buffer.from(buf.toString('utf8').replaceAll('__V__', stamp), 'utf8');
  }
  writeFileSync(join(out, f), buf);
  console.log('→', join(out, f));
}
console.log('build', stamp);
