/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2021 CERN.
 * Copyright (C) 2021 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { CommunitySettingsForm } from "..//components/CommunitySettingsForm";
import _get from "lodash/get";
import { useField } from "formik";
import React, { Component } from "react";
import { RadioField } from "react-invenio-forms";
import { Header } from "semantic-ui-react";
import PropTypes from "prop-types";

const VisibilityField = ({ label, formConfig, ...props }) => {
  const [field] = useField(props);
  return (
    <>
      {formConfig.access.visibility.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath="access.visibility"
            label={item.text}
            labelIcon={item.icon}
            checked={_get(field.value, "access.visibility") === item.value}
            value={item.value}
          />
          <label className="helptext">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

VisibilityField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

VisibilityField.defaultProps = {
  label: "",
};

class CommunityPrivilegesForm extends Component {
  getInitialValues = () => {
    return {
      access: {
        visibility: "public",
        // TODO: Re-enable once properly integrated to be displayed
        // member_policy: "open",
        // record_policy: "open",
      },
    };
  };

  render() {
    const { formConfig, community } = this.props;
    return (
      <CommunitySettingsForm
        initialValues={this.getInitialValues()}
        community={community}
      >
        <Header as="h2" size="tiny">
          {i18next.t("Community visibility")}
        </Header>
        <VisibilityField formConfig={formConfig} />
        {/* TODO: Re-enable once properly integrated to be displayed */}
        {/*
              <Grid.Column width={6}>
                <Header as="h3">Records permissions</Header>
                <p>This is a text explaining about the permission</p>
                <SelectField
                  fieldPath="access.record_policy"
                  options={this.props.formConfig.access.record_policy}
                />
                <Button compact primary icon labelPosition="left">
                  <Icon name="save"></Icon>Save
                </Button>
              </Grid.Column>
              <Grid.Column width={10} />
              <Grid.Column width={6}>
                <Header as="h3">Members permission policy</Header>
                <p>This is a text explaining about the permission</p>
                <SelectField
                  fieldPath="access.member_policy"
                  options={this.props.formConfig.access.member_policy}
                />
                <Button compact primary icon labelPosition="left">
                  <Icon name="save"></Icon>Save
                </Button>
              </Grid.Column>
              <Grid.Column width={10} /> */}
      </CommunitySettingsForm>
    );
  }
}

CommunityPrivilegesForm.propTypes = {
  community: PropTypes.object.isRequired,
  formConfig: PropTypes.object.isRequired,
};

export default CommunityPrivilegesForm;
