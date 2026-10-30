// content.js 가 보낸 진행 상황을 맥 수신기(listener.py)의 로컬 로그 서버로 넘긴다.
// 페이지에서 바로 localhost 로 보내면 브라우저 보안 정책에 막혀서 백그라운드를 거친다.
// done 이 있으면 끝났다는 뜻: "ok" 면 수신기가 크롬을 앞으로 띄우고, "fail" 이면 알림만 띄운다.
// show 면 끝나진 않았지만 창이 보여야 해서 크롬을 앞으로 띄운다
function log(text, done, show) {
  return fetch("http://127.0.0.1:8789/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ log: text, done, show }),
  }).catch(() => {}); // 수신기가 꺼져 있어도 진행은 계속
}

// 수신기가 내려(최소화) 둔 창은 한 번도 안 그려져서 네이버 로그인 클릭이 안 먹는다 (10/26·10/30).
// 로그인 때만은 창을 올리고 크롬을 앞으로 띄운 뒤 그려질 때까지 잠깐 기다린다
async function showForLogin(windowId) {
  const w = await chrome.windows.get(windowId);
  if (w.state !== "minimized") return;
  await chrome.windows.update(windowId, { state: "normal", focused: true });
  await log("네이버 로그인은 창이 보여야 눌려서 크롬을 앞으로 띄워요.", undefined, true);
  await new Promise((r) => setTimeout(r, 1000));
}

// 크롬 디버거로 사람이 누른 것과 같은 클릭을 보낸다 (naver.js). 자동완성된 비밀번호는 사람의 입력이 있어야 페이지에 넘어간다.
// 먼저 진짜 마우스 클릭을 보내는데, 화면이 꺼져 있거나 창이 가려져 한 번도 안 그려진 페이지에서는 마우스 입력이 오류 없이 버려진다
// (10/14 12:56 화면 꺼진 사이 그래서 로그인을 못 함). 그러면 userGesture 로 click() 한다 — 사람의 입력으로 쳐서 비밀번호도 넘어간다.
async function trustedClick(tabId, selector) {
  const target = { tabId };
  const cmd = (method, params) => Promise.race([
    chrome.debugger.sendCommand(target, method, params),
    new Promise((_, fail) => setTimeout(() => fail(new Error(`${method} 응답 없음`)), 3000)),
  ]);
  const find = `document.querySelector(${JSON.stringify(selector)})`;
  await chrome.debugger.attach(target, "1.3");
  try {
    await new Promise((r) => setTimeout(r, 300)); // '디버깅 중' 안내 줄이 뜨며 화면이 밀린 뒤에 위치를 잰다
    const { result } = await cmd("Runtime.evaluate", {
      expression: `(() => {
        const e = ${find};
        if (!e) return null;
        e.scrollIntoView({ block: "center" });
        window.__hwadamHit = false;
        addEventListener("mousedown", (ev) => { window.__hwadamHit = e.contains(ev.target); }, { capture: true, once: true });
        const r = e.getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      })()`,
      returnByValue: true,
    });
    const at = result.value;
    if (!at) throw new Error(`${selector} 없음`);
    // mouseMoved 는 안 보이는 페이지에서 5초씩 멈춰서 보내지 않는다
    const send = (params) => cmd("Input.dispatchMouseEvent", { ...at, ...params });
    await send({ type: "mousePressed", button: "left", clickCount: 1 });
    await send({ type: "mouseReleased", button: "left", clickCount: 1 });
    // 눌려서 벌써 다음 페이지로 넘어갔으면 값이 없거나 읽기가 실패한다 → 들어간 것
    const hit = await cmd("Runtime.evaluate", { expression: "window.__hwadamHit", returnByValue: true }).catch(() => null);
    if (hit?.result?.value === false) {
      log("화면이 꺼져 있거나 창이 가려져 마우스 클릭이 안 들어가서 바로 눌러요.");
      await cmd("Runtime.evaluate", { expression: `${find}.click()`, userGesture: true });
    }
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
}

chrome.runtime.onMessage.addListener((msg, sender) => {
  // 수신기는 창을 내려(최소화) 둔 채 진행시킨다. 주문서가 뜨면 그 창을 올리고 수신기가 크롬을 앞으로 띄운다
  if (msg?.done === "ok" && sender.tab) {
    chrome.windows.update(sender.tab.windowId, { state: "normal", focused: true })
      .catch(() => {}).then(() => log(msg.log, "ok"));
  } else if (msg?.log) log(msg.log, msg.done);
  if (msg?.trustedClick && sender.tab) {
    showForLogin(sender.tab.windowId).catch(() => {})
      .then(() => trustedClick(sender.tab.id, msg.trustedClick))
      .catch((e) => log(`클릭 실패: ${e.message}. 직접 진행해 주세요.`));
  }
});
