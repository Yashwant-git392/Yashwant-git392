/* Campus Shikayat Setu — UI dynamics (vanilla JS, no deps) */
(function () {
  "use strict";
  var root = document.documentElement;

  /* ---------- theme (light/dark) ---------- */
  var THEME_KEY = "sss-theme";
  function applyTheme(t) { root.classList.toggle("dark", t === "dark"); }
  try {
    var saved = localStorage.getItem(THEME_KEY);
    if (saved) applyTheme(saved);
    else if (window.matchMedia && window.matchMedia("(prefers-color-scheme: dark)").matches) applyTheme("dark");
  } catch (e) { /* private mode */ }
  window.toggleTheme = function () {
    var next = root.classList.contains("dark") ? "light" : "dark";
    applyTheme(next);
    try { localStorage.setItem(THEME_KEY, next); } catch (e) {}
  };

  /* ---------- sidebar: mobile drawer + desktop collapse ---------- */
  window.toggleNav = function () { document.body.classList.toggle("nav-open"); };
  window.closeNav = function () { document.body.classList.remove("nav-open"); };
  window.toggleSide = function () { document.body.classList.toggle("side-collapsed"); };
  document.addEventListener("keydown", function (e) {
    if (e.key === "Escape") document.body.classList.remove("nav-open");
  });
  document.addEventListener("click", function (e) {
    if (e.target.classList && e.target.classList.contains("overlay")) closeNav();
  });

  /* ---------- toasts: auto-dismiss + close ---------- */
  document.querySelectorAll(".toast").forEach(function (toast) {
    var close = toast.querySelector(".toast-close");
    if (close) close.addEventListener("click", function () { toast.remove(); });
    setTimeout(function () {
      toast.style.opacity = "0"; toast.style.transform = "translateX(30px)";
      setTimeout(function () { toast.remove(); }, 320);
    }, 5200);
  });

  /* ---------- KPI counters ---------- */
  var counters = document.querySelectorAll("[data-count]");
  if (counters.length) {
    var reduce = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    counters.forEach(function (el) {
      var target = parseInt(el.getAttribute("data-count"), 10);
      if (isNaN(target) || reduce) { el.textContent = el.getAttribute("data-count"); return; }
      var dur = 850, t0 = null;
      function tick(t) {
        if (!t0) t0 = t;
        var p = Math.min(1, (t - t0) / dur);
        var ease = 1 - Math.pow(2, -7 * p);
        el.textContent = Math.round(target * (p < 1 ? ease : 1));
        if (p < 1) requestAnimationFrame(tick); else el.textContent = target;
      }
      requestAnimationFrame(tick);
    });
  }

  /* ---------- animated bars ---------- */
  var bars = document.querySelectorAll("[data-bar]");
  if (bars.length) {
    requestAnimationFrame(function () {
      bars.forEach(function (b) { b.style.width = b.getAttribute("data-bar") + "%"; });
    });
  }

  /* ---------- live table filter ---------- */
  document.querySelectorAll("[data-filter-table]").forEach(function (input) {
    var table = document.querySelector(input.getAttribute("data-filter-table"));
    if (!table) return;
    var rows = Array.prototype.slice.call(table.querySelectorAll("tbody tr"));
    var counter = document.querySelector(input.getAttribute("data-filter-count") || "");
    var emptyRow = table.querySelector("[data-filter-empty]");
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase(), shown = 0;
      rows.forEach(function (tr) {
        var hit = !q || tr.textContent.toLowerCase().indexOf(q) !== -1;
        tr.classList.toggle("row-hidden", !hit);
        if (hit) shown++;
      });
      if (counter) counter.textContent = shown + " of " + rows.length;
      if (emptyRow) emptyRow.style.display = shown ? "none" : "table-row";
    });
  });

  /* ---------- password visibility toggles ---------- */
  document.querySelectorAll("[data-pwd-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var input = btn.parentElement.querySelector("input");
      if (!input) return;
      input.type = input.type === "password" ? "text" : "password";
      btn.setAttribute("aria-label", input.type === "password" ? "Show password" : "Hide password");
    });
  });

  /* ---------- demo credential chips (login page) ---------- */
  document.querySelectorAll("[data-fill]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var parts = btn.getAttribute("data-fill").split("|");
      var u = document.querySelector('input[name="username"]'), p = document.querySelector('input[name="password"]');
      if (u) u.value = parts[0] || "";
      if (p) p.value = parts[1] || "";
      if (p) p.focus();
    });
  });

  /* ---------- character counters ---------- */
  document.querySelectorAll("[data-counter-for]").forEach(function (out) {
    var field = document.querySelector(out.getAttribute("data-counter-for"));
    if (!field) return;
    var need = parseInt(out.getAttribute("data-min") || "0", 10);
    var update = function () {
      var n = field.value.trim().length;
      out.textContent = n + " / min " + need;
      out.classList.toggle("ok", n >= need);
    };
    field.addEventListener("input", update); update();
  });

  /* ---------- live routing preview (lodge form) ---------- */
  (function () {
    var form = document.getElementById("lodge-form");
    if (!form) return;
    var title = form.querySelector('[name="title"]');
    var desc = form.querySelector('[name="description"]');
    var panel = document.getElementById("route-preview");
    if (!title || !desc || !panel) return;
    var rpDept = panel.querySelector("[data-rp=dept]"), rpPrio = panel.querySelector("[data-rp=prio]"),
        rpSla = panel.querySelector("[data-rp=sla]"), rpScore = panel.querySelector("[data-rp=score]"),
        rpCat = panel.querySelector("[data-rp=cat]");
    var timer = null, lastKey = "";
    function hide() { panel.classList.remove("show"); }
    function fetchPreview() {
      var t = title.value.trim(), d = desc.value.trim();
      if (t.length < 8 || d.length < 20) { hide(); return; }
      var key = t + "||" + d;
      if (key === lastKey) return;
      lastKey = key;
      fetch("/api/route-preview?title=" + encodeURIComponent(t) + "&description=" + encodeURIComponent(d), {
        credentials: "same-origin", headers: { "Accept": "application/json" }
      }).then(function (r) { return r.ok ? r.json() : null; }).then(function (data) {
        if (!data) return hide();
        rpDept.textContent = data.department || "General & Administration";
        rpCat.textContent = data.category || "—";
        rpPrio.textContent = data.priority;
        rpPrio.className = "rp-v badge badge-" + (data.priority === "High" ? "red" : data.priority === "Medium" ? "amber" : "gray");
        rpSla.textContent = data.sla_hours + " h";
        rpScore.textContent = data.score > 0 ? data.score + " pts" : "fallback";
        panel.classList.add("show");
      }).catch(hide);
    }
    [title, desc].forEach(function (el) {
      el.addEventListener("input", function () {
        clearTimeout(timer);
        timer = setTimeout(fetchPreview, 350);
      });
    });
  })();

  /* ---------- SLA live countdown ---------- */
  document.querySelectorAll("[data-sla-due]").forEach(function (el) {
    var due = new Date(el.getAttribute("data-sla-due").replace(" ", "T"));
    if (isNaN(due)) return;
    function render() {
      var now = new Date(), diff = due - now;
      var abs = Math.abs(diff);
      var h = Math.floor(abs / 36e5), m = Math.floor((abs % 36e5) / 6e4), s = Math.floor((abs % 6e4) / 1e3);
      var str = (h > 0 ? h + "h " : "") + m + "m " + (h > 0 ? "" : s + "s");
      el.classList.remove("ok", "warn", "late");
      if (diff >= 0) {
        el.textContent = "⏳ " + str + " left";
        el.classList.add(diff < 6 * 36e5 ? "warn" : "ok");
      } else {
        el.textContent = "⚠ overdue by " + str;
        el.classList.add("late");
      }
    }
    render();
    setInterval(render, 1000);
  });

  /* ---------- reports: print button ---------- */
  document.querySelectorAll("[data-print]").forEach(function (btn) {
    btn.addEventListener("click", function () { window.print(); });
  });
})();
