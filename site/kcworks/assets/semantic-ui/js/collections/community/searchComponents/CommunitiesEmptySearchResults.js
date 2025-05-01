import React from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/kcworks/i18next";
import { Button, Segment, Header, Icon } from "semantic-ui-react";

export const CommunitiesEmptySearchResults = (props) => {
  const { queryString, resetQuery } = props;
  return (
    <Segment placeholder textAlign="center">
      <Header icon>
        <Icon name="search" />
        {i18next.t("No collections found!")}
      </Header>
      {queryString && (
        <Button primary onClick={() => resetQuery()}>
          {i18next.t("Reset search")}
        </Button>
      )}
    </Segment>
  );
};

CommunitiesEmptySearchResults.propTypes = {
  queryString: PropTypes.string.isRequired,
  resetQuery: PropTypes.func.isRequired,
};
