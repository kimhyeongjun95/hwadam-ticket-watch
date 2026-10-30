// 화담숲 상품 페이지가 #hwadam-auto=날짜_시간_매수 를 달고 열리면
// 날짜 → 회차 → 입장권 성인 → 일반 → 매수 → 모노레일(2구간) → 구매하기 순서로 눌러 주문서를 띄운다. 결제는 사람이 한다.
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
  // done: 끝났을 때만 "ok"(주문서 뜸 → 내려 둔 창을 올리고 크롬을 앞으로) 또는 "fail"(멈춤 → 맥 알림)
  const say = (text, color, done) => {
    banner.textContent = `화담숲 자동 진행: ${text}`;
    if (color) banner.style.background = color;
    if (!banner.isConnected && document.body) document.body.appendChild(banner);
    console.log("[hwadam-auto]", text);
    // 맥 수신기 로그에도 남긴다 (background.js 가 localhost 로 전달)
    try { chrome.runtime.sendMessage({ log: text, done }); } catch (_) {}
  };
  // 단계마다 페이지를 열기 시작한 뒤 몇 초째인지 적어 두고 끝날 때 로그에 붙인다 (어디가 느린지 보려고)
  const laps = [];
  const lap = (name) => laps.push(`${name} ${(performance.now() / 1000).toFixed(1)}`);
  const took = () => (laps.length ? ` [초: ${laps.join(" · ")}]` : "");
  const stop = (text) => { say(text + took(), "#b91c1c", "fail"); throw new Error(text); };

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
  const byText = (s) => buttons().find((e) => text(e) === s);

  // 매수 입력칸을 qty 까지 올린다. 옵션을 고른 직후엔 플러스 버튼이 잠깐 비활성이라, 눌릴 수 있게 될 때까지 기다렸다가 누른다
  // (예전엔 비활성을 보자마자 포기해서 2장 알림에도 1장으로 넘어갔다 — 10/17·10/18 세 번)
  // 입장권·모노레일 단계마다 플러스 버튼이 따로 있고 지나간 단계 것은 숨어 있어서 보이는 것만 누른다
  async function setQty(input, qty) {
    const plusReady = () => {
      const p = buttons('button[aria-label="플러스 버튼"]')[0];
      return p && !p.disabled && p.getAttribute("aria-disabled") !== "true" ? p : null;
    };
    for (let i = 0; i < 10 && Number(input.value) < qty; i++) {
      const plus = await until(plusReady, 2000);
      if (!plus) break;
      const before = Number(input.value);
      plus.click();
      await until(() => Number(input.value) !== before || null, 1000);
    }
  }

  // 입장권을 고른 뒤 같은 주문에 모노레일을 더한다. 모노레일만 따로는 못 사고, 입장 20분 뒤 회차부터, 입장권 매수까지만 고를 수 있다.
  // '모노레일 선택' → (화담채를 안 골라서 뜨는 확인 창의) '모노레일로 이동' → 구간 → qty 장 남은 가장 이른 회차 → 성인 → 매수.
  // 고르면 설명을, 못 고르면 '이전'으로 입장권 단계에 돌아가 null 을 돌려준다 (그러면 입장권만 사고 모노레일은 나중에 추가상품으로).
  const MONO_SEGMENT = "2구간(1-3)";
  async function addMonorail(qty) {
    const segment = () => buttons(`button[role="option"][aria-label="${MONO_SEGMENT} 선택하기"]`)[0];
    const back = async (why) => {
      say(`${why} 모노레일 없이 입장권만 구매하기로 가요.`);
      // 반쯤 고른 모노레일이 주문에 딸려 가지 않게 지우고 돌아간다
      buttons('button[aria-label$="옵션 삭제"]').forEach((e) => e.click());
      byText("이전")?.click();
      await until(() => byText("모노레일 선택"), 3000);
      return null;
    };
    const next = byText("모노레일 선택");
    if (!next) return back("'모노레일 선택' 버튼이 없어요.");
    next.click();
    const go = await until(() => byText("모노레일로 이동") || segment(), 3000);
    if (go && text(go) === "모노레일로 이동") go.click();
    const seg = await until(segment, 5000);
    if (!seg) return back(`모노레일 ${MONO_SEGMENT}을 못 찾았어요.`);
    seg.click();
    lap("모노레일 구간");

    // 회차 — 입장권과 같은 모양 <button role="option" aria-label="09:00 선택">09:002매</button>, 품절이면 '마감'.
    // 지나간 입장권 회차 버튼도 숨은 채 남아 있어서 보이는 것만 본다. 재고를 받아오기 전일 수 있어 2초까지 기다린다
    const slots = () => buttons('button[role="option"]').filter((e) => /^\d{2}:\d{2} 선택$/.test(e.getAttribute("aria-label") || ""));
    // 글자가 '17:081매' 처럼 붙어 있어서 앞의 시각(5글자)을 떼고 읽는다
    const left = (e) => (e.disabled ? 0 : Number((text(e).slice(5).match(/^(\d+)매/) || [])[1] || 0));
    await until(() => slots().length || null, 5000);
    const slot = await until(() => slots().find((e) => left(e) >= qty), 2000);
    if (!slot) return back(`${MONO_SEGMENT} 모노레일에 ${qty}장 남은 회차가 없어요.`);
    const time = slot.getAttribute("aria-label").slice(0, 5);
    slot.click();
    lap("모노레일 회차");

    const adult = await until(() => buttons('button[role="option"]').find((e) => text(e).startsWith("모노레일 성인") && !e.disabled), 3000);
    if (!adult) return back("'모노레일 성인'을 못 찾았어요.");
    adult.click();
    const input = await until(() => buttons('input[aria-label="숫자 입력"]')[0], 3000);
    if (!input) return back("모노레일 매수 입력칸을 못 찾았어요.");
    await setQty(input, qty);
    if (Number(input.value) !== qty) return back(`모노레일을 ${qty}장으로 못 맞췄어요 (지금 ${input.value}장).`);
    lap("모노레일 매수");
    return `모노레일 ${MONO_SEGMENT} ${time} ${qty}장`;
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
    // 옵션 창이 막 열렸으면 달력이 늦게 그려질 수 있어 3초까지 기다려 보고 판단한다
    if (!calendarOpen() && innerWidth > 700 && !(await until(calendarOpen, 3000))) {
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
    const entryInput = await waitFor(() => buttons('input[aria-label="숫자 입력"]')[0], "매수 입력칸");
    await setQty(entryInput, qty);
    lap("매수");
    // 목표 매수를 못 채우면 구매하기를 누르지 않는다 (남은 표가 정말 모자라거나 버튼이 안 눌린 경우)
    if (Number(entryInput.value) !== qty) {
      stop(`${qty}장으로 못 맞춰서 구매하기를 누르지 않았어요 (지금 ${entryInput.value}장). 남은 표가 모자랄 수 있어요.`);
    }

    // 7. 모노레일. 못 고르면 입장권만 산다
    const mono = await addMonorail(qty);

    // 8. 구매하기 — 지금 보이는 단계(모노레일 또는 입장권)의 매수 입력칸과 같은 창 안의 버튼
    const input = buttons('input[aria-label="숫자 입력"]')[0] || entryInput;
    let box = input.parentElement, buy = null;
    while (box && !buy) {
      buy = [...box.querySelectorAll("button")].find((e) => visible(e) && text(e) === "구매하기" && !e.disabled);
      box = box.parentElement;
    }
    if (!buy) stop("'구매하기' 버튼을 못 찾았어요. 직접 눌러 주세요.");
    if (dry) {
      buy.style.outline = "4px solid #f59e0b";
      const item = document.querySelector('button[aria-label$="옵션 삭제"]')?.getAttribute("aria-label")?.replace(/ 옵션 삭제$/, "");
      return say(`시험 모드라 '구매하기' 직전에 멈췄어요 (노란 테두리). 선택: ${item} ${entryInput.value}장 + ${mono || "모노레일 없음"}${took()}`, "#b45309", "ok");
    }
    lap("구매하기");
    say(`구매하기 누름 (${mono || "모노레일 없이 입장권만"}) — 주문서가 뜨면 결제만 하세요.${took()}`, "#047857");
    // 주문서로 넘어가면 이 페이지가 사라진다. 그대로 남아 창이 뜨면 ('선택한 상품이 매진되었어요' 등) 무엇인지 남긴다
    const notices = () => [...document.querySelectorAll('[role="dialog"], [role="alertdialog"]')].filter((e) => visible(e) && text(e))
      .concat([...document.querySelectorAll("body *")].filter((e) => !e.children.length && /매진|품절|초기화|다시 선택/.test(e.textContent) && visible(e)));
    let shown = new Set();
    try { shown = new Set(notices()); } catch (_) {} // 무슨 일이 있어도 구매하기는 누른다
    const here = location.href; // 같은 페이지 안에서 주문서 주소로 바뀌어도 넘어간 것
    // 주문서로 넘어가면 이 페이지가 사라지니 그 직전(pagehide)에 알린다
    const ordered = () => say(`주문서로 넘어감 (${mono || "모노레일 없이 입장권만"})`, null, "ok");
    addEventListener("pagehide", ordered, { once: true });
    buy.click();
    for (const end = Date.now() + 15000; Date.now() < end; ) {
      await sleep(300);
      if (location.href !== here) {
        removeEventListener("pagehide", ordered);
        return ordered();
      }
      let notice = null;
      try { notice = notices().find((e) => !shown.has(e)); } catch (_) {}
      if (notice) {
        removeEventListener("pagehide", ordered);
        stop(`구매하기 뒤 주문서 대신 '${(notice.innerText || text(notice)).trim().replace(/\s+/g, " ").slice(0, 60)}' 창이 떴어요.`);
      }
    }
    removeEventListener("pagehide", ordered);
    say("구매하기 누른 지 15초가 지났는데 주문서가 안 떠요. 화면을 확인해 주세요.", "#b91c1c", "fail");
  }

  run().catch((e) => console.warn("[hwadam-auto]", e));
})();
