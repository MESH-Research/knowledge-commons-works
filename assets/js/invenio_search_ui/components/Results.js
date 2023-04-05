/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 * Copyright (C) 2021 Graz University of Technology.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import Overridable from "react-overridable";
import React, { useContext } from "react";
import {
  Count,
  LayoutSwitcher,
  ResultsMultiLayout,
  Sort,
  ResultsList,
  ResultsGrid,
} from "react-searchkit";
import { Grid } from "semantic-ui-react";
import { SearchConfigurationContext } from "./context";
import { i18next } from "@translations/invenio_search_ui/i18next";
import { InvenioSearchPagination } from "./InvenioSearchPagination";

export const Results = ({ currentResultsState = {} }) => {
  const { total } = currentResultsState.data;
  const { sortOptions, layoutOptions, paginationOptions, buildUID } =
    useContext(SearchConfigurationContext);
  const multipleLayouts = layoutOptions.listView && layoutOptions.gridView;
  return (
    (total || null) && (
      <Overridable
        id={buildUID("SearchApp.results")}
        {...{
          sortOptions,
          paginationOptions,
          currentResultsState,
          layoutOptions,
        }}
      >
        <Grid relaxed>
          <Grid.Row>
            <Grid.Column>
              {multipleLayouts ? (
                <ResultsMultiLayout />
              ) : layoutOptions.listView ? (
                <ResultsList />
              ) : (
                <ResultsGrid />
              )}
            </Grid.Column>
          </Grid.Row>
          <InvenioSearchPagination paginationOptions={paginationOptions} />
        </Grid>
      </Overridable>
    )
  );
};

export const ResultOptions = ({ currentResultsState = {} }) => {
  const { total } = currentResultsState.data;
  const {
    sortOptions,
    paginationOptions,
    sortOrderDisabled,
    layoutOptions,
    buildUID,
  } = useContext(SearchConfigurationContext);
  const multipleLayouts = layoutOptions.listView && layoutOptions.gridView;
  return (
    (total || null) && (
      <Overridable
        id={buildUID("SearchApp.resultOptions")}
        {...{
          currentResultsState,
          sortOptions,
          paginationOptions,
          layoutOptions,
        }}
      >
        <Grid>
          <Grid.Row verticalAlign="middle">
            <Grid.Column textAlign="left" width={multipleLayouts ? 5 : 8}>
              <Count label={(cmp) => <>{cmp} result(s) found</>} />
              <br />
            </Grid.Column>
            <Grid.Column width={8} textAlign="right">
              {sortOptions && (
                <Overridable
                  id={buildUID("SearchApp.sort")}
                  options={sortOptions}
                >
                  <Sort
                    sortOrderDisabled={sortOrderDisabled || false}
                    values={sortOptions}
                    ariaLabel={i18next.t("Sort")}
                    label={(cmp) => (
                      <>
                        <label className="mr-10">{i18next.t("Sort by")}</label>{cmp}
                      </>
                    )}
                  />
                </Overridable>
              )}
            </Grid.Column>
            {multipleLayouts ? (
              <Grid.Column width={3} textAlign="right">
                <LayoutSwitcher />
              </Grid.Column>
            ) : null}
          </Grid.Row>
        </Grid>
      </Overridable>
    )
  );
};
