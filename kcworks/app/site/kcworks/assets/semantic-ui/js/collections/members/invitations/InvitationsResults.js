/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Grid } from "semantic-ui-react";
import { ResultsPerPage, Pagination, ResultsList } from "react-searchkit";
import PropTypes from "prop-types";
import { Trans } from "react-i18next";

export const InvitationsResults = ({ paginationOptions, currentResultsState }) => {
  const { total } = currentResultsState.data;
  return (
    total && (
      <Grid>
        <Grid.Row>
          <Grid.Column width={16}>
            <ResultsList />
          </Grid.Column>
        </Grid.Row>
        <Grid.Row verticalAlign="middle">
          <Grid.Column width={8} textAlign="right">
            <Pagination
              options={{
                size: "mini",
                showFirst: false,
                showLast: false,
              }}
            />
          </Grid.Column>
          <Grid.Column textAlign="right" width={8}>
            <ResultsPerPage
              values={paginationOptions.resultsPerPage}
              label={(cmp) => (
                <Trans key="communitiesInvitationsResult" count={cmp}>
                  {cmp} results per page
                </Trans>
              )}
            />
          </Grid.Column>
        </Grid.Row>
      </Grid>
    )
  );
};

InvitationsResults.propTypes = {
  paginationOptions: PropTypes.object.isRequired,
  currentResultsState: PropTypes.object.isRequired,
};
