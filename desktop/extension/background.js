// content.js 가 보낸 진행 상황을 맥 수신기(listener.py)의 로컬 로그 서버로 넘긴다.
// 페이지에서 바로 localhost 로 보내면 브라우저 보안 정책에 막혀서 백그라운드를 거친다.
// done 이 있으면 끝났다는 뜻: "ok"(주문서 뜸)·"dry"(시험 끝) 면 수신기가 크롬을 앞으로 띄우고, "fail" 이면 알림만 띄운다.
// "soldout"(품절 등 살 게 없음) 이면 수신기는 알리지 않고, 새 창이었으면 여기서 닫는다 (대기 창은 content.js 가 새로 읽어 다시 대기).
// show 면 끝나진 않았지만 창이 보여야 해서 크롬을 앞으로 띄운다
function log(text, done, show, standby) {
  return fetch("http://127.0.0.1:8789/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ log: text, done, show, standby }),
  }).catch(() => {}); // 수신기가 꺼져 있어도 진행은 계속
}

// 수신기가 내려(최소화) 둔 창은 한 번도 안 그려져서 네이버 로그인 마우스 클릭이 안 먹는다 (10/26·10/30).
// 키보드 로그인(trustedEnter)이 안 됐을 때만 창을 올리고 크롬을 앞으로 띄운 뒤 그려질 때까지 잠깐 기다린다
async function showForLogin(windowId) {
  const w = await chrome.windows.get(windowId);
  if (w.state !== "minimized") return;
  await chrome.windows.update(windowId, { state: "normal", focused: true });
  await log("네이버 로그인은 창이 보여야 눌려서 크롬을 앞으로 띄워요.", undefined, true);
  await sleep(1000);
}

const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
const debuggerCmd = (target) => (method, params) => Promise.race([
  chrome.debugger.sendCommand(target, method, params),
  new Promise((_, fail) => setTimeout(() => fail(new Error(`${method} 응답 없음`)), 3000)),
]);

// 네이버 로그인을 크롬 디버거의 키보드 입력으로 한다 (naver.js). 마우스 입력은 화면 위 위치로 들어가서 안 그려진 숨은 창에서는 버려지지만,
// 키보드 입력은 포커스된 칸으로 바로 가서 숨은 창에서도 들어간다. 사람의 입력이라 자동완성된 비밀번호도 페이지에 넘어온다.
// 비밀번호 칸에서 End 를 눌러 비밀번호가 보이면 Enter 로 로그인하고, 다음 화면으로 넘어갔으면 true.
// 비밀번호가 안 보이면 빈 비밀번호로 보내지 않고 false (그러면 창을 띄워 마우스로 누른다)
async function trustedEnter(tabId, selector) {
  const target = { tabId };
  const cmd = debuggerCmd(target);
  const find = `document.querySelector(${JSON.stringify(selector)})`;
  await chrome.debugger.attach(target, "1.3");
  try {
    await cmd("Emulation.setFocusEmulationEnabled", { enabled: true }); // 창이 숨어 있어도 페이지가 포커스를 가진 것처럼
    const { result } = await cmd("Runtime.evaluate", { expression: `(() => { const e = ${find}; if (!e) return null; e.focus(); return location.href; })()`, returnByValue: true });
    const here = result.value;
    if (!here) throw new Error(`${selector} 없음`);
    const key = async (key, code, keyCode, text) => {
      await cmd("Input.dispatchKeyEvent", { type: text ? "keyDown" : "rawKeyDown", key, code, windowsVirtualKeyCode: keyCode, text });
      await cmd("Input.dispatchKeyEvent", { type: "keyUp", key, code, windowsVirtualKeyCode: keyCode });
    };
    await key("End", "End", 35);
    let filled = false;
    for (let i = 0; i < 10 && !filled; i++) {
      await sleep(100);
      filled = (await cmd("Runtime.evaluate", { expression: `!!${find}?.value`, returnByValue: true })).result.value;
    }
    if (!filled) return false;
    await key("Enter", "Enter", 13, "\r");
    for (let i = 0; i < 20; i++) {
      await sleep(250);
      const now = await cmd("Runtime.evaluate", { expression: "location.href", returnByValue: true }).catch(() => null);
      if (now?.result?.value !== here) return true; // 넘어가는 중이면 읽기가 실패하거나 주소가 바뀐다
    }
    return false;
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
}

// 크롬 디버거로 사람이 누른 것과 같은 클릭을 보낸다 (trustedEnter 가 안 됐을 때, 창을 띄운 뒤). 자동완성된 비밀번호는 사람의 입력이 있어야 페이지에 넘어간다.
// 먼저 진짜 마우스 클릭을 보내는데, 화면이 꺼져 있거나 창이 가려져 한 번도 안 그려진 페이지에서는 마우스 입력이 오류 없이 버려진다
// (10/14 12:56 화면 꺼진 사이 그래서 로그인을 못 함). 그러면 userGesture 로 click() 한다 — 사람의 입력으로 쳐서 비밀번호도 넘어간다.
async function trustedClick(tabId, selector) {
  const target = { tabId };
  const cmd = debuggerCmd(target);
  const find = `document.querySelector(${JSON.stringify(selector)})`;
  await chrome.debugger.attach(target, "1.3");
  try {
    await sleep(300); // '디버깅 중' 안내 줄이 뜨며 화면이 밀린 뒤에 위치를 잰다
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

// 키보드 Enter 로 먼저 해 보고, 안 되면 창을 띄워 마우스로 '로그인'을 누른다
async function naverLogin(tab, msg) {
  const ok = await trustedEnter(tab.id, msg.trustedEnter).catch((e) => {
    log(`키보드 로그인 실패: ${e.message}`);
    return false;
  });
  if (ok) return log("키보드로 네이버 로그인을 눌렀어요.");
  await log("키보드로는 로그인이 안 돼서 마우스로 눌러요.");
  await showForLogin(tab.windowId).catch(() => {});
  await trustedClick(tab.id, msg.trustedClick);
}

// 대기 창(content.js)이 연결해 오면 수신기에 알림이 오길 기다렸다가(/standby/wait, 20초씩) 그 창에 넘기고 받았다고 알린다.
// 서비스 워커는 확장 API 를 30초 동안 안 부르면 꺼지니 매번 하나 부른다
chrome.runtime.onConnect.addListener((port) => {
  if (port.name !== "standby") return;
  let alive = true;
  port.onDisconnect.addListener(() => { alive = false; });
  // 크롬이 메모리 아끼려고 오래 안 본 탭을 비우면 대기 창이 죽는다
  if (port.sender?.tab) chrome.tabs.update(port.sender.tab.id, { autoDiscardable: false }).catch(() => {});
  // 지금 대기 중인 창을 기억해 둔다 (새로 띄울 때 옛 창을 닫으려고). 품절로 멈춰 새로 읽은 창도 여기서 다시 대기 창이 된다
  if (port.sender?.tab) chrome.storage.local.set({ standbyWindow: port.sender.tab.windowId });
  (async () => {
    while (alive) {
      await chrome.runtime.getPlatformInfo();
      try {
        const r = await fetch("http://127.0.0.1:8789/standby/wait");
        if (r.status !== 200 || !alive) continue;
        chrome.storage.local.remove("standbyWindow"); // 이제 주문하러 가는 창이다
        port.postMessage(await r.json());
        fetch("http://127.0.0.1:8789/standby/ack", { method: "POST" }).catch(() => {});
      } catch (_) {
        await sleep(5000); // 수신기가 꺼져 있음
      }
    }
  })();
});

// 품절 등으로 멈춘 창을 닫는다. Dock 에 내려가 있고 탭이 하나뿐일 때만 (사람이 올려 보고 있거나 다른 탭을 열었으면 둔다)
async function closeIfHidden(windowId) {
  const w = await chrome.windows.get(windowId, { populate: true });
  if (w.state === "minimized" && w.tabs.length === 1) await chrome.windows.remove(windowId);
}

chrome.runtime.onMessage.addListener((msg, sender) => {
  // 수신기는 창을 내려(최소화) 둔 채 진행시킨다. 주문서가 뜨면 그 창을 올리고 수신기가 크롬을 앞으로 띄운다
  if ((msg?.done === "ok" || msg?.done === "dry") && sender.tab) {
    chrome.windows.update(sender.tab.windowId, { state: "normal", focused: true })
      .catch(() => {}).then(() => log(msg.log, msg.done));
  } else if (msg?.done === "soldout" && sender.tab) {
    log(msg.log, msg.done, undefined, msg.standby).then(() => msg.standby || closeIfHidden(sender.tab.windowId)).catch(() => {});
  } else if (msg?.log) log(msg.log, msg.done);
  if (msg?.trustedClick && sender.tab) {
    naverLogin(sender.tab, msg).catch((e) => log(`클릭 실패: ${e.message}. 직접 진행해 주세요.`));
  }
});

// 대기 창은 여기서 띄운다. 수신기가 AppleScript 로 띄우면 창이 화면에 떴다가 Dock 으로 내려가고 앱이 바뀌어서 (11/2),
// 크롬 API 로 처음부터 내린(최소화) 채, 앞으로 나오지 않게 연다. 30초마다 수신기에 띄워야 하는지 묻는다
const PRODUCT = "https://leisure-web.yanolja.com/leisure/10367229";
async function checkStandby() {
  let need;
  try {
    const r = await fetch("http://127.0.0.1:8789/standby/need");
    if (r.status !== 200) return;
    need = await r.json();
  } catch (_) {
    return; // 수신기가 꺼져 있음
  }
  if (need.reload) return chrome.runtime.reload(); // 확장 파일을 고쳤을 때 수신기가 새로 읽힌다 (listener.py --reload-extension)
  try {
    const { standbyWindow } = await chrome.storage.local.get("standbyWindow");
    const old = standbyWindow && (await chrome.windows.get(standbyWindow, { populate: true }).catch(() => null));
    if (old && old.state !== "minimized") return log("대기 창을 사람이 보고 있어서 새로 띄우지 않아요."); // 그대로 둔다
    // 알림을 못 받게 된 옛 대기 창 (확장을 새로 읽었거나 로그인하다 막힘) 은 닫는다
    if (old && old.tabs.length === 1) await chrome.windows.remove(old.id).catch(() => {});
    // 옵션 창이 휴대폰 폭에서만 열려서 폭을 정해 뒤에(focused: false — 앞 앱이 안 바뀜) 연 뒤 바로 내린다.
    // 처음부터 내린 채 만들면 폭을 못 정하고, 내린 창 크기를 바꾸면 다시 올라온다 (11/2)
    const w = await chrome.windows.create({ url: need.url, focused: false, left: 60, top: 40, width: 480, height: 940 });
    await chrome.windows.update(w.id, { state: "minimized" });
    await chrome.storage.local.set({ standbyWindow: w.id });
    const after = await chrome.windows.get(w.id).catch(() => null);
    log(`대기 창 띄움 (${after?.state} ${after?.width}x${after?.height})`);
  } catch (e) {
    log(`대기 창 띄우기 실패: ${e.message}`);
  }
}
chrome.alarms.create("standby", { periodInMinutes: 0.5 });
chrome.alarms.onAlarm.addListener((a) => { if (a.name === "standby") checkStandby(); });
checkStandby(); // 확장이 (새로) 뜰 때도 바로 한 번
