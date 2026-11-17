// SPDX-License-Identifier: GPL-3.0-or-later
// Filters for the tools directory: by task, platform, and cost. Without this
// script, the full table shows and the filters stay hidden.
(function () {
  "use strict";
  // Matomo event, if analytics is loaded (see analytics.js). Fixed values only, never typed text.
  function track(category, action, name) {
    if (window._paq) window._paq.push(name ? ["trackEvent", category, action, name] : ["trackEvent", category, action]);
  }
  var form = document.querySelector("[data-tool-filters]");
  if (!form) return;
  var rows = document.querySelectorAll(".tools-table tbody tr");
  var count = document.querySelector("[data-tool-count]");
  form.hidden = false;

  function apply() {
    var task = form.elements.task.value;
    var platform = form.elements.platform.value;
    var free = form.elements.free.checked;
    var shown = 0;
    rows.forEach(function (r) {
      var ok = (!task || r.dataset.tasks.split("|").indexOf(task) !== -1) &&
        (!platform || r.dataset.platforms.split(" ").indexOf(platform) !== -1) &&
        (!free || r.dataset.free === "true");
      r.hidden = !ok;
      if (ok) shown++;
    });
    var filtered = task || platform || free;
    count.textContent = filtered ? "Showing " + shown + " of " + rows.length + " tools" : rows.length + " tools";
  }

  form.addEventListener("change", function (e) {
    apply();
    var f = e.target;
    if (f.name === "free") { if (f.checked) track("Tools", "Filter", "free"); }
    else if (f.value) track("Tools", "Filter", f.name + ":" + f.value); // option values from the page, not typed text
  });
  form.addEventListener("submit", function (e) { e.preventDefault(); });
  apply();
})();
