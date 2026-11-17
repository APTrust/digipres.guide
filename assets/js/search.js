// SPDX-License-Identifier: GPL-3.0-or-later
// Search page. Uses the Pagefind index (built by `pagefind --site public`
// after Hugo) through Pagefind's own JavaScript API, with our own results
// list. The query is kept in the address (?q=), so searches can be shared.
(function () {
  "use strict";
  // Matomo event, if analytics is loaded (see analytics.js). Fixed values only, never typed text.
  function track(category, action, name) {
    if (window._paq) window._paq.push(name ? ["trackEvent", category, action, name] : ["trackEvent", category, action]);
  }
  var form = document.querySelector("[data-search]");
  if (!form) return;
  var input = form.elements.q;
  var status = document.querySelector("[data-search-status]");
  var results = document.querySelector("[data-search-results]");
  var pagefind = null;
  var latest = 0;
  var counted = false; // one event per page view; the search terms are never sent

  function engine() {
    if (!pagefind) {
      pagefind = import(form.dataset.bundle + "pagefind.js").then(function (pf) {
        return pf.options({ excerptLength: 24 }).then(function () { return pf; });
      });
    }
    return pagefind;
  }

  function el(tag, cls, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text) e.textContent = text;
    return e;
  }

  function show(items, q) {
    results.textContent = "";
    items.forEach(function (d) {
      var li = el("li");
      var h = el("h2");
      var a = el("a", null, (d.meta && d.meta.title) || d.url);
      a.href = d.url;
      h.appendChild(a);
      li.appendChild(h);
      var p = el("p");
      p.innerHTML = d.excerpt; // Pagefind's excerpt: escaped page text with <mark> around matches
      li.appendChild(p);
      // Matches under particular headings, such as sections of a phase page.
      var subs = (d.sub_results || []).filter(function (s) { return s.url !== d.url; }).slice(0, 3);
      if (subs.length) {
        var ul = el("ul");
        subs.forEach(function (s) {
          var sli = el("li");
          var sa = el("a", null, s.title);
          sa.href = s.url;
          sli.appendChild(sa);
          ul.appendChild(sli);
        });
        li.appendChild(ul);
      }
      results.appendChild(li);
    });
  }

  function run(q) {
    var mine = ++latest;
    q = q.trim();
    var url = new URL(window.location.href);
    if (q) url.searchParams.set("q", q); else url.searchParams.delete("q");
    window.history.replaceState(null, "", url);
    if (!q) {
      status.textContent = "";
      results.textContent = "";
      return;
    }
    engine().then(function (pf) {
      return pf.debouncedSearch(q, {}, 250);
    }).then(function (search) {
      if (mine !== latest || !search) return null; // a newer search replaced this one
      var n = search.results.length;
      status.textContent = n === 0 ? "No results for “" + q + "”." : (n === 1 ? "1 result" : n + " results") + " for “" + q + "”.";
      return Promise.all(search.results.slice(0, 20).map(function (r) { return r.data(); }));
    }).then(function (items) {
      if (items && mine === latest) {
        show(items, q);
        if (!counted) { counted = true; track("Search", "Search"); }
      }
    }).catch(function () {
      status.textContent = "Search isn't available here. It works on the published site, or in a local build that runs Pagefind (see the README).";
    });
  }

  form.addEventListener("submit", function (e) {
    e.preventDefault();
    run(input.value);
  });
  input.addEventListener("input", function () { run(input.value); });

  var start = new URLSearchParams(window.location.search).get("q");
  if (start) {
    input.value = start;
    run(start);
  }
})();
