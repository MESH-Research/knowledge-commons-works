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
  RemoteSelectField,
} from "react-invenio-forms";
import { Form } from "semantic-ui-react";
import { Field, getIn, useFormik } from "formik";
import { i18next } from "@translations/invenio_rdm_records/i18next";

const SubjectsField = ({
  clearable = true,
  description = undefined,
  fieldPath,
  hideSchemeLabels = true,
  label = i18next.t("Keywords and subjects"),
  labelIcon = "tag",
  multiple = true,
  placeholder = i18next.t(
    "Search for a subject by name. (Press the 'enter' key to select)"
    ),
  required = false,
  limitToOptions,
}) => {
  const [limitTo, setLimitTo] = useState("all");

  const serializeSubjects = (subjects) =>
    subjects.map((subject) => {
      const scheme = subject.scheme ? `(${subject.scheme}) ` : "";
      return {
        text: !!hideSchemeLabels ? subject.subject : scheme + subject.subject,
        value: subject.subject,
        key: subject.subject,
        ...(subject.id ? { id: subject.id } : {}),
        subject: subject.subject,
      };
    });

  const prepareSuggest = (searchQuery) => {
    const prefix = limitTo === "all" ? "" : `${limitTo}:`;
    return `${prefix}${searchQuery}`;
  };

  const facets = {
    "FAST-topical": "topics",
    "FAST-corporate": "groups",
    "FAST-geographic": "places",
    "FAST-event": "events",
    "FAST-personal": "people",
    "FAST-formgenre": "forms and genres",
    "FAST-chronological": "time periods",
    "FAST-title": "titles of works",
    "FAST-meeting": "meetings and conferences",
  }

  const topFacets = {
    "FAST-topical": "topics",
    "All": "all",
  }

  let facetOptions = limitToOptions.map((option) => {
    if ( Object.keys(facets).includes(option.value) ) {
      return {
        key: option.value,
        value: option.text,
        text: facets[option.value],
      }
    } else {
      return option
    }
  }).sort((a, b) => a.text < b.text ? -1 : a.text > b. text ? 1 : 0);

  for (const key of Object.keys(topFacets)) {
    let item = facetOptions.splice(facetOptions.findIndex((item) => item.key === key), 1)[0];
    facetOptions.unshift(item)
  }
  console.log("limitToOptions", limitToOptions);
  console.log("facetOptions", facetOptions);

  return (
    <>
      <GroupField className="main-group-field">
        <Form.Field className="subjects-field-inner" width={16}>
          <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
          <GroupField fluid>
            {/* <Form.Field
            width={4}
            style={{ marginBottom: "auto", marginTop: "auto" }}
            className=""
          >
            {i18next.t("Suggest from")}
          </Form.Field> */}
            <Field name={fieldPath} width={10}>
              {({ form: { values } }) => {
                return (
                  <RemoteSelectField
                    clearable={clearable}
                    fieldPath={fieldPath}
                    initialSuggestions={getIn(values, fieldPath, [])}
                    multiple={multiple}
                    noQueryMessage={" "}
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
                    onValueChange={({ formikProps }, selectedSuggestions) => {
                      formikProps.form.setFieldValue(
                        fieldPath,
                        // save the suggestion objects so we can extract information
                        // about which value added by the user
                        selectedSuggestions
                      );
                    }}
                    value={getIn(values, fieldPath, []).map(
                      (val) => val.subject
                    )}
                    label={
                      <>
                        {/* eslint-disable-next-line jsx-a11y/label-has-associated-control */}
                        <label className="mobile-hidden">&nbsp;</label>
                      </>
                    } /** For alignment purposes */
                    allowAdditions={false}
                    width={11}
                    aria-describedby={`${fieldPath}-helpt-text`}
                    helptext={description}
                    scrolling
                  />
                );
              }}
              {/* <div
                id={`${fieldPath}-helpt-text`}
                className="helptext ui label"
              >
                {description}
              </div> */}
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
        </Form.Field>
      </GroupField>
    </>
  );
}

SubjectsField.propTypes = {
  limitToOptions: PropTypes.array.isRequired,
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  required: PropTypes.bool,
  multiple: PropTypes.bool,
  clearable: PropTypes.bool,
  placeholder: PropTypes.string,
  description: PropTypes.string,
};

export { SubjectsField };