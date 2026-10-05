// content.js 가 보낸 진행 상황을 맥 수신기(listener.py)의 로컬 로그 서버로 넘긴다.
// 페이지에서 바로 localhost 로 보내면 브라우저 보안 정책에 막혀서 백그라운드를 거친다.
chrome.runtime.onMessage.addListener((msg) => {
  if (!msg || !msg.log) return;
  fetch("http://127.0.0.1:8789/log", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ log: msg.log }),
  }).catch(() => {}); // 수신기가 꺼져 있어도 진행은 계속
});
