// content.js 가 보낸 진행 상황을 맥 수신기(listener.py)의 로컬 로그 서버로 넘긴다.
// 페이지에서 바로 localhost 로 보내면 브라우저 보안 정책에 막혀서 백그라운드를 거친다.
function log(text) {
  fetch("http://127.0.0.1:8789/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ log: text }),
  }).catch(() => {}); // 수신기가 꺼져 있어도 진행은 계속
}

// 크롬 디버거로 진짜 마우스 클릭을 보낸다 (naver.js). 자동완성된 비밀번호는 이런 사람의 입력이 있어야 페이지에 넘어간다.
async function trustedClick(tabId, selector) {
  const target = { tabId };
  await chrome.debugger.attach(target, "1.3");
  try {
    await new Promise((r) => setTimeout(r, 300)); // '디버깅 중' 안내 줄이 뜨며 화면이 밀린 뒤에 위치를 잰다
    const { result } = await chrome.debugger.sendCommand(target, "Runtime.evaluate", {
      expression: `(() => {
        const e = document.querySelector(${JSON.stringify(selector)});
        if (!e) return null;
        e.scrollIntoView({ block: "center" });
        const r = e.getBoundingClientRect();
        return { x: r.left + r.width / 2, y: r.top + r.height / 2 };
      })()`,
      returnByValue: true,
    });
    const at = result.value;
    if (!at) throw new Error(`${selector} 없음`);
    const send = (params) => chrome.debugger.sendCommand(target, "Input.dispatchMouseEvent", { ...at, ...params });
    await send({ type: "mouseMoved", button: "none" });
    await send({ type: "mousePressed", button: "left", clickCount: 1 });
    await send({ type: "mouseReleased", button: "left", clickCount: 1 });
  } finally {
    await chrome.debugger.detach(target).catch(() => {});
  }
}

chrome.runtime.onMessage.addListener((msg, sender) => {
  if (msg?.log) log(msg.log);
  if (msg?.trustedClick && sender.tab) {
    trustedClick(sender.tab.id, msg.trustedClick).catch((e) => log(`클릭 실패: ${e.message}. 직접 진행해 주세요.`));
  }
});
