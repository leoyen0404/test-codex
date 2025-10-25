# test-codex

This repository exposes a tiny static homepage that showcases the "classified"
projects that live inside the repo. A helper script keeps the homepage navigator
in sync with any project directories added under `projects/`.

## Project structure

```
.
├── index.html                 # Homepage with the Classified Projects navigator
├── projects/                  # Each subdirectory represents a project
│   └── <project>/project.json # Metadata that powers the navigator entry
└── scripts/update_homepage.py # Script that rewrites the homepage navigation
```

A sample project (`projects/example-project/`) has been included to demonstrate
how the updater works.

## Adding a new project

1. Create a directory inside `projects/` using a URL-friendly slug. For example
   `projects/new-analysis/`.
2. Add a `project.json` file containing metadata that will power the navigator
   entry:

   ```json
   {
     "name": "New Analysis",
     "description": "Short blurb that appears underneath the link on the homepage.",
     "url": "projects/new-analysis/index.html"
   }
   ```

   The `url` can point to any location—typically the project's README or
   dedicated landing page inside the repository.
3. Optionally add whatever project assets or documentation you need in the new
   directory.
4. Run the updater to refresh the homepage navigation:

   ```bash
   python scripts/update_homepage.py
   ```

   Use `--dry-run` to preview the generated markup before writing to the
   homepage:

   ```bash
   python scripts/update_homepage.py --dry-run
   ```

The navigation is rewritten between the `<!-- PROJECT_NAV_START -->` and
`<!-- PROJECT_NAV_END -->` markers inside `index.html`. This makes it safe to run
whenever new projects are introduced—the rest of the page remains untouched.
