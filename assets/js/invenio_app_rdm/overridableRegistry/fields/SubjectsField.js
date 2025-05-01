// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import PropTypes from "prop-types";
import {
  FieldLabel,
  GroupField,
  Icon,
  Label,
} from "react-invenio-forms";
// import { RemoteSelectField } from "react-invenio-forms";
import { RemoteSelectField } from "@js/invenio_modular_deposit_form/replacement_components/RemoteSelectField";
import { Form } from "semantic-ui-react";
import { Field, getIn, useFormik } from "formik";
import { i18next } from "@translations/i18next";

const SubjectsField = ({
  clearable = true,
  description = undefined,
  fieldPath,
  helpText = undefined,
  hideSchemeLabels = true,
  label = i18next.t("Subjects"),
  icon = "tag",
  multiple = true,
  placeholder = i18next.t(
    "Search using full words"
    ),
  required = false,
  limitToOptions,
  noQueryMessage = " ",
  // noResultsMessage = " ",
  ...otherProps
}) => {
  const [limitTo, setLimitTo] = useState("all");

  const serializeSubjects = (subjects) => {
    const subs = subjects.map((subject) => {
      const scheme = subject.scheme ? `(${subject.scheme}) ` : "";
      return {
        text: !!hideSchemeLabels ? subject.subject : scheme + subject.subject,
        value: subject.subject,
        key: subject.subject,
        ...(subject.id ? { id: subject.id } : {}),
        subject: subject.subject,
      };
    });
    return subs;
  }

  const prepareSuggest = (searchQuery) => {
    const prefix = limitTo === "all" ? "" : `${limitTo}:`;
    return `${prefix}${searchQuery}`;
  };

  const facets = {
    "FAST-corporate": "groups",
    "FAST-geographic": "places",
    "FAST-event": "events",
    "FAST-personal": "people",
    "FAST-formgenre": "forms and genres",
    "FAST-chronological": "time periods",
    "FAST-title": "titles of works",
    "FAST-meeting": "meetings and conferences",
    "Homosaurus": "homosaurus",
  }

  const topFacets = {
    "FAST-topical": "topics",
    "All": "all",
  }

  let facetOptions = limitToOptions.reduce((options, option, it) => {
    if ( Object.keys(facets).includes(option.value) ) {
      options.push({
        key: option.value,
        value: option.text,
        text: facets[option.value],
      });
    }
    return options;
  }, []).sort((a, b) => a.text < b.text ? -1 : a.text > b.text ? 1 : 0);

  for (let [key, item] of Object.entries(topFacets)) {
    // FIXME: This is ugly and I'm tired
    // let item = facetOptions.splice(facetOptions.findIndex((item) => item.key === key), 1)[0];
    facetOptions.unshift(
      {
        key: key,
        value: key === "All" ? item : key,
        text: item,
      }
    )
  }

  return (
    <>
      <GroupField className="main-group-field">
        <Form.Field className="subjects-field-inner" width={16}>
          <FieldLabel htmlFor={fieldPath} icon={icon} label={label} />
          {!!description && (
          <div
            id={`${fieldPath}-helpt-text`}
            className="helptext label top"
          >
            {description}
          </div>
          )}
          <GroupField fluid>
            {/* <Form.Field
            width={4}
            style={{ marginBottom: "auto", marginTop: "auto" }}
            className=""
          >
            {i18next.t("Suggest from")}
          </Form.Field> */}
            <Field name={fieldPath} width={10}>
              {({ field, form: { values } }) => {
                return (
                  <RemoteSelectField
                    {...otherProps}
                    allowAdditions={false}
                    aria-describedby={`${fieldPath}-helpt-text`}
                    clearable={clearable}
                    description={undefined}  /** Description is rendered separately */
                    fieldPath={fieldPath}
                    helpText={undefined} /** Help text is rendered separately */
                    initialSuggestions={getIn(values, fieldPath, [])}
                    label={
                      <>
                        {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
                        <label className="mobile-hidden">&nbsp;</label>
                      </>
                    } /** For alignment purposes */
                    multiple={multiple}
                    noQueryMessage={noQueryMessage}
                    // noResultsMessage={noResultsMessage}
                    onValueChange={({ formikProps }, selectedSuggestions) => {
                      formikProps.form.setFieldValue(
                        fieldPath,
                        selectedSuggestions.map((suggestion) => ({
                          subject: suggestion.value,
                          id: suggestion.id,
                        }))
                      );
                    }}
                    placeholder={placeholder}
                    preSearchChange={prepareSuggest}
                    suggestionAPIQueryParams={{ type: "best_fields" }}
                    required={required}
                    serializeSuggestions={serializeSubjects}
                    serializeAddedValue={(value) => ({
                      text: value,
                      value: value,
                      key: value,
                      subject: value,
                    })}
                    suggestionAPIUrl="/api/subjects"
                    value={getIn(values, fieldPath, []).map(
                      (val) => val.subject
                    )}
                    width={11}
                    scrolling
                  />
                );
              }}
            </Field>
            <Form.Dropdown
              defaultValue={facetOptions[0].value}
              fluid
              onChange={(event, data) =>
                setLimitTo(data.value)
              }
              options={facetOptions}
              selection
              scrolling
              width={6}
              label={i18next.t("From subject category...")}
            />
          </GroupField>
          {!!helpText && (
          <div
            id={`${fieldPath}-helpt-text`}
            className="helptext label"
          >
            {helpText}
          </div>
          )}
        </Form.Field>
      </GroupField>
    </>
  );
}

SubjectsField.propTypes = {
  limitToOptions: PropTypes.array.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  icon: PropTypes.string,
  required: PropTypes.bool,
  multiple: PropTypes.bool,
  clearable: PropTypes.bool,
  placeholder: PropTypes.string,
  description: PropTypes.string,
};

export { SubjectsField };