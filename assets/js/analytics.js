// SPDX-License-Identifier: GPL-3.0-or-later
// Matomo page-view counting, set up for privacy (see "Analytics" in
// planning/project-plan.md and the privacy note on /about/):
//  - no cookies, and nothing is sent when the browser asks not to be tracked;
//  - addresses are recorded without their query strings, so what readers type
//    into search (/search/?q=...) never reaches Matomo;
//  - no user IDs, form contents, or other free text.
// Every pathfinder answer is its own page (/start/<situation>/<level>/), so
// page views alone show which paths readers choose.
// The tracker address and site ID come from params.matomo in hugo.toml.
(function () {
  "use strict";
  var me = document.currentScript;
  var u = me.dataset.url;
  if (u.slice(-1) !== "/") u += "/";

  function bare(href) {
    try {
      var x = new URL(href);
      return x.origin + x.pathname;
    } catch (e) {
      return "";
    }
  }

  var _paq = window._paq = window._paq || [];
  _paq.push(["disableCookies"]);
  _paq.push(["setDoNotTrack", true]);
  _paq.push(["setCustomUrl", bare(window.location.href)]);
  if (document.referrer) {
    var ref = new URL(document.referrer);
    // Our own pages: drop the query. Other sites: keep only the site's address.
    _paq.push(["setReferrerUrl", ref.origin === window.location.origin ? bare(document.referrer) : ref.origin + "/"]);
  }
  _paq.push(["trackPageView"]);
  _paq.push(["enableLinkTracking"]);
  _paq.push(["setTrackerUrl", u + "matomo.php"]);
  _paq.push(["setSiteId", me.dataset.site]);

  var g = document.createElement("script");
  g.async = true;
  g.src = u + "matomo.js";
  document.head.appendChild(g);
})();
