import React, { Component } from "react";
import PropTypes from "prop-types";
import { Grid } from "semantic-ui-react";
import { AdminForm } from "../formik/AdminForm";

export class CreatePage extends Component {
  handleCreate = () => {
    const { listUIEndpoint } = this.props;
    window.location.replace(listUIEndpoint);
  };

  render() {
    const { resourceSchema, apiEndpoint, formFields } = this.props;

    return (
      <Grid>
        <Grid.Column width={12}>
          <AdminForm
            resourceSchema={resourceSchema}
            apiEndpoint={apiEndpoint}
            formFields={formFields}
            create
            successCallback={this.handleCreate}
          />
        </Grid.Column>
      </Grid>
    );
  }
}

CreatePage.propTypes = {
  resourceSchema: PropTypes.object.isRequired,
  apiEndpoint: PropTypes.string.isRequired,
  formFields: PropTypes.object,
  listUIEndpoint: PropTypes.string.isRequired,
};

CreatePage.defaultProps = {
  formFields: undefined,
};
