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
| `content/` | The site's pages, in Markdown. For now, one placeholder page per phase. |
| `layouts/`, `assets/` | Hugo templates and CSS. The CSS is a placeholder until the design phase. |
| `hugo.toml` | Site settings, including the `launched` switch |

Manuscript drafts are kept in `content-drafts/`, which git ignores. They are not published in this repository.

## How the site will work

- **[Hugo](https://gohugo.io/)** builds the static site. GitHub Actions uses one pinned version of Hugo, and the site is published on GitHub Pages.
- **Content** is plain Markdown, one page per toolkit section, imported from the manuscript with pandoc.
- **Path data** is edited by the team in a Google Sheet. A converter turns it into YAML files in `data/`, and the build fails if a path points to a section, tool, or level that doesn't exist.
- **Search** uses [Pagefind](https://pagefind.app/).
- **JavaScript** is a small amount of hand-written code, with no frameworks or libraries. Every pathfinder result is also a static page at `/start/<situation>/<level>/`, so the site works without JavaScript.
- **Accessibility** target: WCAG 2.2 AA.
- **Analytics:** Matomo, without cookies and with IP addresses anonymized.

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
