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

    const rorRegexp = new RegExp(
      "(?:https?://)?(?:ror\\.org/)?(0\\w{6}\\d{2})$",
      "i"
    );
    // See https://ror.org/facts/#core-components.

    if (typeof val !== "string") {
      return createError({ path, message: "ROR must be a string" });
    } else if (!rorRegexp.test(val)) {
      return createError({ path, message: message ?? "Invalid ROR identifier" });
    }

    return true;
  });
};

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
      return createError({ path, message: message ?? "ISNI is not a valid length" });
    }

    try {
      let r = 0;
      for (let x of val.slice(0, -1)) {
        r = (r + parseInt(x, 10)) * 2;
      }
      const ck = (12 - (r % 11)) % 11;
      if (ck !== convertXTo10(val.slice(-1))) {
        return createError({ path, message: message ?? "Invalid ISNI identifier" });
      };
    } catch (error) {
      return createError({ path, message: message ?? "Invalid ISNI identifier" });
    }

    return true;
  });
};

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

    const gndResolverUrl = "http://d-nb.info/gnd/";

    const gndRegexp = new RegExp(
      "(gnd:|GND:)?(" +
        "(1|10)\\d{7}[0-9X]|" +
        "[47]\\d{6}-\\d|" +
        "[1-9]\\d{0,7}-[0-9X]|" +
        "3\\d{7}[0-9X]" +
        ")"
    );
    // See https://www.wikidata.org/wiki/Property:P227.

    if (val.startsWith(gndResolverUrl)) {
      val = val.slice(gndResolverUrl.length);
    }

    if (typeof val !== "string") {
      return createError({ path, message: "GND must be a string" });
    } else if (!gndRegexp.test(val)) {
      return createError({ path, message: message ?? "Invalid GND" });
    }

    return true;
  });
};

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
};

export { gndValidator, isniValidator, orcidValidator, rorValidator };
