/*
* This file is part of Knowledge Commons Works.
*   Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
*   Copyright (C) 2020-2024 CERN.
*   Copyright (C) 2020-2024 Northwestern University.
*   Copyright (C) 2020-2024 T U Wien.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import React from "react";
import { Header } from "semantic-ui-react";
import { useField } from "formik";
import { RadioField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import * as Yup from "yup";
import _get from "lodash/get";
import PropTypes from "prop-types";

// Default set invenio_communities/views/communities.py
const REVIEW_POLICY_FIELDS = [
    {
        "text": "Review all submissions",
        "value": "closed",
        "icon": "lock",
        "helpText": i18next.t(
            "All submissions to the collection must be reviewed."
        ),
    },
    {
        "text": "Allow curators, managers and owners to publish without review",
        "value": "open",
        "icon": "group",
        "helpText": i18next.t(
            "Submissions to the collection by default requires review, but curators, managers and owners can publish directly without review."
        ),
    },
]

const ReviewPolicyField = ({ label="", formConfig, ...props }) => {
  const [field] = useField(props);
  return (
    <>
      {formConfig.access.review_policy.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath="access.review_policy"
            label={item.text}
            aria-label={item.text}
            labelIcon={item.icon}
            checked={_get(field.value, "access.review_policy") === item.value}
            value={item.value}
          />
          <label className="helptext ml-20">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

ReviewPolicyField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

const CurationPolicyFormLayout = ({ formConfig, community }) => {

  formConfig.access.review_policy = REVIEW_POLICY_FIELDS;

  return (
    <>
      <Header as="h3" className="mt-5">
        {i18next.t("Submission review policy")}
      </Header>
      <ReviewPolicyField formConfig={formConfig} />
    </>
  );
};

CurationPolicyFormLayout.propTypes = {
  formConfig: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};

export { CurationPolicyFormLayout, ReviewPolicyField };
