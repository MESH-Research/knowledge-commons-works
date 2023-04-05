// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import { Pagination, ResultsPerPage } from "react-searchkit";
import { Grid } from "semantic-ui-react";

export const InvenioSearchPagination = ({ paginationOptions }) => {
  return (
    <Grid.Row verticalAlign="middle">
      <Grid.Column className="computer tablet only" width={4}></Grid.Column>
      <Grid.Column
        className="computer tablet only"
        width={8}
        textAlign="center"
      >
        <Pagination
          options={{
            size: "mini",
            showFirst: false,
            showLast: false,
          }}
        />
      </Grid.Column>
      <Grid.Column className="mobile only" width={16} textAlign="center">
        <Pagination
          options={{
            boundaryRangeCount: 0,
            showFirst: false,
            showLast: false,
          }}
        />
      </Grid.Column>
      <Grid.Column
        className="computer tablet only "
        textAlign="right"
        width={4}
      >
        <ResultsPerPage
          values={paginationOptions.resultsPerPage}
          label={(cmp) => <> {cmp} results per page</>}
        />
      </Grid.Column>
      <Grid.Column className="mobile only mt-10" textAlign="center" width={16}>
        <ResultsPerPage
          values={paginationOptions.resultsPerPage}
          label={(cmp) => <> {cmp} results per page</>}
        />
      </Grid.Column>
    </Grid.Row>
  );
};
