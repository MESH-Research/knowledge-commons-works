import React from "react";
import { PropTypes } from "prop-types";
import { Grid, Header } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";

const CommunityRecordsSearchEmptyResults = ({ queryString, searchPath, resetQuery }) => {
  return (
    <Grid>
      <Grid.Row centered>
        <Grid.Column width={12} textAlign="center">
          <Header as="h2">
            {i18next.t("This collection does not yet include any works you can view")}
          </Header>
        </Grid.Column>
      </Grid.Row>
      {/* <Grid.Row centered>
        <Grid.Column width={8} textAlign="center">
          <Button primary onClick={resetQuery}>
            <Icon name="search" />
            {i18next.t("Start over")}
          </Button>
        </Grid.Column>
      </Grid.Row>
      <Grid.Row centered>
        <Grid.Column width={12}>
          <Segment secondary padded size="large">
            <Header as="h3" size="small">
              {i18next.t("ProTip")}!
            </Header>
            <Trans>
              <p>
                <a href={`${searchPath}?q=metadata.publication_date:[2017-01-01 TO *]`}>
                  metadata.publication_date:[2017-01-01 TO *]
                </a>{" "}
                will give you all the publications from 2017 until today.
              </p>
            </Trans>
            <Trans>
              <p>
                For more tips, check out our{" "}
                <a href="/help/search" title={i18next.t("Search guide")}>
                  search guide
                </a>{" "}
                for defining advanced search queries.
              </p>
            </Trans>
          </Segment>
        </Grid.Column>
      </Grid.Row> */}
    </Grid>
  );
};

CommunityRecordsSearchEmptyResults.propTypes = {
  queryString: PropTypes.string.isRequired,
  resetQuery: PropTypes.func.isRequired,
  searchPath: PropTypes.string,
};

CommunityRecordsSearchEmptyResults.defaultProps = {
  searchPath: "/search",
};

export { CommunityRecordsSearchEmptyResults };