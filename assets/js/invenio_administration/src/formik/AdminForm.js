import React, { Component } from "react";
import PropTypes from "prop-types";
import { Form, Formik } from "formik";
import { Form as SemanticForm, Modal } from "semantic-ui-react";
import { InvenioAdministrationActionsApi } from "../api/actions";
import { Button } from "semantic-ui-react";
import { NotificationContext } from "../ui_messages";
import { ErrorMessage } from "../ui_messages";
import isEmpty from "lodash/isEmpty";
import { GenerateForm } from "./GenerateForm";
import { deserializeFieldErrors } from "../components/utils";
import { i18next } from "@translations/invenio_administration/i18next";
import mapValues from "lodash/mapValues";

export class AdminForm extends Component {
  constructor(props) {
    super(props);
    const { resource, resourceSchema } = props;

    this.state = {
      error: undefined,
      formData: resource
        ? resource
        : mapValues(resourceSchema, function (value) {
            const defaultValue = value.metadata?.default;
            if (defaultValue) {
              return defaultValue;
            }
            return "";
          }),
    };
  }

  static contextType = NotificationContext;

  onSubmit = async (values, actions) => {
    const { apiEndpoint, pid, successCallback, create } = this.props;
    const { addNotification } = this.context;
    let response;
    try {
      if (create) {
        response = await InvenioAdministrationActionsApi.createResource(
          apiEndpoint,
          values
        );
      } else {
        response = await InvenioAdministrationActionsApi.editResource(
          apiEndpoint,
          pid,
          values
        );
      }
      actions.setSubmitting(false);
      actions.resetForm({ values: { ...values } });
      addNotification({
        title: "Success",
        content: "Your changes were successfully submitted",
        type: "success",
      });
      successCallback(response.data);
    } catch (e) {
      console.error(e);
      let errorMessage = e.message;

      // API errors need to be deserialised to highlight fields.
      const apiResponse = e?.response?.data;
      if (apiResponse) {
        const apiErrors = apiResponse.errors || [];
        const deserializedErrors = deserializeFieldErrors(apiErrors);
        actions.setErrors(deserializedErrors);
        errorMessage = apiResponse.message || errorMessage;
      }

      this.setState({
        error: { header: "Form error", content: errorMessage, id: e.code },
      });
    }
  };

  resetErrorState = () => {
    this.setState({ error: undefined });
  };

  render() {
    const { resourceSchema, create, formFields } = this.props;
    const { formData, error } = this.state;

    return (
      <Formik initialValues={formData} onSubmit={this.onSubmit}>
        {(props) => {
          return (
            <>
              <Modal.Content>
                <SemanticForm
                  id="admin-form"
                  as={Form}
                  onSubmit={(e) => {
                    e.preventDefault();
                    props.handleSubmit();
                  }}
                >
                  <GenerateForm
                    formFields={formFields}
                    jsonSchema={resourceSchema}
                    create={create}
                  />
                  {!isEmpty(error) && (
                    <ErrorMessage
                      {...error}
                      removeNotification={this.resetErrorState}
                    />
                  )}
                </SemanticForm>
              </Modal.Content>

              <Modal.Actions>
                <Button
                  form="admin-form"
                  type="submit"
                  primary
                  loading={props.isSubmitting}
                  disabled={props.isSubmitting}
                >
                  {i18next.t("Save")}
                </Button>
              </Modal.Actions>
            </>
          );
        }}
      </Formik>
    );
  }
}

AdminForm.propTypes = {
  resource: PropTypes.object,
  resourceSchema: PropTypes.object.isRequired,
  apiEndpoint: PropTypes.string.isRequired,
  pid: PropTypes.string,
  create: PropTypes.bool,
  formFields: PropTypes.object,
  successCallback: PropTypes.func,
};

AdminForm.defaultProps = {
  resource: undefined,
  create: false,
  pid: undefined,
  formFields: undefined,
  successCallback: () => {},
};
