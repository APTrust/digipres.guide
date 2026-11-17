// Pathfinder: shows the two-question form and sends the reader to the
// static page for their answers, /start/<situation>/<level>/.
// Every path is a real page, so nothing breaks if this script doesn't run.
(function () {
  "use strict";
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
      window.location.href = form.dataset.base + situation + "/" + level + "/";
    });
  });
})();
