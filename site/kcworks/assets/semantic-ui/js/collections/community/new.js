/*
 * This file is part of Invenio.
 * Copyright (C) 2016-2022 CERN.
 * Copyright (C) 2021-2022 Northwestern University.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { Formik, useFormikContext } from "formik";
import _isEmpty from "lodash/isEmpty";
import _get from "lodash/get";
import React, { Component } from "react";
import ReactDOM from "react-dom";
import {
  CustomFields,
  FieldLabel,
  RadioField,
  TextField,
  withCancel,
} from "react-invenio-forms";
import { Button, Divider, Form, Grid, Header, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "@js/invenio_communities/api";
import { communityErrorSerializer } from "@js/invenio_communities/api/serializers";
import PropTypes from "prop-types";

const IdentifierField = ({ formConfig }) => {
  const { values } = useFormikContext();

  const helpText = (
    <>
      {i18next.t(
        "This is your collection's unique identifier, used as the last part of the collection URL. You will be able to access your collection at: "
      )}
      {`${formConfig.SITE_UI_URL}/collections/${values["slug"]}`}
    </>
  );

  return (
    <TextField
      required
      id="slug"
      label={
        <FieldLabel htmlFor="slug" icon="barcode" label={i18next.t("URL Identifier")} />
      }
      fieldPath="slug"
      helpText={helpText}
      fluid
      className="text-muted"
      // Prevent submitting before the value is updated:
      onKeyDown={(e) => {
        e.key === "Enter" && e.preventDefault();
      }}
    />
  );
};

IdentifierField.propTypes = {
  formConfig: PropTypes.object.isRequired,
};

class CommunityCreateForm extends Component {
  state = {
    error: "",
  };

  componentWillUnmount() {
    this.cancellableCreate && this.cancellableCreate.cancel();
  }

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    setSubmitting(true);
    const client = new CommunityApi();
    const payload = {
      metadata: {},
      ...values,
    };
    this.cancellableCreate = withCancel(client.create(payload));

    try {
      const response = await this.cancellableCreate.promise;
      setSubmitting(false);
      // TODO: Can we update this url with "collections" on the back end?
      const settingsUrl = response.data.links.settings_html.replace("communities", "collections");
      window.location.href = settingsUrl;
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { errors, message } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(message);
      }

      if (errors) {
        errors.map(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }
  };

  render() {
    const { formConfig, canCreateRestricted } = this.props;
    const { error } = this.state;
    console.log("formConfig", formConfig);
    formConfig.access.visibility[0].helpText = i18next.t(
      "Your collection is publicly accessible and shows up in search results.");
    formConfig.access.visibility[1].helpText = i18next.t(
      "Your collection is only accessible to users with access.");

    return (
      <Formik
        initialValues={{
          access: {
            visibility: "public",
          },
          slug: "",
        }}
        onSubmit={this.onSubmit}
      >
        {({ values, isSubmitting, handleSubmit }) => (
          <Form onSubmit={handleSubmit} className="communities-creation">
            <Message hidden={error === ""} negative className="flashed">
              <Grid container centered>
                <Grid.Column mobile={16} tablet={12} computer={8} textAlign="left">
                  <strong>{error}</strong>
                </Grid.Column>
              </Grid>
            </Message>
            <Grid container centered>
              <Grid.Row>
                <Grid.Column mobile={16} tablet={12} computer={8} textAlign="center">
                  <Header as="h1" className="rel-mt-2">
                    {i18next.t("Start your new collection")}
                  </Header>
                  <Divider />
                </Grid.Column>
              </Grid.Row>
              <Grid.Row textAlign="left">
                <Grid.Column mobile={16} tablet={12} computer={8}>
                  <TextField
                    required
                    id="metadata.title"
                    fluid
                    fieldPath="metadata.title"
                    // Prevent submitting before the value is updated:
                    onKeyDown={(e) => {
                      e.key === "Enter" && e.preventDefault();
                    }}
                    label={
                      <FieldLabel
                        htmlFor="metadata.title"
                        icon="book"
                        label={i18next.t("Collection name")}
                      />
                    }
                  />
                  <IdentifierField formConfig={formConfig} />
                  {!_isEmpty(customFields.ui) && (
                    <CustomFields
                      config={customFields.ui}
                      templateLoaders={[
                        (widget) => import(`@templates/custom_fields/${widget}.js`),
                        (widget) => import(`react-invenio-forms`),
                      ]}
                      fieldPathPrefix="custom_fields"
                    />
                  )}
                  {canCreateRestricted && (
                    <>
                      <Header as="h3">{i18next.t("Collection visibility")}</Header>
                      {formConfig.access.visibility.map((item) => (
                        <React.Fragment key={item.value}>
                          <RadioField
                            key={item.value}
                            fieldPath="access.visibility"
                            label={item.text}
                            labelIcon={item.icon}
                            checked={_get(values, "access.visibility") === item.value}
                            value={item.value}
                            onChange={({ event, data, formikProps }) => {
                              formikProps.form.setFieldValue(
                                "access.visibility",
                                item.value
                              );
                            }}
                          />
                          <label className="helptext">{item.helpText}</label>
                        </React.Fragment>
                      ))}
                    </>
                  )}
                </Grid.Column>
              </Grid.Row>
              <Grid.Row>
                <Grid.Column textAlign="center">
                  <Button
                    positive
                    icon
                    labelPosition="left"
                    loading={isSubmitting}
                    disabled={isSubmitting}
                    type="button"
                    onClick={(event) => handleSubmit(event)}
                  >
                    <Icon name="plus" />
                    {i18next.t("Create collection")}
                  </Button>
                </Grid.Column>
              </Grid.Row>
            </Grid>
          </Form>
        )}
      </Formik>
    );
  }
}

CommunityCreateForm.propTypes = {
  formConfig: PropTypes.object.isRequired,
  canCreateRestricted: PropTypes.bool.isRequired,
};

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const customFields = JSON.parse(domContainer.dataset.customFields);
const canCreateRestricted = JSON.parse(domContainer.dataset.canCreateRestricted);

ReactDOM.render(
  <CommunityCreateForm
    formConfig={formConfig}
    customFields={customFields}
    canCreateRestricted={canCreateRestricted}
  />,
  domContainer
);
export default CommunityCreateForm;
