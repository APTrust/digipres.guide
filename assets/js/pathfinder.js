// SPDX-License-Identifier: GPL-3.0-or-later
// Pathfinder: shows the two-question form and sends the reader to the
// static page for their answers, /start/<situation>/<level>/.
// Every path is a real page, so nothing breaks if this script doesn't run.
(function () {
  "use strict";
  // Matomo event, if analytics is loaded (see analytics.js). Fixed values only, never typed text.
  function track(category, action, name) {
    if (window._paq) window._paq.push(name ? ["trackEvent", category, action, name] : ["trackEvent", category, action]);
  }
  document.querySelectorAll("form[data-pathfinder]").forEach(function (form) {
    form.hidden = false;
    form.addEventListener("submit", function (event) {
      event.preventDefault();
      var situation = form.elements.situation.value;
      var level = form.elements.level.value;
      if (!situation || !level) {
        form.reportValidity();
        return;
      }
      track("Pathfinder", form.closest("details") ? "Change answers" : "Show path", situation + "/" + level);
      window.location.href = form.dataset.base + situation + "/" + level + "/";
    });
  });
})();
