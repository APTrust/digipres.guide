// SPDX-License-Identifier: GPL-3.0-or-later
// Feedback form. Fills in the page the reader came from, then sends the form
// to Google Forms in the background and shows our own thank-you message.
// Google doesn't tell an outside page whether a response arrived, so the
// message says the feedback was sent, not that it was received.
(function () {
  "use strict";
  // Matomo event, if analytics is loaded (see analytics.js). Fixed values only, never typed text.
  function track(category, action, name) {
    if (window._paq) window._paq.push(name ? ["trackEvent", category, action, name] : ["trackEvent", category, action]);
  }
  var form = document.querySelector("[data-feedback]");
  if (!form) return;
  var status = form.querySelector("[data-feedback-status]");
  var pageField = form.querySelector("[data-feedback-page]");
  var honeypot = form.querySelector("[data-honeypot]");
  var button = form.querySelector("button[type=submit]");

  // ?page=/learn/ from the footer link: show it as a full address.
  var from = new URLSearchParams(window.location.search).get("page");
  if (from && from.charAt(0) === "/" && from.charAt(1) !== "/" && !pageField.value) {
    pageField.value = new URL(from, pageField.dataset.site).href;
  }

  function say(text, ok) {
    status.textContent = text;
    status.className = "form-status " + (ok ? "ok" : "error");
    status.focus();
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    if (!form.reportValidity()) return;
    if (honeypot.value) { // a bot filled in the hidden field
      form.reset();
      say("Thanks. Your feedback was sent to the toolkit team.", true);
      return;
    }
    var body = new URLSearchParams();
    new FormData(form).forEach(function (value, name) {
      if (name !== honeypot.name) body.append(name, value);
    });
    button.disabled = true;
    fetch(form.action, { method: "POST", mode: "no-cors", body: body })
      .then(function () {
        track("Feedback", "Sent");
        form.reset();
        say("Thanks. Your feedback was sent to the toolkit team.", true);
      })
      .catch(function () {
        say("Your feedback couldn't be sent. Check your connection and try again.", false);
      })
      .then(function () { button.disabled = false; });
  });
})();
