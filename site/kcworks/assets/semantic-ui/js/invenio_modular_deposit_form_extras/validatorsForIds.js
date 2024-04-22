import { ORCID } from "orcid-utils";

const rorValidator = function (val) {
  // Test if argument is a ROR ID.
  const rorRegexp = new RegExp(
    "(?:https?://)?(?:ror\\.org/)?(0\\w{6}\\d{2})$",
    "i"
  );
  // See https://ror.org/facts/#core-components.
  return rorRegexp.test(val);
};

const isniValidator = (val) => {
  // Test if argument is an International Standard Name Identifier.
  const convertXTo10 = (x) => {
    // Convert char to int with X being converted to 10.
    return x !== "X" ? parseInt(x, 10) : 10;
  };

  val = val.replace(/-/g, "").replace(/ /g, "").toUpperCase();
  if (val.length !== 16) {
    return false;
  }
  try {
    let r = 0;
    for (let x of val.slice(0, -1)) {
      r = (r + parseInt(x, 10)) * 2;
    }
    const ck = (12 - (r % 11)) % 11;
    return ck === convertXTo10(val.slice(-1));
  } catch (error) {
    return false;
  }
};

const gndValidator = (val) => {
  // Test if argument is a GND ID.
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

  return gndRegexp.test(val);
};

const orcidValidator = (val) => {
  // const orcidUrls = ["http://orcid.org/", "https://orcid.org/"];
  // const orcidIsniRanges = [
  //   (15000000, 35000000),
  //   (900000000000, 900100000000),
  // ];
  // // Valid ORCiD ISNI block ranges.

  // See
  //     https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier

  // Test if argument is an ORCID ID.
  // See http://support.orcid.org/knowledgebase/
  // articles/116780-structure-of-the-orcid-identifier

  // for (let orcidUrl of orcidUrls) {
  //   if (val.startsWith(orcidUrl)) {
  //     val = val.slice(orcidUrl.length);
  //     break;
  //   }
  // }

  // val = val.replace(/-/g, "").replace(/ /g, "");
  // if (isIsni(val)) {
  //   val = parseInt(val.slice(0, -1), 10); // Remove check digit and convert to int.
  //   return orcidIsniRanges.some(
  //     ([start, end]) => start <= val && val <= end
  //   );
  // }
  if (ORCID.isValid(val)) {
    return true;
  }
  return false;
};

export { gndValidator, isniValidator, orcidValidator, rorValidator };
