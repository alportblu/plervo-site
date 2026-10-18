# Plervo website

The official website for **Plervo Suite**, an open-source family of desktop apps for documents, design and media. Visitors can explore the apps, download the Suite for their computer, read security information and optionally support **AlporT**.

**Live site:** [plervo.com](https://plervo.com) · **App source and releases:** [alportblu/plervo-pdf](https://github.com/alportblu/plervo-pdf) · **Optional support:** [Buy Me a Coffee](https://buymeacoffee.com/alport)

## Run locally

This is a standalone static site built with Python, HTML and CSS, plus a local JavaScript module that suggests the appropriate download platform.

```sh
python3 build.py
python3 -m unittest -v
node --test tests/downloads.test.mjs
python3 -m http.server 4173 --bind 127.0.0.1 --directory dist
```

There are no analytics, cookies or external widgets. Platform detection uses basic information already exposed by the browser, does not transmit it and never starts a download automatically. All three platform options remain visible; phones and tablets receive a message explaining that the apps are for desktop computers. Detection does not assume the processor architecture.

## Hosting and checks

The site runs on Cloudflare Pages Free at https://plervo.com, https://www.plervo.com and https://plervo-site.pages.dev, using Direct Upload of the `dist` directory. The domain remains registered with GoDaddy; DNS is managed by Cloudflare. Both custom domains have been verified over HTTPS.

The `Plervo site checks` workflow checks generation, links, download safeguards and platform suggestions on every push and pull request. The protected `main` branch requires a pull request and this passing check, including for administrators.

## Public downloads

The main download is **Plervo Suite 0.1.0-alpha.4**, for Mac with Apple Silicon or Linux x86_64. Install the Suite first, then choose apps from its catalog.

All 13 apps are available on both platforms: PDF, Photo, Vector, Video, Develop, Motion, Publish, Write, Slides, Sheets, CAD, Audio and Canvas. Slides and Audio have English-only interfaces in this alpha. Mac packages are signed and notarized. Linux offers DEB and RPM packages and requires glibc 2.39 or newer; the Suite's declared dependencies include ALSA for multimedia apps.

Windows awaits SignPath approval, signing integration and validation of the final signed packages. All 13 internal candidates passed native installation, repair/removal, representative command-line operations, and normal GUI startup/close checks.

Public app downloads are tested through the Suite's actual installation components in isolated destinations, including reinstallation. Linux also checks removal and preservation of synthetic files. Local Linux checks use emulated x86_64 containers in addition to native acceptance recorded in CI.

This is an experimental alpha. Final Mac GUI acceptance, installation on a clean Mac, audio hardware, external plugins and wider device coverage remain outside the completed validation. See the [release notes](https://github.com/alportblu/plervo-pdf/releases/tag/v0.1.0-alpha.4) for current limits.

## Download configuration

`config.json` controls public links. Publish the site only after the matching release can be downloaded anonymously and the Suite has verified management of every advertised app. Never add placeholder links, unvalidated packages or a nonexistent stable release.

The generator requires a SHA-256 checksum, an official repository URL, explicit validation and publisher signing for Mac/Windows. Mac also requires notarization. A direct PDF package, or one with a mismatched version or platform, is rejected as the main download.

Each qualified download's `products` field controls app availability. Older releases without this field offer PDF only. DEB and RPM packages for the same version must list the same products. Add a product only after publishing and verifying its package and Suite management on that platform. Until then, its card says “In validation,” without promising installation. Slides and Audio identify their English-only interfaces.

## Languages

The root URL `/` always opens in English, without redirecting based on browser language. The header selector opens the same page in English, Portuguese (`/pt/`) or Spanish (`/es/`). Navigation preserves the language through the URL, without cookies, local storage or additional JavaScript.

Support, security, privacy, credits and 404 pages are translated. Legacy Portuguese paths redirect to `/pt/`. Metadata, canonical URLs, hreflang and the sitemap follow each language. Text lives in `locales/{en,pt,es}.json`; matching key coverage is required.

## Security and optional support

The `/security/` page and its translations point to the private GitHub reporting channel enabled in `alportblu/plervo-pdf`. The site does not receive the reports' contents.

The owner-provided support destination is https://buymeacoffee.com/alport. Public creator credit uses **AlporT**. The `/support/` page and its translations open the service only when the visitor chooses the link. There are no banking details, service tokens or private keys in this project.

## Design and attribution

The SVG identity, layout and Suite screenshot are original Plervo work. The current image shows Suite alpha.4 running natively on Ubuntu 24.04, captured by the [acceptance CI](https://github.com/alportblu/plervo-pdf/actions/runs/39001993059) from source `4da05339d4f6f6715d09f0622975b8164be7f480`.

Inter Regular and SemiBold are served locally under OFL-1.1, with the license included, and come from the already attributed Plervo PDF assets. No Adobe or ArtCraft artwork is included. The app catalog uses the original, attributed Plervo icon family; sources, hashes and licenses are in `public/assets/products/`. The visual direction and research are documented in [DESIGN.md](DESIGN.md).
