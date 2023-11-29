import {
  addMethod,
  object as yupObject,
  string as yupString,
  date as yupDate,
} from "yup";

addMethod(yupString, "dateInSequence", function () {
  return this.test("test-name", function (value) {
    console.log("dateInSequence", value);
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
  metadata: yupObject()
    .shape({
      title: yupString().required("A title is required"),
      resource_type: yupString().required("A resource type is required"),
      publication_date: yupString()
        .dateInSequence()
        .required("A publication date is required"),
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
