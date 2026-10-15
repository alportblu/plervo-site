# Plervo Suite web direction

Light editorial product site. Original Plervo identity: ink #192721, paper #f7f8f4, lime #cae862. Inter is self-hosted under OFL-1.1 (license in public/assets/OFL-Inter.txt), sourced from the already attributed Plervo PDF font assets. No trackers, remote fonts, component service or animation dependency.

Research: UI/UX Pro Max (https://github.com/nextlevelbuilder/ui-ux-pro-max-skill), tenfoldmarc setup (https://github.com/tenfoldmarc/website-builder-setup), 21st MCP (https://github.com/21st-dev/magic-mcp), Motion (https://github.com/motiondivision/motion). The installed UI/UX Pro Max 2.2.3 was consulted for typography, contrast, hierarchy and responsive checks. React-specific tooling was not added to this static Python/HTML/CSS site.

Composition: type-led hero, real Suite screenshot, numbered installation flow, one honest product entry, high-contrast download area, security details and voluntary support. No fabricated testimonials, customer counts or unavailable apps. English default; Portuguese and Spanish preserve the current page.

Suite screenshot: original Plervo UI rendered with Inter and egui's open fonts, without system fonts or personal documents. Capture is generated from the app, not a design mockup. Download configuration is updated only after signed artifacts pass validation.

Deployment: the build gives CSS, JavaScript, the brand mark and the Suite preview content-based filenames. Returning visitors receive matching HTML and assets even when the browser retains a previous release's files.

Responses use `no-transform` to prevent proxy-injected analytics, with cache revalidation to keep the published HTML current. The final custom-domain HTML must match the built file. This follows [Cloudflare's documented opt-out from beacon injection](https://developers.cloudflare.com/web-analytics/get-started/); the restrictive CSP stays in place.
