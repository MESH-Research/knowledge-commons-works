/*
 * This file is part of Knowledge Commons Works.
 * Copyright (C) 2026 Mesh Research.
 */

import { i18next } from "@translations/kcworks/i18next";
import * as Yup from "yup";
import {
  isOptionalBoolean,
  isOptionalFontFamily,
  isOptionalFontSize,
  isOptionalFontWeight,
  isOptionalHexColor,
} from "@js/kcworks/utils/themeInputValidation";

const HEX_COLOR_MESSAGE = i18next.t("Must be a hex color (#RGB or #RRGGBB).");
const INVALID_VALUE_MESSAGE = i18next.t("Invalid value.");

/**
 * @param {string} label
 * @returns {import("yup").StringSchema}
 */
function optionalHexColorField(label) {
  return Yup.string().test(`${label}-hex-color`, HEX_COLOR_MESSAGE, isOptionalHexColor);
}

const themeStyleSchema = Yup.object({
  primaryColor: optionalHexColorField("primaryColor"),
  primaryTextColor: optionalHexColorField("primaryTextColor"),
  secondaryColor: optionalHexColorField("secondaryColor"),
  secondaryTextColor: optionalHexColorField("secondaryTextColor"),
  tertiaryColor: optionalHexColorField("tertiaryColor"),
  tertiaryTextColor: optionalHexColorField("tertiaryTextColor"),
  mainHeaderBackgroundColor: optionalHexColorField("mainHeaderBackgroundColor"),

  mainHeaderUseLogo: Yup.mixed().test("boolean", INVALID_VALUE_MESSAGE, isOptionalBoolean),
  mainHeaderUseGradient: Yup.mixed().test(
    "boolean",
    INVALID_VALUE_MESSAGE,
    isOptionalBoolean
  ),

  font: Yup.object({
    family: Yup.string().test(
      "font-family",
      i18next.t("Invalid font family."),
      isOptionalFontFamily
    ),
    weight: Yup.mixed().test(
      "font-weight",
      i18next.t("Font weight must be normal, bold, bolder, lighter, or 100–900."),
      isOptionalFontWeight
    ),
    size: Yup.string().test(
      "font-size",
      i18next.t("Font size must be a length (em, rem, px, or %)."),
      isOptionalFontSize
    ),
  }),
});

/** Yup schema for theme fields on the community Formik values object. */
export const communityThemeValidationSchema = Yup.object({
  theme: Yup.object({
    enabled: Yup.mixed().test("boolean", INVALID_VALUE_MESSAGE, isOptionalBoolean),
    style: themeStyleSchema,
  }),
});
