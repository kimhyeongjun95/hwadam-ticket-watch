// 화담숲 자동 진행 중 NOL 로그인이 풀려 있으면 content.js 가 NOL 로그인 화면으로 보낸다.
// 그때만 '네이버로 시작하기'를 눌러 준다. 크롬에 네이버 로그인이 돼 있으면 바로 상품 페이지로 돌아와 이어 가고,
// 네이버 로그인 화면이 뜨면 naver.js 가 이어 받는다.
// 로그인 화면 버튼: <button><img alt="NAVER_Positive">네이버로 시작하기</button>
(async () => {
  const onLoginPage = () => /^\/v3\/login\/?$/.test(location.pathname);
  if (!onLoginPage()) return;
  const { pending } = await chrome.storage.local.get("pending");
  if (!pending?.loginTried || pending.naverClicked || Date.now() - pending.at > 60e3) return;
  // 로그인이 실패해 이 화면으로 다시 와도 또 누르며 맴돌지 않게 한 번만
  await chrome.storage.local.set({ pending: { ...pending, naverClicked: true } });

  const log = (text) => {
    console.log("[hwadam-auto]", text);
    // '직접 로그인' 해야 하면 자동 진행이 멈춘 것 → 맥 알림
    try { chrome.runtime.sendMessage({ log: text, done: /직접 로그인/.test(text) ? "fail" : undefined }); } catch (_) {}
  };
  const visible = (e) => !!(e && (e.offsetWidth || e.offsetHeight));
  const naver = () => [...document.querySelectorAll("button")]
    .find((b) => visible(b) && (b.querySelector('img[alt^="NAVER"]') || /네이버로/.test(b.textContent)));

  log("NOL 로그인 화면에서 '네이버로 시작하기' 누르는 중…");
  // React 가 붙기 전에는 눌러도 반응이 없어서 화면이 넘어갈 때까지 1초마다 다시 누른다
  for (const end = Date.now() + 15000; Date.now() < end && onLoginPage(); ) {
    naver()?.click();
    await new Promise((r) => setTimeout(r, 1000));
  }
  if (onLoginPage()) log("'네이버로 시작하기'를 못 눌렀어요. 직접 로그인 후 진행해 주세요.");
})();
