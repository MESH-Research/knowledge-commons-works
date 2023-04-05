import _set from "lodash/set";

export const sortFields = (schema) => {
  /**
   * Sort fields based on the order param supplied by view configuration
   * Doesn't take care of nested field - sorts only one level
   */
  return (
    Object.entries(schema)
      // sort by order
      .sort((a, b) => {
        if (a[1]?.ui && b[1].ui) {
          return a[1].ui.order > b[1].ui.order;
        }
        return true;
      })
      // build object with sorted attributes
      .reduce((sorted, entry) => {
        const key = entry[0];
        sorted[key] = schema[key];
        return sorted;
      }, {})
  );
};

export const deserializeFieldErrors = (errors) => {
  /**
   * Deserialises field errors from the API to be consumed by the front-end.
   * The output's format works with Formik.
   */
  let deserializedErrors = {};
  if (Array.isArray(errors)) {
    for (const e of errors) {
      if (
        Object.prototype.hasOwnProperty.call(e, "field") &&
        Object.prototype.hasOwnProperty.call(e, "messages")
      ) {
        _set(deserializedErrors, e.field, e.messages.join(" "));
      }
    }
  }
  return deserializedErrors;
};
