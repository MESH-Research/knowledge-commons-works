/**
 * Webpack/rspack alias target for ``tinymce/tinymce``.
 *
 * Self-hosted TinyMCE 8+ requires ``license_key`` or editors mount read-only.
 * ``react-invenio-forms`` and other Invenio bundles ``require("tinymce/tinymce")``
 * without passing a key. This shim loads the real package entry (``tinymce``,
 * which does **not** hit the ``tinymce/tinymce`` alias) and sets GPL defaults for
 * every subsequent ``init``.
 *
 * Must use ESM ``export default``: TinyMCE 8 is an ES module, and the bundler's
 * ESM interop forbids ``module.exports =`` on that graph
 * (``ES Modules may not assign module.exports``).
 *
 * Skins: TinyMCE HTTP-loads ``{baseURL}/skins/.../skin${suffix}.css`` (and
 * content CSS the same way). TinyMCE 6 hard-coded ``.min``; TinyMCE 8 derives
 * ``suffix`` from a ``tinymce*.min.js`` script tag, which webpack chunks do not
 * provide — so ``suffix`` stays empty and it requests ``skin.css`` /
 * ``content.css``. Set ``suffix: ".min"`` to restore the 6.x filenames.
 *
 * Paragraph styles: ``RichEditor`` always passes its own ``content_style``, which
 * replaces defaults — so we inject into each editor iframe on ``init`` instead.
 *
 * Paired with ``scripts/patch-webpack-assets-tinymce.py``, which bumps the generated
 * assets ``package.json`` to TinyMCE 8.9.3+ / ``@tinymce/tinymce-react`` ^6.3 so the
 * install matches this shim.
 */

import tinymce from "tinymce";

const gplDefaults = {
  license_key: "gpl",
  // Match TinyMCE 6 bundled behavior: request *.min.css under baseURL/skins/...
  suffix: ".min",
};

/** Injected into every editor content iframe (survives RichEditor content_style). */
const PARAGRAPH_CONTENT_STYLE = "p { font-size: 1rem; line-height: 1.25em; }";
const PARAGRAPH_STYLE_ELEMENT_ID = "kcworks-richeditor-p-style";

/**
 * @param {import("tinymce").Editor} editor
 */
function injectParagraphStyles(editor) {
  editor.on("init", () => {
    const doc = editor.getDoc();
    if (!doc?.head || doc.getElementById(PARAGRAPH_STYLE_ELEMENT_ID)) {
      return;
    }
    const style = doc.createElement("style");
    style.id = PARAGRAPH_STYLE_ELEMENT_ID;
    style.textContent = PARAGRAPH_CONTENT_STYLE;
    doc.head.appendChild(style);
  });
}

if (typeof tinymce.overrideDefaults === "function") {
  tinymce.overrideDefaults({
    ...(tinymce.defaultOptions || {}),
    ...gplDefaults,
  });
} else {
  tinymce.defaultOptions = {
    ...(tinymce.defaultOptions || {}),
    ...gplDefaults,
  };
  if (gplDefaults.suffix) {
    tinymce.suffix = gplDefaults.suffix;
  }
}

if (typeof tinymce.on === "function") {
  tinymce.on("AddEditor", (event) => {
    if (event?.editor) {
      injectParagraphStyles(event.editor);
    }
  });
}

export default tinymce;
