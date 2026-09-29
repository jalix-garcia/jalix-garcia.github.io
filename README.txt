Jennifer Alix-García personal website
=====================================

A Quarto website. Every publication list on the site is generated from a single
file, data/publications.toml, so a paper only ever needs to be entered once.


FOLDER LAYOUT

  _quarto.yml               Site settings: navigation bar, footer, theme.
  index.qmd                 Home page (bio, profile links, research themes, recent papers).
  publications.qmd          All publications, grouped by theme.
  work-in-progress.qmd      Working papers.
  teaching.qmd              Syllabi and advisees. Edited directly (not generated).
  styles.scss               Fonts, colors, and layout.
  favicon.svg               Browser-tab icon.
  data/publications.toml    THE publication list. Field guide at the top of the file.
  scripts/build_pages.py    Turns publications.toml into page content. Runs
                            automatically before every render.
  images/                   Headshot and the four research-theme photos. Theme photos
                            are set per theme in publications.toml (image, image_alt,
                            image_focus); they appear on the home-page cards and as
                            banners on the publications page. Keep them around
                            1000 pixels wide and under about 300 KB.
  images/pubs/              Figure thumbnails for "Recent publications" on the home
                            page, set per paper with thumbnail / thumbnail_alt in
                            publications.toml. Most came from the papers' Overleaf
                            Figures folders (Dropbox/Apps/Overleaf). About 700
                            pixels wide, white margins trimmed.
  files/Alix-Garcia-CV.pdf  The CV. Keep this file name so the link never changes.
  files/papers/             Manuscript PDFs.
  files/syllabi/            Syllabus PDFs.

  Not part of the site (ignored by git):
  _site/                    The rendered website. This is what gets published.
  _generated/               Intermediate files written by build_pages.py.
  incoming/                 The original PDFs downloaded from Google Drive. Safe to
                            delete once you are happy with the site.


COMMON UPDATES

Add a new paper
  Open data/publications.toml and copy an existing [[pub]] block. Fill in title,
  with, venue, citation, year, doi, theme and type. Add featured = true and a
  summary if it should appear under "Recent publications" on the home page.
  When a forthcoming paper comes out, fill in citation and delete forthcoming.

Move a working paper to publications
  Change its type from "wip" to "article" and add venue, year, doi and theme.
  Remove status.

Update the CV
  Replace files/Alix-Garcia-CV.pdf with the new PDF, using the same file name.

Add a manuscript or syllabus PDF
  Put it in files/papers/ or files/syllabi/, then point to it from
  publications.toml (manuscript = "files/papers/...") or teaching.qmd.

The build stops with a readable message if an entry has a typo in a field name,
an unknown theme, or a manuscript path that does not exist.


PREVIEW AND RENDER

Quarto on this machine comes bundled with RStudio and is not on the PATH:

  "C:\Program Files\RStudio\resources\app\bin\quarto\bin\quarto.exe" preview

Run that from this folder. It opens the site in a browser and reloads as you
edit the .qmd files. After editing publications.toml, stop and restart preview
so the lists are rebuilt. Use "render" instead of "preview" to rebuild _site/
without opening a browser.

The build script needs Python 3.11 or newer (for tomllib). Nothing else to
install.


PUBLISHING

The live site is https://jalix-garcia.github.io, served by GitHub Pages from the
repository https://github.com/jalix-garcia/jalix-garcia.github.io.

  main branch       The source files in this folder.
  gh-pages branch   The rendered site. Written by Quarto; never edit it by hand.

To put changes online, run these from this folder:

  git add -A
  git commit -m "Describe the change"
  git push
  "C:\Program Files\RStudio\resources\app\bin\quarto\bin\quarto.exe" publish gh-pages --no-browser

The last command re-renders the site and pushes it to the gh-pages branch. The
live site updates a minute or two later.
