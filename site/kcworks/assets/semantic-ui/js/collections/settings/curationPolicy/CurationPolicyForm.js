/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { useField } from "formik";
import { CommunitySettingsForm } from "../components";
import _get from "lodash/get";
import React, { Component } from "react";
import { RadioField } from "react-invenio-forms";
import { Header } from "semantic-ui-react";
import PropTypes from "prop-types";
import * as Yup from "yup";

const COMMUNITY_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    curation_policy: Yup.string().max(5000, "Maximum number of characters is 5000"),
  }),
});

const ReviewPolicyField = ({ label, formConfig, ...props }) => {
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
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

ReviewPolicyField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

ReviewPolicyField.defaultProps = {
  label: "",
};

export class CurationPolicyForm extends Component {
  getInitialValues = () => {
    return {
      metadata: {
        curation_policy: "",
      },
      access: {
        review_policy: "closed",
      },
    };
  };

  render() {
    const { community, formConfig } = this.props;
    return (
      <CommunitySettingsForm
        initialValues={this.getInitialValues()}
        community={community}
        validationSchema={COMMUNITY_VALIDATION_SCHEMA}
      >
        <Header size="tiny" className="mt-0">
          {i18next.t("Submission review policy")}
        </Header>
        <ReviewPolicyField formConfig={formConfig} />
      </CommunitySettingsForm>
    );
  }
}

CurationPolicyForm.propTypes = {
  community: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};
