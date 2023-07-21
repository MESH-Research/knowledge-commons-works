// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C)      2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { Component } from "react";
import { connect } from "react-redux";
import PropTypes from "prop-types";
import { Field } from "formik";
import { FieldLabel } from "react-invenio-forms";
import { Card, Divider, Form, Header, Segment } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  MetadataAccess,
  FilesAccess,
  EmbargoAccess,
  AccessMessage,
} from "./access_rights_components";

export class AccessRightFieldCmp extends Component {
  /** Top-level Access Right Component */

  render() {
    const {
      fieldPath,
      formik, // this is our access to the shared current draft
      label,
      labelIcon,
      showMetadataAccess,
      community,
    } = this.props;

    const isGhostCommunity = community?.is_ghost === true;
    const communityAccess =
      (community && !isGhostCommunity && community.access.visibility) || "public";
    const isMetadataOnly = !formik.form.values.files.enabled;

    return (
        <Form.Field required>
          <Segment className="access-right">
            <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />

            {showMetadataAccess && (
              <>
                <MetadataAccess
                  recordAccess={formik.field.value.record}
                  communityAccess={communityAccess}
                />
                <Divider hidden />
              </>
            )}

            <FilesAccess
              access={formik.field.value}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />

            {/* <Divider hidden /> */}

            <AccessMessage
              access={formik.field.value}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />
          </Segment>
          <Segment fluid>

            {/* <Divider hidden /> */}
            <Card.Header as={Header} size="tiny">
              {i18next.t("Options")}
            </Card.Header>
            <EmbargoAccess
              access={formik.field.value}
              accessCommunity={communityAccess}
              metadataOnly={isMetadataOnly}
            />
          </Segment>
        </Form.Field>
    );
  }
}

AccessRightFieldCmp.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  formik: PropTypes.object.isRequired,
  label: PropTypes.string.isRequired,
  labelIcon: PropTypes.string.isRequired,
  showMetadataAccess: PropTypes.bool,
  community: PropTypes.object,
};

AccessRightFieldCmp.defaultProps = {
  showMetadataAccess: true,
  community: undefined,
};

const mapStateToPropsAccessRightFieldCmp = (state) => ({
  community: state.deposit.editorState.selectedCommunity,
});

export const AccessRightFieldComponent = connect(
  mapStateToPropsAccessRightFieldCmp,
  null
)(AccessRightFieldCmp);

export class AccessRightField extends Component {
  render() {
    const { fieldPath } = this.props;

    return (
      <Field name={fieldPath}>
        {(formik) => <AccessRightFieldComponent formik={formik} {...this.props} />}
      </Field>
    );
  }
}

AccessRightField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string.isRequired,
  labelIcon: PropTypes.string,
  isMetadataOnly: PropTypes.bool,
};

AccessRightField.defaultProps = {
  labelIcon: undefined,
  isMetadataOnly: undefined,
};
