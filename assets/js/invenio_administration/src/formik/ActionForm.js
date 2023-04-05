import React, { Component } from "react";
import PropTypes from "prop-types";
import { Form, Formik } from "formik";
import { InvenioAdministrationActionsApi } from "../api/actions";
import { Button, Modal } from "semantic-ui-react";
import { Form as SemanticForm } from "semantic-ui-react";
import _get from "lodash/get";
import { ErrorMessage } from "../ui_messages";
import isEmpty from "lodash/isEmpty";
import { GenerateForm } from "./GenerateForm";
import { deserializeFieldErrors } from "../components/utils";
import { i18next } from "@translations/invenio_administration/i18next";

export class ActionForm extends Component {
  constructor(props) {
    super(props);

    this.state = {
      loading: false,
      error: undefined,
      formData: {},
    };
  }

  onSubmit = async (formData, actions) => {
    this.setState({ loading: true });
    const { actionKey, actionSuccessCallback } = this.props;
    const actionEndpoint = this.getEndpoint(actionKey);

    try {
      const response = await InvenioAdministrationActionsApi.resourceAction(
        actionEndpoint,
        formData
      );
      this.setState({ loading: false });
      actionSuccessCallback(response.data);
    } catch (e) {
      console.error(e);
      this.setState({ loading: false });
      let errorMessage = e.message;

      // API errors need to be de-serialised to highlight fields.
      const apiResponse = e?.response?.data;
      if (apiResponse) {
        const apiErrors = apiResponse.errors || [];
        const deserializedErrors = deserializeFieldErrors(apiErrors);
        actions.setErrors(deserializedErrors);
        errorMessage = apiResponse.message || errorMessage;
      }

      this.setState({
        error: { header: "Action error", content: errorMessage, id: e.code },
      });
    }
  };

  getEndpoint = (actionKey) => {
    const { resource } = this.props;
    let endpoint;
    // get the action endpoint from the current resource links
    endpoint = _get(resource, `links.actions[${actionKey}]`);

    // endpoint can be also within links, not links.action
    // TODO: handle it in a nicer way
    if (isEmpty(endpoint)) {
      endpoint = _get(resource, `links[${actionKey}]`);
    }
    if (!endpoint) {
      console.error("Action endpoint not found in the resource!");
    }
    return endpoint;
  };

  resetErrorState = () => {
    this.setState({ error: undefined });
  };

  render() {
    const { actionSchema, formFields, actionCancelCallback } = this.props;
    const { loading, formData, error } = this.state;
    return (
      <Formik initialValues={formData} onSubmit={this.onSubmit}>
        {(props) => (
          <>
            <Modal.Content>
              <SemanticForm as={Form} id="action-form" onSubmit={props.handleSubmit}>
                <GenerateForm
                  jsonSchema={actionSchema}
                  formFields={formFields}
                  create
                  dropDumpOnly
                />
                {!isEmpty(error) && (
                  <ErrorMessage {...error} removeNotification={this.resetErrorState} />
                )}
              </SemanticForm>
            </Modal.Content>

            <Modal.Actions>
              <Button type="submit" primary form="action-form" loading={loading}>
                {i18next.t("Save")}
              </Button>
              <Button
                onClick={actionCancelCallback}
                floated="left"
                icon="cancel"
                labelPosition="left"
                content={i18next.t("Cancel")}
              />
            </Modal.Actions>
          </>
        )}
      </Formik>
    );
  }
}

ActionForm.propTypes = {
  resource: PropTypes.object.isRequired,
  actionSchema: PropTypes.object.isRequired,
  actionKey: PropTypes.string.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
  actionCancelCallback: PropTypes.func.isRequired,
  formFields: PropTypes.object,
};

ActionForm.defaultProps = {
  formFields: {},
};
