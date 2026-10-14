// 화담숲 상품 페이지가 #hwadam-auto=날짜_시간_매수 를 달고 열리면
// 날짜 → 회차 → 입장권 성인 → 일반 → 매수 → 구매하기 순서로 눌러 주문서를 띄운다. 결제는 사람이 한다.
// 끝에 _dry 를 붙이면 구매하기 직전에 멈춘다 (시험용).
// 사이트가 뜨면서 주소의 # 부분을 지워 버려서, 페이지 스크립트보다 먼저(document_start) 읽어 둔다.
// NOL 로그인이 풀려 있으면 네이버로 로그인하러 갔다가(login.js) 돌아와서 이어 간다.
(() => {
  const SPEC = /^#hwadam-auto=(\d{4})-(\d{2})-(\d{2})_(\d{2}:\d{2})_(\d+)(_dry)?$/;
  const fromHash = SPEC.test(location.hash) ? location.hash : null;
  // 새로고침해도 다시 돌지 않게 표시를 지운다
  if (fromHash) history.replaceState(null, "", location.pathname + location.search);

  const banner = document.createElement("div");
  banner.style.cssText =
    "position:fixed;top:12px;left:50%;transform:translateX(-50%);z-index:2147483647;" +
    "padding:10px 16px;border-radius:10px;background:#1f2937;color:#fff;font:600 14px/1.4 sans-serif;" +
    "box-shadow:0 4px 16px rgba(0,0,0,.3);max-width:90vw";
  const say = (text, color) => {
    banner.textContent = `화담숲 자동 진행: ${text}`;
    if (color) banner.style.background = color;
    if (!banner.isConnected && document.body) document.body.appendChild(banner);
    console.log("[hwadam-auto]", text);
    // 맥 수신기 로그에도 남긴다 (background.js 가 localhost 로 전달)
    try { chrome.runtime.sendMessage({ log: text }); } catch (_) {}
  };
  // 단계마다 페이지를 열기 시작한 뒤 몇 초째인지 적어 두고 끝날 때 로그에 붙인다 (어디가 느린지 보려고)
  const laps = [];
  const lap = (name) => laps.push(`${name} ${(performance.now() / 1000).toFixed(1)}`);
  const took = () => (laps.length ? ` [초: ${laps.join(" · ")}]` : "");
  const stop = (text) => { say(text + took(), "#b91c1c"); throw new Error(text); };

  const sleep = (ms) => new Promise((r) => setTimeout(r, ms));
  const visible = (e) => !!(e && (e.offsetWidth || e.offsetHeight));
  const text = (e) => (e.textContent || "").trim().replace(/\s+/g, " ");
  // find() 가 무언가를 돌려줄 때까지 기다린다 (ms 가 지나면 null). 화면(DOM)이 바뀔 때마다 바로 다시 본다.
  // 타이머로 자주 보면 창이 안 보일 때 크롬이 타이머를 1초에 한 번으로 늦춰서 단계마다 1초씩 걸린다.
  function until(find, ms) {
    return new Promise((resolve) => {
      let timer;
      const obs = new MutationObserver(() => check());
      const finish = (el) => { obs.disconnect(); clearTimeout(timer); resolve(el); };
      const check = () => { const el = find(); if (el) finish(el); return el; };
      if (check()) return;
      obs.observe(document.documentElement, { subtree: true, childList: true, attributes: true, characterData: true });
      timer = setTimeout(() => finish(find() || null), ms);
    });
  }
  async function waitFor(find, what, ms = 10000) {
    return (await until(find, ms)) || stop(`${what}을(를) 찾지 못했어요. 직접 진행해 주세요.`);
  }
  const buttons = (sel = "button") => [...document.querySelectorAll(sel)].filter(visible);
  // 막 그려진 달력·회차는 재고를 받아오기 전이거나 (창이 안 보여) 늦게 그려져 잠깐 막혀 보일 수 있어서,
  // 막혀 있으면 2초까지 다시 보고 판단한다. 진짜 품절이면 2초 늦게 멈출 뿐
  async function settle(find, ok, ms = 2000) {
    return (await until(() => { const e = find(); return e && ok(e) ? e : null; }, ms)) || find();
  }

  async function run() {
    // 로그인하러 다녀오는 사이 # 이 없어질 수 있어 진행할 회차를 저장소에 맡겨 둔다 (3분 안에 돌아와야 유효)
    const { pending } = await chrome.storage.local.get("pending");
    const resumed = pending && Date.now() - pending.at < 3 * 60e3 ? pending : null;
    const spec = fromHash || resumed?.spec;
    if (!spec) return;
    const loginTried = resumed?.spec === spec && resumed.loginTried;
    if (pending) await chrome.storage.local.remove("pending");
    const [, y, mo, d, time, qtyText, dry] = spec.match(SPEC);
    const qty = Number(qtyText);

    if (document.readyState === "loading") await new Promise((r) => document.addEventListener("DOMContentLoaded", r, { once: true }));
    lap("화면");
    say(`${Number(mo)}/${Number(d)} ${time} 성인 ${qty}장 고르는 중…`);

    // 0. 로그인 확인. 풀려 있으면 NOL 로그인 화면으로 보내고, 거기서 login.js 가 '네이버로 시작하기'를 누른다.
    //    로그인이 끝나면 돌아올 주소에 # 을 붙여 둬서 이 페이지로 돌아와 이어 간다.
    let loggedIn = true; // 못 읽으면 일단 진행 (안 돼 있으면 구매 단계에서 로그인 창이 뜬다)
    try {
      loggedIn = JSON.parse(document.getElementById("__NEXT_DATA__").textContent).props.pageProps.isLoggedIn;
    } catch (_) {}
    if (!loggedIn) {
      if (loginTried) stop("네이버로 로그인했는데도 NOL 로그인이 안 됐어요. 직접 로그인 후 진행해 주세요.");
      say("NOL 로그인이 풀려 있어 네이버로 로그인하는 중…");
      await chrome.storage.local.set({ pending: { spec, at: Date.now(), loginTried: true } });
      const back = location.origin + location.pathname + spec;
      location.href = `https://accounts.yanolja.com/?service=yanolja&redirectUrl=${encodeURIComponent(back)}`;
      return;
    }

    // 1. 옵션 창 열기. 버튼은 서버가 그린 HTML 에 먼저 보이지만 React 가 붙기 전에는 눌러도 반응이 없어서,
    //    이미지 등 페이지 로드가 다 끝나길 기다리지 않고 달력이 뜰 때까지 다시 누른다. 레이아웃마다 버튼이 여럿이라 뒤에서부터.
    //    옵션 창('접어두기' 버튼)은 떴는데 달력이 늦게 그려지는 중이면 더 누르지 않는다 (다시 누르면 닫힐 수 있음).
    const calendarOpen = () => document.querySelector('button[aria-label="다음 날짜로 이동"]');
    const sheetOpen = () => buttons().some((e) => text(e).startsWith("접어두기"));
    for (const end = Date.now() + 20000; !calendarOpen() && !sheetOpen() && Date.now() < end; ) {
      const targets = buttons().filter((e) => text(e) === "옵션 선택하기").reverse();
      if (!targets.length) await until(() => buttons().some((e) => text(e) === "옵션 선택하기"), 1000);
      for (const b of targets) {
        if (calendarOpen() || sheetOpen()) break;
        b.click();
        await until(() => calendarOpen() || sheetOpen(), 600);
      }
    }
    if (!calendarOpen() && innerWidth > 700) {
      stop("창이 넓으면 옵션 창이 안 열려요. 창 폭을 휴대폰처럼 좁게 줄이고 다시 열어 주세요.");
    }
    await waitFor(calendarOpen, "날짜 달력", 3000);
    lap("옵션창");

    // 2. 날짜 — 달력 칸은 <button><abbr aria-label="2026년 10월 31일">31</abbr></button>
    const dayLabel = `${y}년 ${Number(mo)}월 ${Number(d)}일`;
    const findDay = () => [...document.querySelectorAll(`abbr[aria-label="${dayLabel}"]`)].map((a) => a.closest("button")).find(visible);
    let day = null;
    for (let i = 0; i < 4 && !day; i++) {
      day = findDay();
      if (!day) {
        document.querySelector('button[aria-label="다음 날짜로 이동"]')?.click();
        day = await until(findDay, 1500);
      }
    }
    if (!day) stop(`달력에서 ${dayLabel}을 못 찾았어요.`);
    day = (await settle(findDay, (e) => !e.disabled)) || findDay() || day;
    if (day.disabled) stop(`${dayLabel}은 그새 품절됐어요.`);
    day.click();
    lap("날짜");

    // 3. 회차 — <button role="option" aria-label="14:00 선택">14:00 3매</button>, 품절이면 '마감'
    const findSlot = () => document.querySelector(`button[role="option"][aria-label="${time} 선택"]`);
    await waitFor(findSlot, `${time} 회차`);
    const open = (e) => !e.disabled && !/마감/.test(text(e));
    const slot = (await settle(findSlot, open)) || findSlot();
    if (!slot) stop(`${time} 회차가 목록에서 사라졌어요. 다른 회차를 직접 골라 주세요.`);
    if (!open(slot)) stop(`${time} 회차가 그새 마감됐어요 ('${text(slot)}'). 다른 회차를 직접 골라 주세요.`);
    slot.click();
    lap("회차");

    // 4. 이용자: 입장권 성인
    (await waitFor(() => buttons('button[role="option"]').find((e) => text(e) === "입장권 성인"), "'입장권 성인'")).click();
    lap("성인");

    // 5. 이용자 할인: 일반
    (await waitFor(() => buttons('button[role="option"]').find((e) => text(e).startsWith("일반")), "'일반' 요금")).click();
    lap("일반");

    // 6. 매수
    const input = await waitFor(() => buttons('input[aria-label="숫자 입력"]')[0], "매수 입력칸");
    for (let i = 0; i < 10 && Number(input.value) < qty; i++) {
      const plus = document.querySelector('button[aria-label="플러스 버튼"]');
      if (!plus || plus.disabled) break;
      const before = Number(input.value);
      plus.click();
      await until(() => Number(input.value) !== before || null, 1000);
    }
    lap("매수");
    // 알림 뒤 그새 표가 줄었으면 남은 만큼(1장이라도) 산다
    if (Number(input.value) < 1) stop(`매수를 1장으로도 못 맞췄어요 (지금 ${input.value}장).`);
    if (Number(input.value) < qty) say(`${qty}장까지는 안 남아서 ${input.value}장으로 진행해요.`);

    // 7. 구매하기 — 매수 입력칸과 같은 창 안의 버튼
    let box = input.parentElement, buy = null;
    while (box && !buy) {
      buy = [...box.querySelectorAll("button")].find((e) => visible(e) && text(e) === "구매하기" && !e.disabled);
      box = box.parentElement;
    }
    if (!buy) stop("'구매하기' 버튼을 못 찾았어요. 직접 눌러 주세요.");
    if (dry) {
      buy.style.outline = "4px solid #f59e0b";
      const item = document.querySelector('button[aria-label$="옵션 삭제"]')?.getAttribute("aria-label")?.replace(/ 옵션 삭제$/, "");
      return say(`시험 모드라 '구매하기' 직전에 멈췄어요 (노란 테두리). 선택: ${item} ${input.value}장${took()}`, "#b45309");
    }
    lap("구매하기");
    say(`구매하기 누름 — 주문서가 뜨면 결제만 하세요.${took()}`, "#047857");
    // 주문서로 넘어가면 이 페이지가 사라진다. 그대로 남아 창이 뜨면 ('선택한 상품이 매진되었어요' 등) 무엇인지 남긴다
    const notices = () => [...document.querySelectorAll('[role="dialog"], [role="alertdialog"]')].filter((e) => visible(e) && text(e))
      .concat([...document.querySelectorAll("body *")].filter((e) => !e.children.length && /매진|품절|초기화|다시 선택/.test(e.textContent) && visible(e)));
    let shown = new Set();
    try { shown = new Set(notices()); } catch (_) {} // 무슨 일이 있어도 구매하기는 누른다
    const here = location.href; // 같은 페이지 안에서 주문서 주소로 바뀌어도 넘어간 것
    buy.click();
    for (const end = Date.now() + 15000; Date.now() < end; ) {
      await sleep(300);
      if (location.href !== here) return;
      let notice = null;
      try { notice = notices().find((e) => !shown.has(e)); } catch (_) {}
      if (notice) stop(`구매하기 뒤 주문서 대신 '${(notice.innerText || text(notice)).trim().replace(/\s+/g, " ").slice(0, 60)}' 창이 떴어요.`);
    }
    say("구매하기 누른 지 15초가 지났는데 주문서가 안 떠요. 화면을 확인해 주세요.", "#b91c1c");
  }

  run().catch((e) => console.warn("[hwadam-auto]", e));
})();
