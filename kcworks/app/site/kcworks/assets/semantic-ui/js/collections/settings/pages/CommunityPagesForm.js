/*
 * This file is part of Invenio.
 * Copyright (C) 2023 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { i18next } from "@translations/invenio_communities/i18next";
import { Formik } from "formik";
import _defaultsDeep from "lodash/defaultsDeep";
import React, { Component } from "react";
import { RichInputField, AccordionField } from "react-invenio-forms";
import { Button, Form, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { communityErrorSerializer } from "../../api/serializers";
import PropTypes from "prop-types";
import * as Yup from "yup";

const COMMUNITY_PAGES_VALIDATION_SCHEMA = Yup.object({
  metadata: Yup.object({
    curation_policy: Yup.string().max(50000, "Maximum number of characters is 50000"),
    page: Yup.string().max(50000, "Maximum number of characters is 50000"),
  }),
});

export class CommunityPagesForm extends Component {
  state = {
    error: undefined,
  };
  getInitialValues = () => {
    const { community } = this.props;
    let initialValues = _defaultsDeep(community, {
      metadata: {
        curation_policy: "",
        page: "",
      },
    });

    return initialValues;
  };

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    const { community } = this.props;
    setSubmitting(true);

    try {
      const client = new CommunityApi();
      await client.update(community.id, values);
      window.location.reload();
    } catch (error) {
      if (error === "UNMOUNTED") return;

      const { message, errors } = communityErrorSerializer(error);

      if (message) {
        this.setGlobalError(message);
      }

      if (errors) {
        errors.forEach(({ field, messages }) => setFieldError(field, messages[0]));
      }
    }

    setSubmitting(false);
  };
  render() {
    const { error } = this.state;
    const { community } = this.props;

    const hasError = error !== undefined;

    return (
      <Formik
        initialValues={this.getInitialValues(community)}
        validationSchema={COMMUNITY_PAGES_VALIDATION_SCHEMA}
        onSubmit={this.onSubmit}
      >
        {({ isSubmitting, isValid, handleSubmit, values }) => (
          <Form onSubmit={handleSubmit}>
            <Message hidden={!hasError} negative>
              <Message.Content>{error}</Message.Content>
            </Message>
            <AccordionField
              includesPaths={["metadata.curation_policy"]}
              label={i18next.t("Curation policy")}
              active
            >
              <RichInputField
                fieldPath="metadata.curation_policy"
                className="ck-height-10"
                fluid
              />
            </AccordionField>
            <AccordionField
              includesPaths={["metadata.page"]}
              label={i18next.t("About page")}
              active
            >
              <RichInputField
                fieldPath="metadata.page"
                className="ck-height-25"
                fluid
              />
            </AccordionField>
            <Button
              primary
              icon
              labelPosition="left"
              loading={isSubmitting}
              disabled={!isValid || isSubmitting}
              toggle
              type="submit"
            >
              <Icon name="save" />
              {i18next.t("Save")}
            </Button>
          </Form>
        )}
      </Formik>
    );
  }
}

CommunityPagesForm.propTypes = {
  community: PropTypes.object.isRequired,
};
