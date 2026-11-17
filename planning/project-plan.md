# DigiPres Toolkit Website: Project Plan

*Updated November 17, 2026 · Nathan Tallman*

We are building Concept C, "Start Where You Are," as a static Hugo site in a public repository in the APTrust GitHub organization. It is published on GitHub Pages at **digipres.guide**. The site goes live in mid-February 2027, after the final manuscript is imported in January. Its URLs are frozen earlier, so CLIR's PDF can link to them.

## Decisions made

| Decision | Choice |
| --- | --- |
| Site concept | C: Start Where You Are (pathfinder home page, full toolkit one click away) |
| Generator | Hugo, pinned to one exact version in GitHub Actions |
| Repository | Public, in the APTrust GitHub organization, with project members added at the repo level |
| Hosting | GitHub Pages at `digipres.guide`, registered through Cloudflare (see [Domain](#domain)) |
| JavaScript | Hand-written, no libraries. Every path is also a static page. |
| Search | Pagefind (standalone binary) |
| PDF | None from us. CLIR produces the official PDF, and the site links to it. |
| Feedback | A simple form on the site that submits to a Google Form, with responses in a Google Sheet. Both live in an APTrust shared drive managed by Nathan and Biz (see [Feedback form](#feedback-form)). |
| Analytics | Matomo, cookieless, with a privacy-respecting report of path choices (see [Analytics](#analytics)) |
| Accessibility | WCAG 2.2 AA |
| Revisions after launch | None planned. The site launches as v1.0 and gets maintenance only. |
| Branding | Pending CLIR's answer. The working assumption is our own identity with a CLIR credit. |

The toolkit's four phases are **LEARN** (concepts and risks), **READY** (organizational development and preparation), **CURATE** (initial preservation actions), and **PRESERVE** (long-term practices). These names are also the site's top-level sections and the first part of every URL, as in `/learn/`, `/ready/`, `/curate/`, and `/preserve/`.

## Scope

**In scope for launch**

- **Pathfinder:** two questions (what you are working with, what you can put toward it). Every answer combination gets its own static, shareable page at `/start/<situation>/<level>/`.
- **Full toolkit:** the introduction, LEARN, READY, CURATE, PRESERVE, and the conclusion. Each phase reads as one page, with numbered sections, an "On this page" contents list, a link on every heading, "Back to top" and "Next" after each section, and previous and next links between phases. Every section also keeps a short, stable URL (`/curate/check/`) that forwards to its place on the phase page (`/curate/#check`). Those short URLs are the ones to give CLIR.
- **Checklists:** interactive, with progress saved in the reader's own browser, plus a print-friendly worksheet view.
- **Glossary:** a glossary page and a searchable side panel, with each definition credited to its source (SAA, DPC, FADGI) and terms linked from the text.
- **Tools directory:** filterable by workflow step and platform.
- **Further reading and works cited.**
- **Site basics:** search, a feedback form, an "Edit this page on GitHub" link, last-updated dates, a link to CLIR's PDF once it exists, and an about and credits page.

**Out of scope:** PDF or EPUB output, user accounts, any server of our own, translations, and planned revisions after v1.0.

## Schedule

The final manuscript is due **December 15**, the same week winter breaks begin. Work that needs the team (path data, decisions) is due before the break. January is for the final-manuscript import and the pathfinder, while section authors review their pages.

```mermaid
gantt
    title DigiPres Toolkit website, Nov 2026 to Feb 2027
    dateFormat YYYY-MM-DD
    axisFormat %b %d
    section Build (Nathan)
    Phase 0 Setup                          :p0, 2026-11-23, 2026-11-25
    Phase 1 Draft import and data files    :p1, 2026-11-30, 2026-12-11
    Phase 2 Design and templates           :p2, 2026-12-07, 2026-12-18
    Winter break                           :crit, brk, 2026-12-21, 2027-01-01
    Phase 3a Final manuscript import       :p3a, 2027-01-04, 2027-01-08
    Phase 3b Pathfinder                    :p3b, 2027-01-11, 2027-01-29
    Phase 4 Accessibility and testing      :p4, 2027-02-01, 2027-02-12
    Launch                                 :milestone, 2027-02-16, 0d
    section Team
    Fill in path data                      :t1, 2026-11-23, 2026-12-18
    Decisions and CLIR branding            :milestone, 2026-12-04, 0d
    Final manuscript due                   :milestone, 2026-12-15, 0d
    Section authors review their pages     :t2, 2027-01-11, 2027-01-22
    URL list to CLIR                       :milestone, 2027-01-15, 0d
```

| Status | Phase | Dates | What happens | Gate |
| --- | --- | --- | --- | --- |
| ✅ Done (Nov 17) | 0. Setup | Nov 23 to 25 | Repo in the APTrust org, pinned Hugo, Actions deploy to Pages, `digipres.guide` DNS and HTTPS. Code licensed GPL-3.0-or-later; the content license is still an open question. | |
| ✅ Done (Nov 17) | 1. Draft import and data files | Nov 30 to Dec 11 | ✅ Converter from the path data sheet to `paths.yaml`, `tools.yaml`, `storage.yaml`, and `sections.yaml`, plus placeholder pages for every section. ✅ `glossary.yaml` from the Nov 10 draft. ✅ Import script (pandoc) turns the Nov 10 draft into 36 pages, kept private until launch (see [Keeping the toolkit text private](#keeping-the-toolkit-text-private)). | Path data template goes to the team in Phase 0 |
| 🔄 Started early | 2. Design and templates | Dec 7 to 18 | ✅ Theme (our own identity with a CLIR credit; all colors and fonts are tokens at the top of `main.css`), phase pages, about, credits, and privacy page. ✅ Interactive checklists and a printable `/checklists/` worksheet. ✅ Glossary side panel, with terms linked from the text. ✅ Tools filters. ✅ Search page. ✅ Feedback page, waiting on the Google Form's IDs. ⬜ CLIR branding, once CLIR answers. See [Follow-ups from Phase 2](#follow-ups-from-phase-2). | Decisions and CLIR branding answer by **Dec 4** |
| | Winter break | Dec 21 to Jan 1 | | Path data due **Dec 18** · Final manuscript due **Dec 15** |
| ⬜ Not started | 3a. Final manuscript import | Jan 4 to 8 | Re-run the import and the glossary import on the final .docx, privately. Add the project collaborators to the about and credits page (`content/about.md`). | |
| 🔄 Started early | 3b. Pathfinder | Jan 11 to 29 | ✅ First version built from the draft path data (see [Path data](#path-data)). ⬜ Re-run with the team's reviewed sheet, and refinements. ✅ Matomo tracker added (see [Analytics](#analytics)). Every answer loads its own page, so page views count path choices without extra events. | URL list to CLIR by **Jan 15** |
| ⬜ Not started | 4. Accessibility and testing | Feb 1 to 12 | WCAG 2.2 AA audit, keyboard and screen reader passes, a few practitioner walkthroughs | Section authors' review done by **Jan 22** |
| ⬜ Not started | Launch | Week of Feb 15 | Publish the toolkit text (import with `--out content`), set `launched = true`, show only Approved paths, tag v1.0, announce | |

The break dates are assumptions; the team should confirm them. If path data slips past December 18, the pathfinder launches with the situations that are ready.

### Launching before the CLIR PDF

We expect the site to go live before CLIR publishes, and that's fine. For the PDF to link to the site, what matters is that **URLs are final** before CLIR locks the PDF, not that the site is public. So:

1. The domain is settled: `digipres.guide` is registered.
2. After the final manuscript is imported (Jan 8), we freeze the URL map and send CLIR the list of section URLs by January 15.
3. The site can run at its real domain before launch. Search engines are blocked until launch day if we want a quieter preview.
4. When CLIR publishes, we add the PDF link (and DOI, if there is one) to every section page in one small change.

If CLIR's schedule lets both go out together, we hold the announcement until publication day.

## Path data

The pathfinder can't be built without the path data, and none of it is in the manuscript yet. The template is [`path-data-template.xlsx`](path-data-template.xlsx). Upload it to Google Drive and open it as a Google Sheet so the team can work on it together. Everyone on the team is a path data author. Each person takes ownership of one or more situations on the Situations tab.

| Tab | What goes in it |
| --- | --- |
| Start here | Instructions and rules (IDs, blurb length, how to list tools) |
| Levels | Resource levels: title, budget, staff time, IT access, copies goal |
| Situations | Starting situations: title, one-line description, owner, optional effort |
| Steps | Ordered steps per situation: title, blurb, toolkit section, tools, and whether it varies by level |
| Level variations | For steps that vary: what the reader sees, and which storage, at each level |
| Framing copy | Home page intro, the "this is one route" note, the closing "good is good enough" message |
| Storage options, Tools, Sections | Reference lists for the dropdowns. Add rows as needed. |

The grey italic rows are examples from the concept mockup. Sections are keyed to the November 10 draft under the four phase names. If the final manuscript renames a section, keep its ID and change only its title.

The converter is [`scripts/convert_path_data.py`](../scripts/convert_path_data.py) (Python standard library only). It reads the sheet, downloaded as .xlsx, and rewrites `data/paths.yaml`, `data/tools.yaml`, `data/storage.yaml`, and `data/sections.yaml`. It stops with a list of problems, naming the tab and row, if a step points to a section, tool, level, or storage option that doesn't exist. Nothing is written until the whole sheet checks out.

**The pathfinder is already built from the draft data** ([path-data-draft.xlsx](path-data-draft.xlsx)), so the team can review paths on the preview site as well as in the sheet. Every change after review works the same way: download the Sheet, re-run the converter, and push. Rows added, edited, or deleted in the sheet are added, edited, or deleted on the site. Keep IDs stable once they're in use, because they're part of the paths' URLs.

Which situations appear depends on their Status. Before launch, everything except "Not started" is shown, with a "Draft" note on any path that isn't Approved. At launch, `params.pathfinder.statuses` in `hugo.toml` changes to show only Approved paths.

**Also needed from the team before the break**

- [ ] Glossary: the final term list, and which source's definition to show for each term. A first version from the Nov 10 draft is on the site at `/glossary/`, showing every source's definition (cleared to be public on Nov 17). Re-run `scripts/import_glossary.py` on each new draft.
- [ ] Figures: source files (SVG preferred) and alt text for the cycle diagram and the two workflow diagrams. If none exist, we'll redraw them.
- [ ] Tools tab: check URLs and notes for the tools you know.
- [ ] CLIR: whether Pocket Burgundy branding is required.
- [ ] A content license (for example, CC BY 4.0).

### Follow-ups from Phase 2

- [ ] **Glossary links:** after the final import, read through the linked terms on each phase page. Linking matches each term's text, so it can catch a term inside a longer name (for example, "Digital Preservation" inside "Digital Preservation Coalition"). Fix false matches in `assets/js/glossary.js` or reword the term list.
- [ ] **Path data sheet, Tools tab:** the virus scanner's "Used for" is "Prepare", a workflow stage rather than a task, so "Prepare" shows up as a task in the tools filter. Change it (for example, to "Virus scanning") and re-run the converter.
- [ ] **Feedback form spam field:** once the Google Form exists, submit the site's form with JavaScript turned off and check that Google accepts the extra hidden `website` (honeypot) field. If it doesn't, remove the field's `name` and rely on the JavaScript check only.
- [ ] **About and credits page:** add the project collaborators (Phase 3a).

## Final manuscript import

The import script, [`scripts/import_manuscript.py`](../scripts/import_manuscript.py), was written in Phase 1 against the Nov 10 draft, so the final pass (Jan 4 to 8) is mostly a rerun plus review.

1. **Receive the final .docx** (Dec 15) and save it in `content-drafts/`.
2. **Re-run the import.** pandoc converts the .docx to Markdown and splits it into one page per section, following a heading-to-page map in the script. It drops working material (outline, author assignments, timeline), moves each footnote to the page that cites it, and extracts the figures. It warns about any mapped heading it can't find and any path-data section left without a page. Re-run `scripts/import_glossary.py` too.
3. **Review the changes privately.** Compare the new pages in `private/content/` with the draft import (for example, by copying the old folder aside first and diffing).
4. **Keep URLs stable.** When a heading is renamed, update its text in the script's map and keep the page ID. Anything that moves gets a redirect (a Hugo alias).
5. **Reconcile the path data.** The build fails if a path step links to a section that was renamed or removed. We fix those failures in the sheet's Sections tab and re-run the converter.
6. **Section authors review their own pages** (Jan 11 to 22) on the preview site.
7. **Freeze URLs and send the list to CLIR** (Jan 15).

The draft has issues the final manuscript should settle, because the site depends on them:

- The cycle figure describes five stages (Prepare, Curate, Check, Transfer, Save & Maintain), but the CURATE text has four headings, and Check has no heading of its own.
- The phase names now read LEARN, READY, CURATE, and PRESERVE. The conclusion still says CREATE.
- The four figures need alt text. The import leaves it empty.
- CURATE's "Check" and the Conclusion and Works Cited are bold paragraphs rather than headings. The import handles this, but real headings in the final manuscript would be safer.
- The draft's Further Reading appendix is unfinished, so it isn't imported yet. Each phase's "Further Resources with Annotation" becomes its own page (for example `/learn/further-resources/`).

### Keeping the toolkit text private

The toolkit text stays out of the public repository and off the public site until launch.

- The import writes to `private/`, which git ignores, as are the manuscript drafts in `content-drafts/`. The public site and repository keep the "coming soon" placeholders.
- To read the full site locally, run `hugo server --config hugo.toml,hugo.private.toml`. This layers `private/` over the placeholders and shows a red "Private preview" banner on every page. GitHub Actions never uses this config, and `private/` doesn't exist there.
- The path data, tools, and glossary are public now. The glossary was cleared to be public on Nov 17.
- At launch, run the import with `--out content`, which writes the pages into the site itself, then commit them.
- Several passages are unfinished, including the political shifts bullet, the ransomware sentence, and the recommended reading under Program Benchmarking.

## Feedback form

Readers send feedback through a short form styled like the rest of the site: which page, what's wrong or what they'd suggest, and an optional email. Behind it is a Google Form owned by the team, so there are no GitHub accounts, no tokens, and no second repository. Responses stay private, in a Google Sheet only the team can see.

1. Nathan creates the Google Form and its response Sheet in an **APTrust shared drive**, not in anyone's My Drive, so the files belong to APTrust rather than to a person. Nathan and Biz are both Managers of that shared drive. The questions match the site's form. Turn on email notifications for new responses.
2. The site's form posts each field straight to the Google Form's `formResponse` address. The page URL is filled in automatically.
3. The site shows its own "Thanks, we got it" message. Google doesn't confirm success to an outside page, so the message says the feedback was sent rather than claiming it arrived.
4. Without JavaScript, the form still posts, and the reader lands on Google's standard confirmation page.
5. A hidden honeypot field filters out simple bots. If spam becomes a problem, we switch to embedding Google's own form page, which has Google's protections.
6. Each Google Form question has an internal field ID (`entry.123…`) that the site needs. Nathan reads these from the form once, and if a question is deleted and re-created, the site's form must be updated to match.

The privacy note will say that feedback goes to a Google Form held by APTrust for the project team.

**Why a shared drive.** Reader emails stay in an organizational account, not a personal one. If either Manager leaves, the other keeps access, and the form keeps working without any change to the site. If shared-drive sharing turns out to be blocked for team members at other institutions, the fallback is a dedicated project Google account (for example, `feedback@digipres.guide` set up with Cloudflare Email Routing), with its credentials kept in APTrust's password manager.

Once a month, Nathan reviews the Sheet and turns anything actionable into a GitHub issue or a fix.

## Analytics

Matomo handles general traffic. For research on which paths readers choose, we don't need anything extra: every path is its own URL (`/start/legacy-media/no-budget/`), so Matomo's page reports already count path choices. A Matomo event on each in-page switch covers readers who change their answers without reloading.

Privacy settings:

- Cookieless tracking (`disableCookies`), so no consent banner is needed
- IP addresses anonymized to 2 bytes
- Respect Do Not Track
- No user IDs, form contents, or free text sent to Matomo
- Raw logs deleted after a set period (for example, 13 months); aggregated reports kept
- A short privacy note on the site that says what is counted and why

For research, the report is aggregate counts per situation, per level, and per combination over time. If the results will be published, check with the relevant IRB early on whether aggregate, anonymized web analytics need a determination.

Nathan's personal Matomo instance will be used. If needed, the data can be exported and migrated. Alternatively, could use UVA Library's Matomo instance.

**Status (Nov 17):** the tracker is on the site (`assets/js/analytics.js`, configured under `params.matomo` in `hugo.toml`, site ID 7). It is cookieless, honors Do Not Track, records page addresses without query strings (so search terms never reach Matomo), and skips the short section addresses that forward to phase pages. It loads only in production builds, so the preview site at `digipres.guide` is counted from now on; local previews aren't.

Matomo events show which features readers use. They carry fixed values only, never anything a reader types:

| Category | Action | Name |
| --- | --- | --- |
| Pathfinder | Show path, or Change answers (from a path page) | `situation/level` |
| Glossary | Open term, or Open panel | the term's ID |
| Checklist | Tick, Untick, Clear, Print worksheet | the section, such as `curate/check` |
| Tools | Filter | `task:checksums`, `platform:mac`, or `free` |
| Search | Search | none: once per page view, and the search terms are never sent |
| Feedback | Sent | none |

A Pathfinder event can be lost if the reader answers before Matomo finishes loading, because the browser moves straight to the path page. The path page's own view is always counted, so use page views for path counts and events for how readers got there.

- [x] In Matomo's settings: IPs anonymized to 2 bytes (also used for location lookups), and raw logs deleted after 395 days (about 13 months). Both are instance-wide settings, done Nov 17.
- [ ] Decide whether to filter out visits from before launch in the research report (or exclude the team's own visits).

## Domain

**`digipres.guide`** was registered November 17, 2026 through Cloudflare Registrar (about $32 a year, paid by APTrust). Set up in Phase 0:

1. **Verify the domain for the APTrust GitHub organization** (org settings, Pages). This stops anyone else's Pages site from claiming it.
2. **Point DNS at GitHub Pages.** Add A records for the apex to `185.199.108.153`, `.109.153`, `.110.153`, and `.111.153`, plus the matching AAAA records. Add a `www` CNAME to `aptrust.github.io`.
3. **Leave those records "DNS only"** (grey cloud) in Cloudflare, so GitHub can issue the HTTPS certificate. Turning on Cloudflare's proxy later is optional.
4. **Set the custom domain in the repo's Pages settings**, then turn on Enforce HTTPS once the certificate is issued.
5. **Set auto-renew** on the Cloudflare registration, so the domain doesn't lapse while CLIR's PDF points to it.

URLs then take the form `https://digipres.guide/curate/check/` and `https://digipres.guide/start/legacy-media/no-budget/`.

## Roles

| Who | Role |
| --- | --- |
| Nathan and Biz | Developer, accessibility testing, and maintenance after launch |
| Everyone | Path data authors, each owning one or more situations |
| Section authors | Review their own pages after each import: Chelsea and Nathan (LEARN, READY), Biz and Danielle (CURATE), John and Ginnie (PRESERVE), Martha (conclusion, glossary, further reading) |

Project meetings and scheduling stay with the team's existing coordinator.

## Risks

| Risk | Mitigation |
| --- | --- |
| Path data isn't done before the break | Start with the three situations already in the draft. Launch with the paths that are ready. |
| Final manuscript is late, or restructures sections | The import is a rerun, path links are checked at build time, and moved pages get redirects. A late manuscript shifts Phase 3a, and the URL list to CLIR moves with it. |
| CLIR requires its branding late | Get CLIR's answer by Dec 4. All styling lives in one theme file. |
| CLIR locks the PDF before our URLs are final | The domain is registered. URL list to CLIR by Jan 15. Ask CLIR now for their PDF lock date. |
| The domain lapses after the PDF is printed with its URLs | Auto-renew on, with renewal notices going to a shared APTrust address rather than one person |
| Spam through the feedback form | Honeypot field. If needed, switch to embedding Google's own form page. |
| The feedback form's owner leaves | The Form and Sheet live in an APTrust shared drive with two Managers (Nathan and Biz), so no one person's account holds them |
| Google Form field IDs change | Keep the form's questions fixed after launch. If one changes, update the matching field ID in the site's form. |
| Toolkit text goes public before the team is ready | The import writes only to `private/`, which git ignores. GitHub Actions never uses the private preview config. A red banner marks any private build. |
| Paths read as the one right answer | Framing copy on every path page, with the full toolkit always one click away |
| Tool listings go stale | Tools live in one data file. A scheduled link check runs in GitHub Actions. |
| Hugo removes a feature we use | Pin the exact Hugo version. Upgrade only on purpose, with a test build. |

## Open questions

- Is Pocket Burgundy branding required? (CLIR, by Dec 4)
- When does CLIR plan to publish, and when do they lock the PDF?
- Which content license? CC-BY-SA 4.0? Do we want CC-BY-NC-SA 4.0? (The code is GPL-3.0-or-later; this covers the text, glossary, and path data.)
- Confirm the winter break dates for each team member.
- How will section authors review their pages (Jan 11 to 22) while the text is private? Options: a screen-share walkthrough, a zipped private build sent to each author, or a password-protected preview host.
