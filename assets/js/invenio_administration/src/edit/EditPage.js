import React, { Component } from "react";
import PropTypes from "prop-types";
import { InvenioAdministrationActionsApi } from "../api/actions";
import { Grid } from "semantic-ui-react";

import { AdminForm } from "../formik/AdminForm";
import Loader from "../components/Loader";
import { ErrorPage } from "../components";
import _isEmpty from "lodash/isEmpty";

export class EditPage extends Component {
  constructor(props) {
    super(props);
    this.state = { loading: true, resource: undefined, error: undefined };
  }

  componentDidMount() {
    this.getResource();
  }

  getResource = async () => {
    const { apiEndpoint, pid } = this.props;
    try {
      const response = await InvenioAdministrationActionsApi.getResource(
        apiEndpoint,
        pid
      );
      this.setState({
        loading: false,
        resource: response.data,
        error: undefined,
      });
    } catch (e) {
      console.error(e);
      this.setState({ error: e });
    }
  };

  handleOnEditSuccess = () => {
    const { listUIEndpoint } = this.props;
    window.location.replace(listUIEndpoint);
  };

  render() {
    const { resourceSchema, apiEndpoint, pid, formFields } = this.props;
    const { loading, resource, error } = this.state;

    return (
      <Loader isLoading={loading}>
        <ErrorPage
          error={!_isEmpty(error)}
          errorCode={error?.response.status}
          errorMessage={error?.response.data}
        >
          <Grid>
            <Grid.Column width={12}>
              <AdminForm
                resourceSchema={resourceSchema}
                resource={resource}
                apiEndpoint={apiEndpoint}
                formFields={formFields}
                pid={pid}
                successCallback={this.handleOnEditSuccess}
              />
            </Grid.Column>
          </Grid>
        </ErrorPage>
      </Loader>
    );
  }
}

EditPage.propTypes = {
  resourceSchema: PropTypes.object.isRequired,
  apiEndpoint: PropTypes.string.isRequired,
  pid: PropTypes.string.isRequired,
  formFields: PropTypes.object,
  listUIEndpoint: PropTypes.string.isRequired,
};

EditPage.defaultProps = {
  formFields: undefined,
};
