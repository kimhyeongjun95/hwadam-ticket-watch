// 화담숲 자동 진행 중 '네이버로 시작하기'(login.js)를 눌렀는데 네이버 로그인 화면이 뜨면,
// 크롬이 비밀번호를 자동완성해 둔 경우에만 '로그인'을 눌러 준다. 비밀번호는 읽지도 넣지도 않는다.
// 자동완성된 비밀번호는 사람이 화면을 건드리기 전까지 페이지에 빈 값으로 보여서 click() 으로는 빈 비밀번호가 간다.
// 그래서 background.js 가 크롬 디버거로 사람이 누른 것과 같은 클릭을 보낸다 (그동안 '디버깅 중' 안내 줄이 잠깐 뜬다).
(async () => {
  const pw = document.getElementById("pw");
  if (!pw) return; // 로그인 화면이 아님
  const { pending } = await chrome.storage.local.get("pending");
  if (!pending?.naverClicked || pending.naverLoginClicked || Date.now() - pending.at > 90e3) return;
  // 로그인이 실패해 이 화면이 다시 떠도 또 누르며 맴돌지 않게 한 번만
  await chrome.storage.local.set({ pending: { ...pending, naverLoginClicked: true } });

  const log = (text) => {
    console.log("[hwadam-auto]", text);
    // '직접 로그인' 해야 하면 자동 진행이 멈춘 것 → 맥 알림
    try { chrome.runtime.sendMessage({ log: text, done: /직접 로그인/.test(text) ? "fail" : undefined }); } catch (_) {}
  };
  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const visible = (e) => !!(e && (e.offsetWidth || e.offsetHeight));

  // 크롬 자동완성은 화면이 뜨고 조금 뒤에 채워진다
  const filled = () => pw.matches(":-webkit-autofill");
  for (const end = Date.now() + 5000; !filled() && Date.now() < end; ) await sleep(200);
  if (!filled()) return log("네이버 로그인 화면이 떴는데 비밀번호가 자동완성 안 돼 있어요. 직접 로그인해 주세요.");
  if ([...document.querySelectorAll('[id*="captcha" i]')].some(visible)) {
    return log("네이버가 자동입력 방지 문자를 물어봐요. 직접 로그인해 주세요.");
  }

  // 화면 폭에 따라 #loginBtn_column / #loginBtn_row 중 하나만 보인다
  const btn = ["loginBtn_column", "loginBtn_row"].map((id) => document.getElementById(id)).find(visible)
    || [...document.querySelectorAll("button")].find((e) => visible(e) && e.textContent.trim() === "로그인");
  if (!btn) return log("네이버 '로그인' 버튼을 못 찾았어요. 직접 로그인해 주세요.");
  btn.setAttribute("data-hwadam-click", "");
  log("네이버 로그인 화면에서 자동완성된 계정으로 '로그인' 누르는 중…");
  chrome.runtime.sendMessage({ trustedClick: "[data-hwadam-click]" });
})();
