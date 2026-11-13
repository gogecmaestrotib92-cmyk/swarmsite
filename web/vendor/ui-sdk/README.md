# UI SDK (vendored)

`@ui-sdk/web` 0.1.0-beta.1 — the `browser` folder of the npm package, copied as it is (Apache-2.0, see LICENSE).
Vercel's library of interface behaviours as web components: https://github.com/vercel-labs/ui

`web.js` loads each component the first time its tags appear on a page; it and the `web` folder stay side by side.
Used by `web/edit.html` (tabs, the download dialog). Its stylesheet (`web.css`) is not used: the parts are styled by ours.

To update: `npm pack @ui-sdk/web@<version>`, replace `web.js` and `web/` with the package's `browser/web.js` and `browser/web/`,
change the version above, run `tests/edit-page.mjs`. It is a beta: read its changelog before updating.
