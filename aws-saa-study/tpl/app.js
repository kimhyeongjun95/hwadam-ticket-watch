
(function () {
  var INDEX = __INDEX__;
  var CFG = __CFG__;
  var KEY = CFG.key;
  var TOTAL = __TOTAL__;
  var GLOSS = __GLOSS__;
  var done = new Set();
  try { var raw = localStorage.getItem(KEY); if (raw) done = new Set(JSON.parse(raw)); } catch (e) {}
  function save() { try { localStorage.setItem(KEY, JSON.stringify(Array.from(done))); } catch (e) {} }

  var byPart = {};
  INDEX.forEach(function (e) { (byPart[e.part] = byPart[e.part] || []).push(e.id); });

  function render() {
    document.querySelectorAll("button.done").forEach(function (b) {
      var on = done.has(b.dataset.id);
      b.setAttribute("aria-pressed", on ? "true" : "false");
      b.querySelector(".done-text").textContent = on ? CFG.doneOn : CFG.doneOff;
    });
    document.querySelectorAll("#toc a[data-id]").forEach(function (a) { a.classList.toggle("is-done", done.has(a.dataset.id)); });
    var n = 0;
    Object.keys(byPart).forEach(function (p) {
      var ids = byPart[p], c = ids.filter(function (id) { return done.has(id); }).length;
      n += c;
      var el = document.querySelector('[data-count-for="' + p + '"]');
      if (el) el.textContent = c + "/" + ids.length;
      var box = document.querySelector('.toc-part[data-part="' + p + '"]');
      if (box) box.classList.toggle("is-complete", c === ids.length);
    });
    document.getElementById("prog-text").textContent = n + " / " + TOTAL;
    document.getElementById("prog-bar").style.width = (TOTAL ? (n / TOTAL) * 100 : 0) + "%";
  }

  document.addEventListener("click", function (ev) {
    var b = ev.target.closest("button.done");
    if (b) { var id = b.dataset.id; if (done.has(id)) done.delete(id); else done.add(id); save(); render(); return; }
    var c = ev.target.closest("button.copy");
    if (c) {
      var code = c.closest("figure").querySelector("pre").innerText;
      var ok = function () { c.textContent = "복사됨"; setTimeout(function () { c.textContent = "복사"; }, 1400); };
      var fallback = function () {
        var r = document.createRange(); r.selectNodeContents(c.closest("figure").querySelector("pre"));
        var s = window.getSelection(); s.removeAllRanges(); s.addRange(r); c.textContent = "선택됨";
        setTimeout(function () { c.textContent = "복사"; }, 1400);
      };
      try { navigator.clipboard.writeText(code).then(ok, fallback); } catch (e) { fallback(); }
    }
  });

  // glossary popover: [label, english, official korean, definition html, href, link label]
  var pop = document.getElementById("term-pop"), popFor = null;
  function closeTerm(refocus) {
    if (!popFor) return;
    popFor.setAttribute("aria-expanded", "false");
    if (refocus) popFor.focus();
    pop.hidden = true; popFor = null;
  }
  function openTerm(el) {
    var g = GLOSS[el.dataset.g];
    if (!g) return;
    closeTerm(false);
    pop.querySelector("#tp-title").textContent = g[0];
    pop.querySelector(".tp-en").textContent = g[1];
    pop.querySelector(".tp-def").innerHTML = g[3];
    var ko = pop.querySelector(".tp-ko");
    ko.textContent = g[2] ? "한국어 공식 문서 표기: " + g[2] : "";
    ko.hidden = !g[2];
    var art = el.closest("article.topic"), more = pop.querySelector(".tp-more");
    var here = art && g[4] === "#" + art.id;
    more.hidden = !g[4] || here;
    if (g[4]) { more.href = g[4]; more.textContent = "자세히: " + g[5] + " →"; }
    if (/^https?:/.test(g[4])) { more.target = "_blank"; more.rel = "noopener"; }
    else { more.removeAttribute("target"); more.removeAttribute("rel"); }
    pop.hidden = false;
    var r = el.getBoundingClientRect(), vw = document.documentElement.clientWidth;
    var pw = pop.offsetWidth, ph = pop.offsetHeight;
    var bar = document.querySelector(".bar"), top0 = bar ? bar.getBoundingClientRect().bottom : 0;
    var left = Math.min(Math.max(12, r.left + r.width / 2 - pw / 2), vw - pw - 12);
    var top = r.bottom + 8;
    if (top + ph > window.innerHeight - 8 && r.top - 8 - ph > top0) top = r.top - 8 - ph;
    pop.style.left = (left + window.scrollX) + "px";
    pop.style.top = (top + window.scrollY) + "px";
    el.setAttribute("aria-expanded", "true");
    popFor = el;
  }
  document.addEventListener("click", function (ev) {
    var t = ev.target.closest(".term");
    if (t) { if (popFor === t) closeTerm(false); else openTerm(t); return; }
    if (ev.target.closest(".tp-close")) { closeTerm(true); return; }
    var link = ev.target.closest(".tp-more, .tp-all");
    if (link) {
      if (document.body.classList.contains("searching") && !link.target) { q.value = ""; runSearch(); }
      closeTerm(false); return;
    }
    if (!ev.target.closest("#term-pop")) closeTerm(false);
  });
  document.addEventListener("keydown", function (ev) {
    if (ev.key === "Escape") { closeTerm(true); return; }
    var t = ev.target.closest && ev.target.closest(".term");
    if (t && (ev.key === "Enter" || ev.key === " ")) { ev.preventDefault(); if (popFor === t) closeTerm(false); else openTerm(t); }
  });
  window.addEventListener("resize", function () { closeTerm(false); });

  // open / close every analogy note at once
  var tAll = document.getElementById("toggle-analogies");
  tAll.addEventListener("click", function () {
    var open = tAll.getAttribute("aria-pressed") !== "true";
    document.querySelectorAll(CFG.toggleSel).forEach(function (d) { d.open = open; });
    tAll.setAttribute("aria-pressed", open ? "true" : "false");
    tAll.querySelector(".t-long").textContent = open ? CFG.longClose : CFG.longOpen;
    tAll.querySelector(".t-short").textContent = open ? CFG.shortClose : CFG.shortOpen;
  });

  // search across titles and full text
  var q = document.getElementById("q"), msg = document.getElementById("search-msg");
  function runSearch() {
    var terms = q.value.trim().toLowerCase().split(/\s+/).filter(Boolean);
    var searching = terms.length > 0, hits = 0, parts = new Set();
    INDEX.forEach(function (e) {
      var hit = !searching || terms.every(function (t) { return e.t.indexOf(t) >= 0 || e.x.indexOf(t) >= 0; });
      document.getElementById(e.id).hidden = !hit;
      var link = document.querySelector('#toc a[data-id="' + e.id + '"]');
      if (link) link.parentElement.hidden = !hit;
      if (hit) { hits++; parts.add(e.part); }
    });
    document.querySelectorAll("section.part").forEach(function (s) { s.hidden = searching && !parts.has(s.dataset.part); });
    document.querySelectorAll(".toc-part").forEach(function (s) { s.hidden = searching && !parts.has(s.dataset.part); });
    document.body.classList.toggle("searching", searching);
    document.body.classList.toggle("no-results", searching && hits === 0);
    msg.textContent = searching ? "“" + q.value.trim() + "” 검색 결과 " + hits + "개 주제" : "";
  }
  q.addEventListener("input", runSearch);
  document.getElementById("search-clear").addEventListener("click", function () { q.value = ""; runSearch(); q.focus(); });

  // tables that do not fit the screen become stacked cards
  function stackTables(root) {
    (root || document).querySelectorAll(".table-wrap").forEach(function (w) {
      if (!w.querySelector("thead") || !w.offsetParent) return;
      w.classList.remove("stack");
      if (w.scrollWidth > w.clientWidth + 2) w.classList.add("stack");
    });
  }
  var stackTimer = null;
  function restack() { clearTimeout(stackTimer); stackTimer = setTimeout(function () { stackTables(); }, 120); }
  stackTables();
  if (document.fonts && document.fonts.ready) document.fonts.ready.then(restack);
  window.addEventListener("resize", restack);
  document.addEventListener("toggle", function (ev) { if (ev.target.open) stackTables(ev.target); }, true);
  q.addEventListener("input", restack);

  // table of contents drawer on narrow screens
  var tocBtn = document.getElementById("toc-btn");
  function setToc(open) { document.body.classList.toggle("toc-open", open); tocBtn.setAttribute("aria-expanded", open ? "true" : "false"); }
  tocBtn.addEventListener("click", function () { setToc(!document.body.classList.contains("toc-open")); });
  document.getElementById("scrim").addEventListener("click", function () { setToc(false); });
  document.getElementById("toc").addEventListener("click", function (ev) { if (ev.target.closest("a")) setToc(false); });

  // highlight the topic being read
  if ("IntersectionObserver" in window) {
    var links = {};
    document.querySelectorAll("#toc a[data-id]").forEach(function (a) { links[a.dataset.id] = a; });
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (!en.isIntersecting) return;
        Object.keys(links).forEach(function (k) { links[k].removeAttribute("aria-current"); });
        var a = links[en.target.id];
        if (a) {
          a.setAttribute("aria-current", "true");
          var rail = document.getElementById("rail"), r = a.getBoundingClientRect(), rr = rail.getBoundingClientRect();
          if (r.top < rr.top + 40 || r.bottom > rr.bottom - 40) rail.scrollTop += r.top - rr.top - rr.height / 3;
        }
      });
    }, { rootMargin: "-25% 0px -65% 0px" });
    document.querySelectorAll("article.topic").forEach(function (t) { io.observe(t); });
  }

  render();
  function toHash() {
    var id = decodeURIComponent((location.hash || "").slice(1));
    var el = id && document.getElementById(id);
    if (el) el.scrollIntoView({ block: "start", behavior: "instant" });
  }
  if (location.hash) {
    setTimeout(toHash, 60);
    if (document.fonts && document.fonts.ready) document.fonts.ready.then(function () { setTimeout(toHash, 60); });
  }
})();
