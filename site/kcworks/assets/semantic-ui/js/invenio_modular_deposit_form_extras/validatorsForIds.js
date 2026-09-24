// Part of KCWorks
//
// KC-only Yup identifier validators. Stock schemes (ORCID, ROR, GND, ISNI, …) live in
// invenio-modular-deposit-form `validation/validatorsForIds.js`.

function sanitizeWPUsername(username, strict = false) {
  // Remove HTML tags
  username = username.replace(/<\/?[^>]+(>|$)/g, "");

  // Remove accents
  username = username.normalize("NFD").replace(/[\u0300-\u036f]/g, "");

  // Remove percent-encoded characters
  username = username.replace(/%[a-fA-F0-9]{2}/g, "");

  // Remove HTML entities
  username = username.replace(/&[^;]+;/g, "");

  // If strict, reduce to ASCII for max portability
  if (strict) {
    username = username.replace(/[^a-z0-9 _.\-@]/gi, "");
  }

  // Remove all whitespace
  username = username.replace(/\s+/g, "");

  return username;
}

/**
 * Yup test: valid Knowledge Commons username (aligned with WP-style sanitization rules).
 *
 * @param {string} [message] - Override default error message for invalid characters / length
 */
function kcUsernameValidator(message) {
  return this.test("kc_username", message, function (val) {
    const { path, createError } = this;

    if (typeof val !== "string") {
      return createError({ path, message: "KC username cannot be empty" });
    }

    if (val.length < 3) {
      return createError({
        path,
        message: message ?? "Username must be at least 3 characters long",
      });
    }

    const sanitizedUsername = sanitizeWPUsername(val, true);

    if (sanitizedUsername !== val) {
      return createError({
        path,
        message: message ?? "Username contains invalid characters",
      });
    }

    const usernameRegex = /^[a-zA-Z0-9._@-]+$/;

    if (!usernameRegex.test(val)) {
      return createError({
        path,
        message: message ?? "Invalid Knowledge Commons username",
      });
    }

    return true;
  });
}

export { kcUsernameValidator };
