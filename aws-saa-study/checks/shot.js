// 사용: node checks/shot.js <dist/index.html> <outdir> [selector...]
// Artifact 껍데기(charset, viewport)로 감싸 폰(375)·데스크톱(1280), 밝은·어두운 테마 스크린샷을 찍는다.
const { chromium } = require('playwright');
const fs = require('fs'), path = require('path');
(async () => {
  const [src, out, ...sels] = process.argv.slice(2);
  fs.mkdirSync(out, { recursive: true });
  const html = '<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1,viewport-fit=cover"><style>:root{color-scheme:light;box-sizing:border-box}body{margin:0}</style></head><body>' + fs.readFileSync(src, 'utf8') + '</body></html>';
  const tmp = path.join(out, '_page.html'); fs.writeFileSync(tmp, html);
  const b = await chromium.launch();
  for (const [w, h, tag] of [[375, 812, 'phone'], [1280, 900, 'desk']]) {
    for (const scheme of ['light', 'dark']) {
      const ctx = await b.newContext({ viewport: { width: w, height: h }, colorScheme: scheme, deviceScaleFactor: w < 500 ? 2 : 1 });
      const p = await ctx.newPage();
      await p.goto('file://' + tmp); await p.waitForTimeout(1500);
      const sw = await p.evaluate(() => [document.documentElement.scrollWidth, document.documentElement.clientWidth]);
      console.log(tag, scheme, 'scrollWidth', sw);
      await p.screenshot({ path: `${out}/${tag}-${scheme}-top.png` });
      for (const s of sels) {
        const el = await p.$(s); if (!el) { console.log('no', s); continue; }
        await el.evaluate(e => { if (e.tagName === 'DETAILS') e.open = true; e.querySelectorAll('details').forEach(d => d.open = true); });
        // 긴 주제는 앞부분 2,400px만 찍는다(요소 전체·전체 페이지 캡처는 시간 초과가 남).
        await p.setViewportSize({ width: w, height: 2400 });
        await el.evaluate(e => e.scrollIntoView({ block: 'start', behavior: 'instant' })); await p.waitForTimeout(400);
        const bb = await el.boundingBox();
        await p.screenshot({ path: `${out}/${tag}-${scheme}-${s.replace(/[^a-z0-9]+/gi, '_')}.png`,
          clip: { x: bb.x, y: Math.max(0, bb.y), width: bb.width, height: Math.min(bb.height, 2400 - Math.max(0, bb.y)) } });
        await p.setViewportSize({ width: w, height: h });
      }
      await ctx.close();
    }
  }
  await b.close();
})();
