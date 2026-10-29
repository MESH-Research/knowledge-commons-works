/*
 * KCWorks PDF preview load progress.
 *
 * Wraps pdfjsLib.getDocument before upstream open_pdf.js runs so the existing
 * #loadingBar in pdfjs.html reflects download progress. Prefer the record file
 * size (pdf-file-size) when pdf.js does not report a total.
 */

/**
 * @param {HTMLElement} bar
 * @param {number} loaded
 * @param {number} total
 * @param {number} knownSize
 */
function setProgress(bar, loaded, total, knownSize) {
  const denom = total > 0 ? total : knownSize;
  if (!(denom > 0) || !(loaded >= 0)) {
    bar.classList.add("indeterminate");
    return;
  }
  bar.classList.remove("indeterminate");
  const pct = Math.min(100, Math.round((100 * loaded) / denom));
  bar.style.setProperty("--progressBar-percent", `${pct}%`);
}

/**
 * @param {HTMLElement} bar
 */
function showBar(bar) {
  bar.hidden = false;
  bar.removeAttribute("hidden");
  bar.classList.remove("hidden");
  bar.setAttribute("aria-hidden", "false");
}

/**
 * @param {HTMLElement} bar
 */
function hideBar(bar) {
  bar.hidden = true;
  bar.setAttribute("hidden", "hidden");
  bar.classList.add("hidden");
  bar.setAttribute("aria-hidden", "true");
}

document.addEventListener("DOMContentLoaded", () => {
  const lib = window.pdfjsLib;
  const bar = document.getElementById("loadingBar");
  const sizeInput = document.getElementById("pdf-file-size");
  const knownSize = Number(sizeInput?.value || 0);

  if (!lib || typeof lib.getDocument !== "function" || !bar) {
    return;
  }

  const originalGetDocument = lib.getDocument.bind(lib);

  lib.getDocument = (src) => {
    const task = originalGetDocument(src);
    showBar(bar);
    setProgress(bar, 0, 0, knownSize);

    task.onProgress = ({ loaded, total }) => {
      setProgress(bar, loaded, total, knownSize);
    };

    const finish = () => {
      if (knownSize > 0) {
        setProgress(bar, knownSize, knownSize, knownSize);
      }
      hideBar(bar);
    };

    task.promise.then(finish, finish);
    return task;
  };
});
