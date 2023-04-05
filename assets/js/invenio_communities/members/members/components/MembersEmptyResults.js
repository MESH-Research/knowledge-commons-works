import React, { Component } from "react";
import { Button, Header, Icon, Segment } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";

class MembersEmptyResults extends Component {
  render() {
    const {
      resetQuery,
      extraContent,
      queryString,
      currentQueryState,
      currentResultsState,
    } = this.props;

    const isEmptyPageAfterSearch = currentQueryState.page < 0;
    const isEmptyPage =
      currentQueryState.page === 1 && currentResultsState.data.total === 0;

    return (
      <Segment placeholder textAlign="center">
        <Header icon>
          <Icon name={isEmptyPage ? "users" : "search"} />
          {isEmptyPage && i18next.t("This community has no public members.")}
          {isEmptyPageAfterSearch && i18next.t("No matching members found.")}
        </Header>
        {queryString && <em>Current search "{queryString}"</em>}
        <br />
        {isEmptyPageAfterSearch && (
          <Button primary onClick={() => resetQuery()}>
            Clear query
          </Button>
        )}
        {extraContent}
      </Segment>
    );
  }
}

MembersEmptyResults.propTypes = {
  resetQuery: PropTypes.func.isRequired,
  extraContent: PropTypes.node.isRequired,
  queryString: PropTypes.string.isRequired,
  currentQueryState: PropTypes.object.isRequired,
  currentResultsState: PropTypes.object.isRequired,
};

export default withState(MembersEmptyResults);
