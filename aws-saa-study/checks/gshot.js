// 사용: node checks/gshot.js <dist/gallery.html> <outdir> [prefix...]
// 그림 갤러리에서 id가 prefix로 시작하는 그림(정식·비유)을 데스크톱 밝은 테마로 찍는다.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, out, ...pre] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const fonts = '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;600;700&family=Gowun+Dodum&display=swap">';
  const html = '<!doctype html><html><head><meta charset=utf8>' + fonts + '</head><body>' + fs.readFileSync(src, 'utf8') + '</body></html>';
  const tmp = path.join(out, '_gallery.html'); fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  const ctx = await b.newContext({ viewport: { width: 760, height: 900 }, deviceScaleFactor: 1 });
  const p = await ctx.newPage();
  await p.goto('file://' + tmp); await p.waitForTimeout(2500);
  const secs = await p.$$('section');
  for (const s of secs) {
    const id = await s.$eval('h3', e => e.textContent);
    if (pre.length && !pre.some(x => id.startsWith(x))) continue;
    await s.screenshot({ path: `${out}/${id.replace(/[^a-z0-9]+/gi, '_')}.png` });
  }
  await b.close();
})();
