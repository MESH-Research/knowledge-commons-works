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
// import { MembersVisibilityField, VisibilityField } from "@js/invenio_communities/settings/privileges/CommunityPriviledgesForm";
import { useField } from "formik";
import { Header } from "semantic-ui-react";
import { RadioField } from "react-invenio-forms";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";
import _get from "lodash/get";

// Default set invenio_communities/views/communities.py
const VISIBILITY_FIELDS = [
  {
    text: "Public",
    value: "public",
    icon: "group",
    helpText: i18next.t(
      "Your collection is publicly accessible" +
        " and shows up in search results."
    ),
  },
  {
    text: "Restricted",
    value: "restricted",
    icon: "lock",
    helpText: i18next.t(
      "Your collection is restricted to users" + " with access."
    ),
  },
];

// Default set invenio_communities/views/communities.py
const MEMBERS_VISIBILITY_FIELDS = [
  {
    text: "Public",
    value: "public",
    icon: "group",
    helpText: i18next.t(
      "Members who have set their visibility to public are visible " +
        "to anyone. Members with hidden visibility are only visible " +
        "to other members."
    ),
  },
  {
    text: "Members-only",
    value: "restricted",
    icon: "lock",
    helpText: i18next.t(
      "Members in your community are only visible to other members of " +
        "the community."
    ),
  },
];

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
          <label className="helptext ml-15">{item.helpText}</label>
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

const MembersVisibilityField = ({ label = "", formConfig, ...props }) => {
  const [field] = useField(props);
  return (
    <>
      {formConfig.access.members_visibility.map((item) => (
        <React.Fragment key={item.value}>
          <RadioField
            key={item.value}
            fieldPath="access.members_visibility"
            label={item.text}
            labelIcon={item.icon}
            checked={
              _get(field.value, "access.members_visibility") === item.value
            }
            value={item.value}
          />
          <label className="helptext ml-15">{item.helpText}</label>
        </React.Fragment>
      ))}
    </>
  );
};

MembersVisibilityField.propTypes = {
  label: PropTypes.string,
  formConfig: PropTypes.object.isRequired,
};

const CommunityPrivilegesFormLayout = ({ formConfig, community }) => {
  formConfig.access.visibility = VISIBILITY_FIELDS;
  formConfig.access.members_visibility = MEMBERS_VISIBILITY_FIELDS;

  return (
    <>
      <Header as="h3" className="mt-5">
        {i18next.t("Collection visibility")}
        <Header.Subheader className="mt-5">
          {i18next.t(
            "Controls whether the collection is visible to anyone or to members only."
          )}
        </Header.Subheader>
      </Header>
      <VisibilityField formConfig={formConfig} />

      <Header as="h3" className="mt-5">
        {i18next.t("Members visibility")}
        <Header.Subheader className="mt-5">
          {i18next.t(
            "Controls whether the members tab is visible to anyone or to members only."
          )}
        </Header.Subheader>
      </Header>
      <MembersVisibilityField formConfig={formConfig} />
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
    </>
  );
};

export {
  CommunityPrivilegesFormLayout,
  VisibilityField,
  MembersVisibilityField,
};
