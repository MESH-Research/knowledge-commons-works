import {
  addMethod,
  array as yupArray,
  boolean as yupBoolean,
  object as yupObject,
  string as yupString,
  date as yupDate,
} from "yup";

import { rorValidator } from "./validatorsForIds";

addMethod(yupString, "ror", function () {
  return this.test("test-name", rorValidator);
});

addMethod(yupString, "gnd", function () {
  return this.test("test-name", function (val) {
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
  });
});

const isIsni = (val) => {
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

const orcidUrls = ["http://orcid.org/", "https://orcid.org/"];
const orcidIsniRanges = [
  (15_000_000, 35_000_000),
  (900_000_000_000, 900_100_000_000),
];
// Valid ORCiD ISNI block ranges.

// See
//     https://support.orcid.org/hc/en-us/articles/360006897674-Structure-of-the-ORCID-Identifier

addMethod(yupString, "orcid", function () {
  return this.test("test-name", function (val) {
    // Test if argument is an ORCID ID.
    // See http://support.orcid.org/knowledgebase/
    // articles/116780-structure-of-the-orcid-identifier

    for (let orcidUrl of orcidUrls) {
      if (val.startsWith(orcidUrl)) {
        val = val.slice(orcidUrl.length);
        break;
      }
    }

    val = val.replace(/-/g, "").replace(/ /g, "");
    if (isIsni(val)) {
      val = parseInt(val.slice(0, -1), 10); // Remove check digit and convert to int.
      return orcidIsniRanges.some(
        ([start, end]) => start <= val && val <= end
      );
    }
    return false;
  });
});

addMethod(yupString, "isni", function () {
  return this.test("test-name", function (val) {
    // Test if argument is an International Standard Name Identifier.
    return isIsni(val);
  });
});

addMethod(yupString, "dateInSequence", function () {
  return this.test("test-name", function (value) {
    const { path, createError } = this;
    let outOfSequence = false;

    if (!!value) {
      const dateParts = value.split("/");
      if (dateParts?.length > 1) {
        const aDate = new Date(dateParts[0]);
        const bDate = new Date(dateParts[1]);
        if (aDate > bDate) {
          outOfSequence = true;
        }
      }
    }
    return (
      outOfSequence === false ||
      createError({ message: "End date must be after start date" })
    );
  });
});

const validationSchema = yupObject().shape({
  access: yupObject().shape({}),
  custom_fields: yupObject().shape({
    "kcr:ai_usage": yupObject().shape({
      ai_used: yupBoolean(),
      ai_description: yupString().when("ai_used", {
        is: true,
        then: yupString().required(
          "Please describe the role AI played in this work"
        ),
      }),
    }),
  }),
  metadata: yupObject()
    .shape({
      creators: yupArray()
        .of(
          yupObject().shape({
            affiliations: yupArray().of(
              yupObject().shape({
                name: yupString()
                  .matches(/(?!\s).+/, "Affiliation cannot be blank")
                  .required("An affiliation is required"),
              })
            ),
            person_or_org: yupObject().shape({
              type: yupString().required("A type is required"),
              family_name: yupString()
                .matches(/(?!\s).+/, "Family name cannot be blank")
                .required("A family name is required"),
              given_name: yupString().matches(/(?!\s).+/, {
                disallowEmptyString: true,
                message: "Given name cannot be spaces only",
              }),
              identifiers: yupArray().of(
                yupObject().shape({
                  scheme: yupString().required(
                    "A scheme is required for each identifier"
                  ),
                  identifier: yupString()
                    .when("scheme", {
                      is: "url",
                      then: yupString()
                        .url("Must be a valid URL (e.g. https://example.com)")
                        .required("You must provide a URL or remove this row"),
                    })
                    .when("scheme", {
                      is: "orcid",
                      then: yupString()
                        .orcid(
                          "Must be a valid ORCID id (e.g., 0000-0001-2345-6789)"
                        )
                        .required(
                          "You must provide an ORCID id or remove this row"
                        ),
                    })
                    .when("scheme", {
                      is: "isni",
                      then: yupString()
                        .isni(
                          "Must be a valid ISNI id (e.g., 0000-0001-2345-6789)"
                        )
                        .required(
                          "You must provide an ISNI id or remove this row"
                        ),
                    })
                    .when("scheme", {
                      is: "gnd",
                      then: yupString()
                        .gnd("Must be a valid GND id (e.g., gnd:118627813)")
                        .required(
                          "You must provide a GND id or remove this row"
                        ),
                    })
                    .when("scheme", {
                      is: "ror",
                      then: yupString()
                        .ror("Must be a valid ROR id (e.g., 03rjyp183)")
                        .required(
                          "You must provide a GND id or remove this row"
                        ),
                    })
                    .matches(/(?!\s).+/, {
                      disallowEmptyString: true,
                      message: "Identifier cannot be blank",
                    })
                    .required("A value is required for each identifier"),
                })
              ),
            }),
            role: yupString().required(
              "A role is required for each contributor"
            ),
          })
        )
        .min(1, "At least one contributor must be listed")
        .required("At least one contributor must be listed"),
      identifiers: yupArray().of(
        yupObject().shape({
          scheme: yupString().required(
            "An scheme is required for each identifier"
          ),
          identifier: yupString()
            .when("scheme", {
              is: "url",
              then: yupString()
                .url("Must be a valid URL (e.g. https://example.com)")
                .required("You must provide a URL or remove this item"),
            })
            .matches(/(?!\s).+/, {
              disallowEmptyString: true,
              message: "Identifier cannot be blank",
            })
            .required("You must provide an identifier or remove this row"),
        })
      ),
      publisher: yupString(),
      // .matches(/(?!\s).+/, "Publisher cannot be blank")
      // .required("A publisher is required. Enter 'none' if not applicable"),
      publication_date: yupString()
        .dateInSequence()
        .required("A publication date is required"),
      title: yupString()
        .matches(/(?!\s).+/, "Title cannot be blank")
        .min(3, "Title must be at least 3 characters")
        .required("A title is required"),
      resource_type: yupString().required("A resource type is required"),
      additional_descriptions: yupArray().of(
        yupObject().shape({
          description: yupString()
            .matches(/(?!\s).+/, "Description cannot be blank")
            .required("Provide a description or remove this item"),
          type: yupString().required(
            "A type is required for each additional description"
          ),
          lang: yupString(),
        })
      ),
    })
    .required("Some metadata is required"),
});

// const validator = (values) => {
//   const errors = {};
//   if (!values.metadata.resource_type) {
//     errors.metadata = { resource_type: "Required", ...errors.metadata };
//   }
//   if (!values.metadata.title || values.metadata.title === "") {
//     errors.metadata = { title: "Required", ...errors.metadata };
//   }
//   return errors;
// };

export { validationSchema };
