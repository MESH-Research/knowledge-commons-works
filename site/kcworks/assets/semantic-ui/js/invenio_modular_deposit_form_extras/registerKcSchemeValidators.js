// Part of KCWorks — extends modular deposit form identifier validation.
//
// Must load before `@js/invenio_modular_deposit_form/validation/validator` so
// `validator.js`'s `addMethod` loop registers `kc_username` with the rest.

import { SCHEME_ID_TO_VALIDATOR } from "@js/invenio_modular_deposit_form/validation/validatorsForIds";
import { kcUsernameValidator } from "./validatorsForIds";

SCHEME_ID_TO_VALIDATOR.kc_username = kcUsernameValidator;
