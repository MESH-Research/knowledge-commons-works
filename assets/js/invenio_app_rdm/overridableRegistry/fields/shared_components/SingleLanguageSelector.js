import React, { useEffect } from "react";
import PropTypes from "prop-types";
import { LanguagesField } from "@js/invenio_modular_deposit_form/replacement_components/LanguagesField";
import { i18next } from "@translations/i18next";
import { useFormikContext } from "formik";

/**
 * A single language selector component for use in AdditionalTitlesField and AdditionalDescriptionsField.
 * Handles conversion between string and object language values, and manages language selection.
 * This component is specifically designed for single language selection (not multiple).
 *
 * @param {Object} props - The component props.
 * @param {string} props.fieldPath - The path to the field in the form values.
 * @param {Object} props.value - The current field value.
 * @param {number} props.index - The index of the field in the array.
 * @param {Object} props.recordUI - The record.ui property from the redux store.
 * @param {string} props.fieldName - The name of the field in recordUI (e.g. 'additional_titles' or 'additional_descriptions').
 * @returns {React.ReactNode} The component.
 */
const SingleLanguageSelector = ({ fieldPath, value, index, recordUI, fieldName, ...extraProps }) => {
  const { setFieldValue } = useFormikContext();

  // Get language object from value and recordUI
  // Necessary because the initial form value may be a string
  // and needs to be converted to an object with id and title_l10n
  // but the recordUI may not have client-side form value updates
  const getLangObject = (value, index) => {
    let langObject = null;
    if (typeof value.lang === "string") {
      const matchingUiLang = recordUI?.[fieldName]?.[index]?.lang;
      if (matchingUiLang) {
        langObject = {
          id: matchingUiLang.id,
          title_l10n: matchingUiLang.title_l10n,
        }
      }
    } else if (value.lang) {
      langObject = {id: value.lang.id, title_l10n: value.lang.title_l10n};
    }
    return langObject;
  };

  // Convert the initial form value to an object with id and title_l10n
  // if it's just a string
  useEffect(() => {
    const langObject = getLangObject(value, index);
    if (langObject && (
        typeof value.lang === 'string' ||
        !value.lang ||
        value.lang.id !== langObject.id ||
        value.lang.title_l10n !== langObject.title_l10n
    )) {
      setFieldValue(`${fieldPath}.lang`, langObject);
    }
  }, []);

  // Get initial options for LanguagesField
  const getInitialOptions = (value, index) => {
    const langObject = getLangObject(value, index);
    return langObject ? [langObject] : [];
  };

  return (
    <LanguagesField
      serializeSuggestions={(suggestions) => {
        return (suggestions?.map((suggestion) => ({
          text: suggestion?.title_l10n,
          value: suggestion.id,
          fieldPathPrefix: suggestion?.id,
          key: suggestion?.id,
        })))
      }}
      initialOptions={getInitialOptions(value, index)}
      onValueChange={({event, data, formikProps}, selectedSuggestions) => {
        setFieldValue(`${fieldPath}.lang`, !selectedSuggestions.length ? null : {
          title_l10n: selectedSuggestions[0].text,
          id: selectedSuggestions[0].value,
        });
      }}
      fieldPath={`${fieldPath}.lang`}
      id={`${fieldPath}.lang`}
      label="Language"
      multiple={false}
      noQueryMessage={i18next.t("Search languages")}
      noResultsMessage={i18next.t("No languages found")}
      placeholder=""
      icon={null}
      clearable={false}
      selectOnBlur={true}
      width={4}
      {...extraProps}
    />
  );
};

SingleLanguageSelector.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  value: PropTypes.object.isRequired,
  index: PropTypes.number.isRequired,
  recordUI: PropTypes.object,
  fieldName: PropTypes.string.isRequired,
};

export { SingleLanguageSelector };