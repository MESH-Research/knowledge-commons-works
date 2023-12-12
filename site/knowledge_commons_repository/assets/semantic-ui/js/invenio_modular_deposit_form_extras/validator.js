import {
  addMethod,
  array as yupArray,
  boolean as yupBoolean,
  object as yupObject,
  string as yupString,
  date as yupDate,
} from "yup";

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
                    "An identifier scheme is required"
                  ),
                  identifier: yupString()
                    .when("scheme", {
                      is: "url",
                      then: yupString().url("Must be a valid URL"),
                    })
                    .matches(/(?!\s).+/, {
                      disallowEmptyString: true,
                      message: "Identifier cannot be blank",
                    })
                    .required("An identifier is required"),
                })
              ),
            }),
            role: yupString().required("A role is required"),
          })
        )
        .min(1, "At least one contributor must be listed")
        .required("At least one contributor must be listed"),
      identifiers: yupArray().of(
        yupObject().shape({
          scheme: yupString().required("An identifier scheme is required"),
          identifier: yupString()
            .when("scheme", {
              is: "url",
              then: yupString().url("Must be a valid URL"),
            })
            .matches(/(?!\s).+/, {
              disallowEmptyString: true,
              message: "Identifier cannot be blank",
            })
            .required("An identifier is required"),
        })
      ),
      publisher: yupString()
        .matches(/(?!\s).+/, "Publisher cannot be blank")
        .required("A publisher is required"),
      publication_date: yupString()
        .dateInSequence()
        .required("A publication date is required"),
      title: yupString()
        .matches(/(?!\s).+/, "Title cannot be blank")
        .required("A title is required"),
      resource_type: yupString().required("A resource type is required"),
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
