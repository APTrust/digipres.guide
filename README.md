# Digital Preservation Toolkit website

Source for **[digipres.guide](https://digipres.guide)**, the website for *Digital Preservation Appraisal & Selection: Toolkit for Organizations with Limited Resources*. The toolkit is being published by CLIR in its Pocket Burgundy series, and CLIR will produce the official PDF.

The website presents the same content in a form people can use while they work. A pathfinder asks what you're working with and what you can put toward it, then shows the steps, tools, and toolkit sections that matter most for your situation. The full toolkit is always one click away. It's organized in four phases:

- **LEARN:** understanding digital preservation concepts and risks
- **READY:** organizational development and preparation
- **CURATE:** first preservation actions
- **PRESERVE:** long-term preservation practices

> **Status:** in development. A placeholder site is in place; content arrives in January 2027. We expect to launch the week of February 15, 2027.

## What's here

| Path | What it is |
| --- | --- |
| [`planning/project-plan.md`](planning/project-plan.md) | The project plan: decisions, schedule, roles, risks, and open questions |
| [`planning/path-data-template.xlsx`](planning/path-data-template.xlsx) | A blank template for the pathfinder's data: situations, levels, steps, tools, and storage options |
| [`planning/path-data-draft.xlsx`](planning/path-data-draft.xlsx) | The same template, pre-filled from the November 10 draft so the team can review it |
| [`concepts/site-concepts.html`](concepts/site-concepts.html) | The three design concepts the team chose between. We chose Concept C, "Start Where You Are." |
| `content/` | The site's pages, in Markdown. Section pages are placeholders until the manuscript is imported. |
| `content/start/` | The pathfinder. Its pages are generated from `data/paths.yaml`, one per situation and resource level. |
| `data/` | Generated from the path data sheet and the manuscript's glossary. Don't edit by hand. |
| [`scripts/convert_path_data.py`](scripts/convert_path_data.py) | Converts the path data sheet (.xlsx) into the files in `data/` and checks every reference |
| [`scripts/import_manuscript.py`](scripts/import_manuscript.py) | Imports the manuscript (.docx) into one page per section, in `private/` until launch. Needs pandoc. |
| [`scripts/import_glossary.py`](scripts/import_glossary.py) | Imports the glossary appendix from a manuscript draft (.docx) into `data/glossary.yaml`. Needs pandoc. |
| `layouts/`, `assets/` | Hugo templates, CSS, and the pathfinder's small script. The CSS is a placeholder until the design phase. |
| `hugo.toml` | Site settings, including the `launched` switch |

Manuscript drafts are kept in `content-drafts/`, and their imported text in `private/`. Git ignores both folders, so the toolkit text isn't published in this repository until launch.

## How the site will work

- **[Hugo](https://gohugo.io/)** builds the static site. GitHub Actions uses one pinned version of Hugo, and the site is published on GitHub Pages.
- **Content** is plain Markdown, one page per toolkit section, imported from the manuscript with pandoc.
- **Path data** is edited by the team in a Google Sheet. A converter turns it into YAML files in `data/`, and the build fails if a path points to a section, tool, or level that doesn't exist.
- **Search** uses [Pagefind](https://pagefind.app/).
- **JavaScript** is a small amount of hand-written code, with no frameworks or libraries. Every pathfinder result is also a static page at `/start/<situation>/<level>/`, so the site works without JavaScript.
- **Accessibility** target: WCAG 2.2 AA.
- **Analytics:** Matomo, without cookies and with IP addresses anonymized.

## Updating the pathfinder

The team edits the path data in a Google Sheet. To publish changes:

1. In Google Sheets, choose **File → Download → Microsoft Excel (.xlsx)**.
2. From the repository root, run:

   ```bash
   python3 scripts/convert_path_data.py ~/Downloads/path-data.xlsx --stubs
   ```

   If anything in the sheet doesn't match (for example, a step names a tool that isn't on the Tools tab), it lists each problem by tab and row and changes nothing. Fix those in the sheet and download again.
3. Commit the changed files in `data/` and push.

`--stubs` adds a placeholder page for any new section on the Sections tab. It never changes existing pages.

## Importing the manuscript

The toolkit text is imported from the manuscript, but it stays private until launch:

```bash
python3 scripts/import_manuscript.py content-drafts/<draft>.docx
hugo server --config hugo.toml,hugo.private.toml
```

The first command writes one page per section to `private/`, which git ignores. The second previews the full site locally, with a red "Private preview" banner. The public build never includes `private/`. At launch, run the import with `--out content` to write the pages into the site itself.

## Updating the glossary

The glossary comes from the manuscript's glossary appendix. When a new draft arrives, run:

```bash
python3 scripts/import_glossary.py content-drafts/<new-draft>.docx
```

Then commit `data/glossary.yaml`. Each term is a Heading 1 in the manuscript, with one Heading 2 per source ("DPC Glossary", "SAA Dictionary", or "FADGI Glossary").

## Building and previewing

Every push to `main` builds the site and deploys it to GitHub Pages ([`.github/workflows/deploy.yml`](.github/workflows/deploy.yml)). Pull requests run the same build without deploying, so mistakes show up before they merge.

The Hugo and Pagefind versions are pinned in the workflow. To preview locally, install the same Hugo version (see `HUGO_VERSION` in the workflow; `hugo.toml` refuses anything older), then run this from the repository root:

```bash
hugo server
```

Then open <http://localhost:1313/>. Search only works in a full build:

```bash
hugo build && pagefind --site public
```

Until launch, `launched = false` in `hugo.toml` puts a preview banner on every page and tells search engines not to index the site. Set it to `true` on launch day.

## Feedback

Once the site is live, use the feedback form on any page. You don't need a GitHub account. Team members can also open an issue in this repository.

## Credits and license

The toolkit is written by a team of digital preservation practitioners. The site is built and maintained by APTrust.

License: to be decided. See the open questions in the [project plan](planning/project-plan.md#open-questions).
