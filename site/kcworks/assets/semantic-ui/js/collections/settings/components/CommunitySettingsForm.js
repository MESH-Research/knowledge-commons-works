import { i18next } from "@translations/invenio_communities/i18next";
import { Formik } from "formik";
import _defaultsDeep from "lodash/defaultsDeep";
import React, { Component } from "react";
import { Button, Form, Icon, Message } from "semantic-ui-react";
import { CommunityApi } from "../../api";
import { communityErrorSerializer } from "../../api/serializers";
import PropTypes from "prop-types";

export class CommunitySettingsForm extends Component {
  state = {
    error: undefined,
    isSaved: false,
  };
  getInitialValues = () => {
    const { community, initialValues } = this.props;
    return _defaultsDeep(community, initialValues);
  };

  setGlobalError = (errorMsg) => {
    this.setState({ error: errorMsg });
  };

  setIsSavedState = (newValue) => {
    this.setState({ isSaved: newValue });
  };

  onSubmit = async (values, { setSubmitting, setFieldError }) => {
    const { community } = this.props;

    setSubmitting(true);

    try {
      const client = new CommunityApi();
      await client.update(community.id, values);

      this.setIsSavedState(true);
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
    const { children, community } = this.props;
    const { isSaved, error } = this.state;
    const hasError = error !== undefined;
    return (
      <Formik initialValues={this.getInitialValues(community)} onSubmit={this.onSubmit}>
        {({ isSubmitting, handleSubmit, values }) => (
          <Form onSubmit={handleSubmit}>
            <Message hidden={!hasError} negative>
              <Message.Content>{error}</Message.Content>
            </Message>
            {children}
            <Button
              primary
              icon
              labelPosition="left"
              loading={isSubmitting}
              toggle
              active={isSaved}
              type="submit"
            >
              <Icon name="save" />
              {isSaved ? i18next.t("Saved") : i18next.t("Save")}
            </Button>
          </Form>
        )}
      </Formik>
    );
  }
}

CommunitySettingsForm.propTypes = {
  community: PropTypes.object.isRequired,
  children: PropTypes.node.isRequired,
  initialValues: PropTypes.object.isRequired,
};
