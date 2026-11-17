// SPDX-License-Identifier: GPL-3.0-or-later
// Glossary helpers, all optional extras on top of the /glossary/ page:
//  - links the first use of each glossary term in every part of the toolkit
//    text marked [data-glossary-scope] to its definition;
//  - opens those links, and any [data-glossary-open] button, in a searchable
//    side panel (#glossary-panel) instead of leaving the page;
//  - adds a "Find a term" filter to the glossary page ([data-glossary-filter]).
(function () {
  "use strict";
  // Matomo event, if analytics is loaded (see analytics.js). Fixed values only, never typed text.
  function track(category, action, name) {
    if (window._paq) window._paq.push(name ? ["trackEvent", category, action, name] : ["trackEvent", category, action]);
  }

  var panel = document.getElementById("glossary-panel");
  var data = null;
  var opener = null;

  function load() {
    if (!data) {
      data = fetch(panel.dataset.src).then(function (r) {
        if (!r.ok) throw new Error(r.status);
        return r.json();
      });
    }
    return data;
  }

  function escapeRe(s) {
    return s.replace(/[.*+?^${}()|[\]\\]/g, "\\$&");
  }

  function textOf(html) {
    var div = document.createElement("div");
    div.innerHTML = html;
    return div.textContent;
  }

  // ---------- Term links ----------
  // Text inside these is never linked.
  var SKIP = "a, h1, h2, h3, h4, h5, h6, code, pre, sup, figcaption, label, button, .footnotes, .section-end, .checklist-status";

  function linkTerms(g) {
    var terms = g.terms.slice().sort(function (a, b) { return b.term.length - a.term.length; });
    var patterns = terms.map(function (t) {
      // "Born Digital" also matches "born-digital"; a trailing "s" matches plurals.
      var words = escapeRe(t.term).replace(/\s+/g, "[\\s\\u00a0-]+");
      return { term: t, re: new RegExp("\\b" + words + "s?\\b", "i") };
    });
    document.querySelectorAll("[data-glossary-scope]").forEach(function (scope) {
      patterns.forEach(function (p) {
        var walker = document.createTreeWalker(scope, NodeFilter.SHOW_TEXT, {
          acceptNode: function (n) {
            return n.parentElement.closest(SKIP) ? NodeFilter.FILTER_REJECT : NodeFilter.FILTER_ACCEPT;
          }
        });
        var node, m;
        while ((node = walker.nextNode())) {
          m = p.re.exec(node.data);
          if (!m) continue;
          var word = node.splitText(m.index);
          word.splitText(m[0].length);
          var a = document.createElement("a");
          a.className = "term-link";
          a.href = g.page + "#" + p.term.id;
          a.dataset.term = p.term.id;
          a.textContent = word.data;
          var hint = document.createElement("span");
          hint.className = "visually-hidden";
          hint.textContent = " (glossary)";
          a.appendChild(hint);
          word.parentNode.replaceChild(a, word);
          break; // first use in this part of the text only
        }
      });
    });
  }

  // ---------- Side panel ----------
  var list, filterInput, status, rendered = false;

  function render(g) {
    if (rendered) return;
    rendered = true;
    g.terms.forEach(function (t) {
      var det = document.createElement("details");
      det.id = "gp-" + t.id;
      var sum = document.createElement("summary");
      sum.textContent = t.term;
      det.appendChild(sum);
      var text = t.term;
      t.definitions.forEach(function (d) {
        var fig = document.createElement("div");
        fig.className = "definition";
        var body = document.createElement("div");
        body.innerHTML = d.html; // built by Hugo from data/glossary.yaml
        if (!body.querySelector("p, ol, ul, blockquote")) { // a one-paragraph definition
          var p = document.createElement("p");
          while (body.firstChild) p.appendChild(body.firstChild);
          body.appendChild(p);
        }
        fig.appendChild(body);
        var src = document.createElement("p");
        src.className = "source";
        if (d.url) {
          var link = document.createElement("a");
          link.href = d.url;
          link.textContent = d.source;
          src.appendChild(link);
        } else {
          src.textContent = d.source;
        }
        fig.appendChild(src);
        det.appendChild(fig);
        text += " " + textOf(d.html);
      });
      det.dataset.text = text.toLowerCase();
      list.appendChild(det);
    });
  }

  function filter(q) {
    q = q.trim().toLowerCase();
    var shown = 0;
    list.querySelectorAll("details").forEach(function (det) {
      var hit = !q || det.dataset.text.indexOf(q) !== -1;
      det.hidden = !hit;
      if (hit) shown++;
    });
    status.textContent = q ? (shown === 1 ? "1 term" : shown + " terms") + " match “" + q + "”" : "";
  }

  function openPanel(id, from) {
    opener = from || document.activeElement;
    load().then(function (g) {
      render(g);
      filterInput.value = "";
      filter("");
      if (!panel.open) panel.showModal();
      var det = id && document.getElementById("gp-" + id);
      if (det) {
        det.open = true;
        det.scrollIntoView({ block: "start" });
        det.querySelector("summary").focus();
      } else {
        filterInput.focus();
      }
    }).catch(function () {
      // No data: fall back to the glossary page.
      var link = from && from.closest("a[href]");
      if (link) window.location.href = link.href;
    });
  }

  if (panel && typeof panel.showModal === "function") {
    list = panel.querySelector(".gp-list");
    filterInput = panel.querySelector("#gp-filter");
    status = panel.querySelector(".gp-status");

    filterInput.addEventListener("input", function () { filter(filterInput.value); });
    panel.querySelector("[data-glossary-close]").addEventListener("click", function () { panel.close(); });
    panel.addEventListener("click", function (e) { if (e.target === panel) panel.close(); });
    panel.addEventListener("close", function () {
      if (opener && opener.focus) opener.focus();
    });

    document.addEventListener("click", function (e) {
      var a = e.target.closest("a.term-link");
      if (!a || e.ctrlKey || e.metaKey || e.shiftKey || e.altKey || e.button !== 0) return;
      e.preventDefault();
      track("Glossary", "Open term", a.dataset.term);
      openPanel(a.dataset.term, a);
    });

    document.querySelectorAll("[data-glossary-open]").forEach(function (b) {
      b.hidden = false;
      b.addEventListener("click", function () { track("Glossary", "Open panel"); openPanel(null, b); });
    });

    if (document.querySelector("[data-glossary-scope]")) {
      load().then(linkTerms).catch(function () {});
    }
  }

  // ---------- Filter on the glossary page ----------
  var pageFilter = document.querySelector("[data-glossary-filter]");
  if (pageFilter) {
    var input = pageFilter.querySelector("input");
    var out = pageFilter.querySelector("[role=status]");
    var terms = document.querySelectorAll(".term");
    var letters = document.querySelectorAll(".az-letter");
    pageFilter.hidden = false;
    pageFilter.addEventListener("submit", function (e) { e.preventDefault(); });
    input.addEventListener("input", function () {
      var q = input.value.trim().toLowerCase();
      var shown = 0;
      terms.forEach(function (t) {
        var hit = !q || t.textContent.toLowerCase().indexOf(q) !== -1;
        t.hidden = !hit;
        if (hit) shown++;
      });
      // Hide a letter heading when none of its terms are showing.
      letters.forEach(function (h) {
        var any = false;
        for (var n = h.nextElementSibling; n && !n.classList.contains("az-letter"); n = n.nextElementSibling) {
          if (n.classList.contains("term") && !n.hidden) { any = true; break; }
        }
        h.hidden = !any;
      });
      out.textContent = q ? (shown === 1 ? "1 term" : shown + " terms") + " match “" + q + "”" : "";
    });
  }
})();
