import { AdminUIRoutes } from "@js/invenio_administration/src/routes";
import PropTypes from "prop-types";
import React, { Component } from "react";
import { Grid, Header, Divider, Container } from "semantic-ui-react";
import { InvenioAdministrationActionsApi } from "../api/actions";
import DetailsTable from "./DetailsComponent";
import { Actions } from "../actions/Actions";
import _isEmpty from "lodash/isEmpty";
import { sortFields } from "../components/utils";
import { Loader, ErrorPage } from "../components";

export default class AdminDetailsView extends Component {
  constructor(props) {
    super(props);
    this.state = {
      loading: true,
      data: undefined,
      error: undefined,
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  fetchData = async () => {
    this.setState({ loading: true });
    const { apiEndpoint, pid, requestHeaders } = this.props;
    try {
      const response = await InvenioAdministrationActionsApi.getResource(
        apiEndpoint,
        pid,
        requestHeaders
      );

      this.setState({
        loading: false,
        data: response.data,
        error: undefined,
      });
    } catch (e) {
      console.error(e);
      this.setState({ error: e });
    }
  };

  childrenWithData = (data, columns) => {
    const { children } = this.props;
    return React.Children.map(children, (child) => {
      if (React.isValidElement(child)) {
        return React.cloneElement(child, { data: data, columns: columns });
      }
      return child;
    });
  };

  handleDelete = () => {
    // after deleting the resource go back to the list view
    const { listUIEndpoint } = this.props;
    window.location.href = listUIEndpoint;
  };

  render() {
    const {
      title,
      columns,
      actions,
      apiEndpoint,
      idKeyPath,
      listUIEndpoint,
      resourceSchema,
      resourceName,
      displayDelete,
      displayEdit,
      uiSchema,
    } = this.props;
    const { loading, data, error } = this.state;
    const sortedColumns = sortFields(resourceSchema);
    return (
      <Loader isLoading={loading}>
        <ErrorPage
          error={!_isEmpty(error)}
          errorCode={error?.response.status}
          errorMessage={error?.response.data}
        >
          <Grid stackable>
            <Grid.Row columns="2">
              <Grid.Column verticalAlign="middle">
                <Header as="h1">{title}</Header>
              </Grid.Column>
              <Grid.Column verticalAlign="middle" floated="right" textAlign="right">
                <Actions
                  title={title}
                  resourceName={resourceName}
                  apiEndpoint={apiEndpoint}
                  editUrl={AdminUIRoutes.editView(listUIEndpoint, data, idKeyPath)}
                  actions={actions}
                  displayEdit={displayEdit}
                  displayDelete={displayDelete}
                  resource={data}
                  idKeyPath={idKeyPath}
                  successCallback={this.handleDelete}
                  listUIEndpoint={listUIEndpoint}
                />
              </Grid.Column>
            </Grid.Row>
          </Grid>
          <Divider />
          <Container fluid>
            <DetailsTable data={data} schema={sortedColumns} uiSchema={uiSchema} />
            {this.childrenWithData(data, columns)}
          </Container>
        </ErrorPage>
      </Loader>
    );
  }
}

AdminDetailsView.propTypes = {
  actions: PropTypes.object,
  apiEndpoint: PropTypes.string.isRequired,
  columns: PropTypes.object.isRequired,
  displayEdit: PropTypes.bool.isRequired,
  displayDelete: PropTypes.bool.isRequired,
  pid: PropTypes.string.isRequired,
  title: PropTypes.string.isRequired,
  children: PropTypes.object,
  resourceName: PropTypes.string.isRequired,
  idKeyPath: PropTypes.string.isRequired,
  listUIEndpoint: PropTypes.string.isRequired,
  resourceSchema: PropTypes.object.isRequired,
  requestHeaders: PropTypes.object.isRequired,
  uiSchema: PropTypes.object.isRequired,
};

AdminDetailsView.defaultProps = {
  actions: undefined,
  children: undefined,
};
