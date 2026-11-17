# Digital Preservation Toolkit website

Source for **[digipres.guide](https://digipres.guide)**, the website for *Digital Preservation Appraisal & Selection: Toolkit for Organizations with Limited Resources*. The toolkit is being published by CLIR in its Pocket Burgundy series, and CLIR will produce the official PDF.

The website presents the same content in a form people can use while they work. A pathfinder asks what you're working with and what you can put toward it, then shows the steps, tools, and toolkit sections that matter most for your situation. The full toolkit is always one click away. It's organized in four phases:

- **LEARN:** understanding digital preservation concepts and risks
- **READY:** organizational development and preparation
- **CURATE:** first preservation actions
- **PRESERVE:** long-term preservation practices

> **Status:** planning. The site is not built yet. We expect to launch the week of February 15, 2027.

## What's here

| Path | What it is |
| --- | --- |
| [`planning/project-plan.md`](planning/project-plan.md) | The project plan: decisions, schedule, roles, risks, and open questions |
| [`planning/path-data-template.xlsx`](planning/path-data-template.xlsx) | A blank template for the pathfinder's data: situations, levels, steps, tools, and storage options |
| [`planning/path-data-draft.xlsx`](planning/path-data-draft.xlsx) | The same template, pre-filled from the November 10 draft so the team can review it |
| [`concepts/site-concepts.html`](concepts/site-concepts.html) | The three design concepts the team chose between. We chose Concept C, "Start Where You Are." |

Manuscript drafts are kept in `content-drafts/`, which git ignores. They are not published in this repository.

## How the site will work

- **[Hugo](https://gohugo.io/)** builds the static site. GitHub Actions uses one pinned version of Hugo, and the site is published on GitHub Pages.
- **Content** is plain Markdown, one page per toolkit section, imported from the manuscript with pandoc.
- **Path data** is edited by the team in a Google Sheet. A converter turns it into YAML files in `data/`, and the build fails if a path points to a section, tool, or level that doesn't exist.
- **Search** uses [Pagefind](https://pagefind.app/).
- **JavaScript** is a small amount of hand-written code, with no frameworks or libraries. Every pathfinder result is also a static page at `/start/<situation>/<level>/`, so the site works without JavaScript.
- **Accessibility** target: WCAG 2.2 AA.
- **Analytics:** Matomo, without cookies and with IP addresses anonymized.

When the site is built, this section will explain how to preview it locally and how deploys work.

## Feedback

Once the site is live, use the feedback form on any page. You don't need a GitHub account. Team members can also open an issue in this repository.

## Credits and license

The toolkit is written by a team of digital preservation practitioners. The site is built and maintained by APTrust.

License: to be decided. See the open questions in the [project plan](planning/project-plan.md#open-questions).
