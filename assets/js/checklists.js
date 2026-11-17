// SPDX-License-Identifier: GPL-3.0-or-later
// Interactive checklists. The import turns the manuscript's ☐ items into task
// lists (<ul class="checklist">), which Hugo renders as disabled checkboxes.
// This script makes them clickable and saves what's ticked in the reader's own
// browser (localStorage), so progress survives a reload. Nothing is sent
// anywhere. The same checklist on a phase page and on the /checklists/
// worksheet shares its progress, because both use the section's
// data-checklist name.
(function () {
  "use strict";
  // Matomo event, if analytics is loaded (see analytics.js). Fixed values only, never typed text.
  function track(category, action, name) {
    if (window._paq) window._paq.push(name ? ["trackEvent", category, action, name] : ["trackEvent", category, action]);
  }

  var KEY = "digipres-checklists";

  function load() {
    try { return JSON.parse(window.localStorage.getItem(KEY)) || {}; } catch (e) { return {}; }
  }
  function save(state) {
    try { window.localStorage.setItem(KEY, JSON.stringify(state)); } catch (e) { /* private mode: progress lasts until the page closes */ }
  }

  var state = load();

  document.querySelectorAll("ul.checklist").forEach(function (list) {
    var scope = list.closest("[data-checklist]");
    var name = scope ? scope.dataset.checklist : window.location.pathname;
    var items = [];

    list.querySelectorAll(":scope > li").forEach(function (li) {
      var box = li.querySelector(":scope > input[type=checkbox], :scope > p > input[type=checkbox]");
      if (!box) return;
      // Put the box and its text in a label, so the whole line is clickable.
      var label = document.createElement("label");
      while (li.firstChild) label.appendChild(li.firstChild);
      li.appendChild(label);
      var text = label.textContent.trim().replace(/\s+/g, " ");
      box.disabled = false;
      box.removeAttribute("disabled");
      box.checked = !!(state[name] && state[name][text]);
      items.push({ box: box, text: text });
    });
    if (!items.length) return;

    var bar = document.createElement("p");
    bar.className = "checklist-status";
    var count = document.createElement("span");
    count.setAttribute("aria-live", "polite");
    var clear = document.createElement("button");
    clear.type = "button";
    clear.className = "button-quiet";
    clear.textContent = "Clear";
    bar.appendChild(count);
    bar.appendChild(clear);
    var sheet = document.body.dataset.worksheet;
    if (sheet && !document.querySelector("[data-worksheet-page]")) {
      var link = document.createElement("a");
      link.href = sheet + "#" + name.replace(/\//g, "-");
      link.textContent = "Printable worksheet";
      bar.appendChild(link);
    }
    list.insertAdjacentElement("afterend", bar);

    function update() {
      var done = items.filter(function (i) { return i.box.checked; }).length;
      count.textContent = done + " of " + items.length + " done";
      clear.hidden = done === 0;
    }

    items.forEach(function (i) {
      i.box.addEventListener("change", function () {
        state = load();
        state[name] = state[name] || {};
        if (i.box.checked) state[name][i.text] = true; else delete state[name][i.text];
        if (!Object.keys(state[name]).length) delete state[name];
        save(state);
        update();
        track("Checklist", i.box.checked ? "Tick" : "Untick", name);
      });
    });
    clear.addEventListener("click", function () {
      items.forEach(function (i) { i.box.checked = false; });
      state = load();
      delete state[name];
      save(state);
      update();
      track("Checklist", "Clear", name);
      items[0].box.focus();
    });
    update();
  });

  // The worksheet's print button.
  document.querySelectorAll("[data-print]").forEach(function (b) {
    b.hidden = false;
    b.addEventListener("click", function () { track("Checklist", "Print worksheet"); window.print(); });
  });
})();
