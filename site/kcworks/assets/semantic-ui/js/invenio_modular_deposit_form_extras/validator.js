// Part of KCWorks
//
// Instance validator: upstream config-driven schema + KC-only shapes via Yup concat.

import {
  boolean as yupBoolean,
  object as yupObject,
  string as yupString,
} from "yup";

import "./registerKcSchemeValidators";
import buildValidationSchema from "@js/invenio_modular_deposit_form/validation/validator";

/** KC-only rules merged onto the stock modular-deposit schema. */
const kcValidationExtensions = yupObject().shape({
  custom_fields: yupObject().shape({
    "kcr:ai_usage": yupObject().shape({
      ai_used: yupBoolean(),
      ai_description: yupString().when("ai_used", {
        is: true,
        then: (schema) =>
          schema.required(
            "Please describe the role AI played in this work"
          ),
      }),
    }),
  }),
});

/**
 * @param {Object} config - Deposit config as stored for the deposit app (same object
 *   `RDMDepositForm` puts in Redux: vocabularies under `config.vocabularies`,
 *   `max_title_length`, pids, etc.). Upstream `buildValidationSchema` uses those
 *   values for identifier scheme lists, title/date type `oneOf`, title max length,
 *   and related rules; omitting or stubbing them yields the wrong schema for production.
 * @returns {import("yup").ObjectSchema}
 */
function buildKcValidationSchema(config) {
  return buildValidationSchema(config).concat(kcValidationExtensions);
}

export default buildKcValidationSchema;
