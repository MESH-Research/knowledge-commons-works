import { ORCID } from "orcid-utils";

/**
 * Test if argument is a Research Organization Registry identifier.
 *
 * The ROR is a 9-character alphanumeric string. It can be in the
 * form of a URL or just the ROR. If the value to be tested is
 * not a string, the error message will be "ROR must be a string".
 *
 * This can be used as a yup validation method using the yup
 * addMethod function like this:
 *
 *   import { addMethod } from "yup";
 *   import { rorValidator } from "./validatorsForIds";
 *   addMethod(yup.string, "ror", rorValidator);
 *
 * Then you can use it in a schema like this:
 *
 *   import * as yup from "yup";
 *   const schema = yup.object().shape({
 *     ror: yup.string().ror("Invalid ROR identifier"),
 *   });
 *
 * If your schema does not provide a custom error message when
 * it calls the ror method, the default error message will be
 * "Invalid ROR identifier". Otherwise this is overridden by
 * the custom error message.
 *
 * @param {string} message
 * @returns either true or an error message
 */
function rorValidator(message) {
  return this.test("ror", message, function (val) {
    const { path, createError } = this;

    if (typeof val !== "string") {
      return createError({ path, message: "ROR identifier cannot be empty" });
    }

    const rorRegexp = new RegExp(
      "^(?:(?:https?://)?ror.org/)?(0\\w{6}\\d{2})$",
      "i"
    );
    // See https://ror.org/facts/#core-components.

    if (!rorRegexp.test(val)) {
      return createError({
        path,
        message: message ?? "Invalid ROR identifier",
      });
    }

    return true;
  });
}

/**
 * Test if argument is an International Standard Name Identifier.
 *
 * The ISNI is a 16-digit number which can be divided into four
 * blocks.
 *
 * This can be used as a yup validation method using the yup
 * addMethod function like this:
 *
 *  import { addMethod } from "yup";
 *  import { isniValidator } from "./validatorsForIds";
 *  addMethod(yup.string, "isni", isniValidator);
 *
 * Then you can use it in a schema like this:
 *
 *   import * as yup from "yup";
 *   const schema = yup.object().shape({
 *    isni: yup.string().isni("Invalid ISNI identifier"),
 *   });
 *
 * If your schema does not provide a custom error message when
 * it calls the isni method, the default error message will be
 * "Invalid ISNI identifier". Otherwise this is overridden by
 * the custom error message. The only exception is where the
 * ISNI is not a valid length, in which case the default error
 * message is "ISNI is not a valid length" and this will not be
 * overridden.
 *
 * @param {string} message
 * @returns either true or an error message
 */
function isniValidator(message) {
  return this.test("isni", message, function (val) {
    const { path, createError } = this;

    // Test if argument is an International Standard Name Identifier.
    const convertXTo10 = (x) => {
      // Convert char to int with X being converted to 10.
      return x !== "X" ? parseInt(x, 10) : 10;
    };

    val = val.replace(/-/g, "").replace(/ /g, "").toUpperCase();
    if (val.length !== 16) {
      return createError({
        path,
        message: message ?? "ISNI is not a valid length",
      });
    }

    try {
      let r = 0;
      for (let x of val.slice(0, -1)) {
        r = (r + parseInt(x, 10)) * 2;
      }
      const ck = (12 - (r % 11)) % 11;
      if (ck !== convertXTo10(val.slice(-1))) {
        return createError({
          path,
          message: message ?? "Invalid ISNI identifier",
        });
      }
    } catch (error) {
      return createError({
        path,
        message: message ?? "Invalid ISNI identifier",
      });
    }

    return true;
  });
}

/**
 * Test if argument is a Gemeinsame Normdatei identifier.
 *
 * The GND is a 10-digit number with an optional check digit.
 *
 * This can be used as a yup validation method using the yup
 * addMethod function like this:
 *
 *   import { addMethod } from "yup";
 *   import { gndValidator } from "./validatorsForIds";
 *   addMethod(yup.string, "gnd", gndValidator);
 *
 * Then you can use it in a schema like this:
 *
 *  import * as yup from "yup";
 *  const schema = yup.object().shape({
 *    gnd: yup.string().gnd("Invalid GND identifier"),
 *  });
 *
 * If your schema does not provide a custom error message when
 * it calls the gnd method, the default error message will be
 * "Invalid GND identifier". Otherwise this is overridden by
 * the custom error message.
 *
 * If the value to be tested starts with "http://d-nb.info/gnd/",
 * the prefix is ignored for validation.
 *
 * @param {string} message
 * @returns either true or an error message
 */
function gndValidator(message) {
  return this.test("gnd", message, function (val) {
    const { path, createError } = this;

    if (typeof val !== "string") {
      return createError({ path, message: "GND identifier cannot be empty" });
    }

    const gndResolverUrl = "http://d-nb.info/gnd/";

    if (val.startsWith(gndResolverUrl)) {
      val = val.slice(gndResolverUrl.length);
    }

    // GND must match one of these patterns:
    // 1. Start with 1 or 10 followed by 7 digits and a check digit (X or number)
    // 2. Start with 4 or 7 followed by 6 digits and a hyphen and a digit
    // 3. Start with 1-9 followed by 0-7 digits and a hyphen and a check digit (X or number)
    // 4. Start with 3 followed by 7 digits and a check digit (X or number)
    const gndRegexp = new RegExp(
      "^(?:(?:gnd:|GND:)?)?(" +
        "(?:1|10)\\d{7}[0-9X]|" +
        "(?:4|7)\\d{6}-\\d|" +
        "(?:[1-9])\\d{0,7}-[0-9X]|" +
        "(?:3)\\d{7}[0-9X]" +
        ")$"
    );

    if (!gndRegexp.test(val)) {
      return createError({ path, message: message ?? "Invalid GND" });
    }

    return true;
  });
}

/**
 * Test if argument is an ORCID.
 *
 * This can be used as a yup validation method using the yup
 * addMethod function like this:
 *
 *  import { addMethod } from "yup";
 *  import { orcidValidator } from "./validatorsForIds";
 *  addMethod(yup.string, "orcid", orcidValidator);
 *
 * Then you can use it in a schema like this:
 *
 *   import * as yup from "yup";
 *   const schema = yup.object().shape({
 *     orcid: yup.string().orcid("Invalid ORCID identifier"),
 *   });
 *
 * If your schema does not provide a custom error message when
 * it calls the orcid method, the default error message will be
 * "Invalid ORCID identifier". Otherwise this is overridden by
 * the custom error message.
 *
 * The ORCID can be in the form of a URL or just the ORCID. If
 * the value to be tested is not a string, the error message will
 * be "ORCID must be a string".
 *
 * @param {string} message
 * @returns
 */
function orcidValidator(message) {
  return this.test("orcid", message, function (val) {
    const { path, createError } = this;

    if (typeof val !== "string") {
      return createError({ path, message: "ORCID must be a string" });
    } else if (!ORCID.isValid(val)) {
      return createError({ path, message: message ?? "Invalid ORCID" });
    }

    return true;
  });
}

function sanitizeWPUsername(username, strict = false) {
  let rawUsername = username;

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
 * Test if argument is a valid Knowledge Commons username.
 *
 * Returns true if the username is unchanged after it is passed through
 * the sanitizeWPUsername function, otherwise returns an error message.
 *
 * This can be used as a yup validation method using the yup
 * addMethod function like this:
 *
 * import { addMethod } from "yup";
 * import { kcUsernameValidator } from "./validatorsForIds";
 * addMethod(yup.string, "kc_username", kcUsernameValidator);
 *
 * Then you can use it in a schema like this:
 *
 * import * as yup from "yup";
 * const schema = yup.object().shape({
 *   kc_username: yup.string().kc_username("Invalid Knowledge Commons username"),
 * });
 *
 * If your schema does not provide a custom error message when
 * it calls the kc_username method, the default error message will be
 * "Invalid Knowledge Commons username". Otherwise this is overridden by
 * the custom error message.
 *
 * @param {string} message
 * @returns either true or an error message
 */
function kcUsernameValidator(message) {
  return this.test("kc_username", message, function (val) {
    const { path, createError } = this;

    if (typeof val !== "string") {
      return createError({ path, message: "KC username cannot be empty" });
    }

    // Check minimum length first
    if (val.length < 3) {
      return createError({
        path,
        message: message ?? "Username must be at least 3 characters long",
      });
    }

    // Sanitize the username
    const sanitizedUsername = sanitizeWPUsername(val, true);

    // Check if the sanitized username matches the original
    if (sanitizedUsername !== val) {
      return createError({
        path,
        message: message ?? "Username contains invalid characters",
      });
    }

    // Only allow alphanumeric characters, dots, underscores, hyphens, and @ for email addresses
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

export {
  gndValidator,
  isniValidator,
  kcUsernameValidator,
  orcidValidator,
  rorValidator,
};
