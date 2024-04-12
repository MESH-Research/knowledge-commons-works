import React, { Component } from "react";
import { withCancel } from "react-invenio-forms";
import { http } from "react-invenio-forms";
import { Grid, Message, Container, Loader } from "semantic-ui-react";
import FeaturedCommunity from "./FeaturedCommunity";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_communities/i18next";

export default class FeaturedCommunities extends Component {
  constructor(props) {
    super(props);
    this.state = {
      data: undefined,
      error: undefined,
      isLoading: false,
    };
  }

  componentDidMount() {
    this.fetchData();
  }

  componentWillUnmount() {
    this.cancellableFetch && this.cancellableFetch.cancel();
  }

  fetchData = async () => {
    this.setState({ isLoading: true });

    this.cancellableFetch = withCancel(http.get("/api/communities/featured"));

    try {
      const response = await this.cancellableFetch.promise;
      this.setState({ data: response.data.hits, isLoading: false });
    } catch (error) {
      let errorMessage = error.message;
      if (error.response) {
        errorMessage = error.response.data.message;
      }
      this.setState({
        error: errorMessage,
        isLoading: false,
      });
    }
  };

  render() {
    const { data, error, isLoading } = this.state;
    const {
      columnNumber,
      widescreenColumnWidth,
      mobileColumnWidth,
      tabletColumnWidth,
      computerColumnWidth,
    } = this.props;
    return isLoading ? (
      <Loader active inline="centered" />
    ) : error ? (
      <Container>
        <Message negative>
          <Message.Header>{i18next.t("An error occurred.")}</Message.Header>
          <p>{error}</p>
        </Message>
      </Container>
    ) : data?.hits ? (
      <Grid className="featured-communities" columns={columnNumber} centered>
        {data.hits.map((hit) => (
          <FeaturedCommunity
            key={hit.id}
            community={hit}
            mobileColumnWidth={mobileColumnWidth}
            tabletColumnWidth={tabletColumnWidth}
            computerColumnWidth={computerColumnWidth}
            widescreenColumnWidth={widescreenColumnWidth}
          />
        ))}
      </Grid>
    ) : (
      ""
    );
  }
}

FeaturedCommunities.propTypes = {
  columnNumber: PropTypes.string.isRequired,
  mobileColumnWidth: PropTypes.string.isRequired,
  tabletColumnWidth: PropTypes.string.isRequired,
  computerColumnWidth: PropTypes.string.isRequired,
  widescreenColumnWidth: PropTypes.string.isRequired,
};
