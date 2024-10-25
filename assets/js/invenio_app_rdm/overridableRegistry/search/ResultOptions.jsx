import React, { useContext } from "react";
import Overridable from "react-overridable";
import { Count, Sort, withState } from "react-searchkit";
import { Button, Grid } from "semantic-ui-react";
import { LayoutSwitcher } from "react-searchkit";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components/context";
import i18next from "i18next";

const ResultOptions = ({
  appName,
  facetsAvailable,
  facetsEnabled,
  currentResultsState = {},
  sortOptions: overrideSortOptions,
  layoutOptions: overrideLayoutOptions,
  setSidebarVisible,
  ...rest
}) => {
  const { total } = currentResultsState.data;
  const {
    sortOptions={overrideSortOptions},
    // paginationOptions,
    sortOrderDisabled,
    layoutOptions={overrideLayoutOptions},
    buildUID,
  } = useContext(SearchConfigurationContext);

  const multipleLayouts = layoutOptions.listView && layoutOptions.gridView;

  const columnWidthsSingleLayout = {
    filterButton: {
      mobile: 2,
      tablet: 1,
    },
    sortOptions: {
      mobile: 8,
      tablet: 7,
      computer: 4,
    },
    count: {
      mobile: 4,
      tablet: 8,
      computer: 7,
    },
    sidebarSpacer: {
      mobile: 0,
      tablet: 0,
      computer: 5,
    },
  };
  const columnWidthsMultipleLayouts = {
    filterButton: {
      mobile: 2,
      tablet: 1,
    },
    sortOptions: {
      mobile: 10,
      tablet: 5,
      computer: 5,
    },
    count: {
      mobile: 4,
      tablet: 7,
      computer: 8,
    },
    layoutSwitcher: {
      mobile: 3,
      tablet: 3,
      computer: 3,
    },
    sidebarSpacer: {
      mobile: 0,
      tablet: 0,
      computer: 5,
    },
  };

  const columnWidths = multipleLayouts
    ? columnWidthsMultipleLayouts
    : columnWidthsSingleLayout;

  return (
    (total || null) && (
      <Grid.Row
        verticalAlign="middle"
        className="search-options-row search-results-options record-search-options justify-space-between mb-25"
      >
        {facetsAvailable && (
          <Grid.Column
            only="mobile tablet"
            {...columnWidths.filterButton}
            textAlign="left"
            verticalAlign="middle"
            className="search-results-options-filter-button"
          >
            <Button
              basic
              icon="sliders"
              onClick={() => setSidebarVisible(true)}
              aria-label={i18next.t("Filter results")}
            />
          </Grid.Column>
        )}

        <Grid.Column
          {...columnWidths.sortOptions}
          className=""
        >
          {sortOptions && (
            <Overridable id={buildUID("SearchApp.sort")} options={sortOptions}>
              <Sort
                sortOrderDisabled={sortOrderDisabled || false}
                values={sortOptions}
                ariaLabel={i18next.t("Sort")}
                className="fluid"
                label={(cmp) => (
                  <>
                    <label className="">{i18next.t("Sort by")}</label>
                    {cmp}
                  </>
                )}
              />
            </Overridable>
          )}
        </Grid.Column>

        <Grid.Column
          {...columnWidths.count}
          textAlign="right"
          className="search-results-options-count"
        >
          <Count
            label={(cmp) => (
              <>
                {cmp}{" "}
                <span className="tablet computer widescreen large monitor only">
                  &nbsp;works{" "}
                </span>
                found
              </>
            )}
            className="circular"
          />
          <br />
        </Grid.Column>
        {multipleLayouts ? (
          <Grid.Column {...columnWidths.layoutSwitcher} textAlign="right">
            <LayoutSwitcher />
          </Grid.Column>
        ) : null}

        <Grid.Column
          {...columnWidths.sidebarSpacer}
        >
        </Grid.Column>

      </Grid.Row>
    )
  );
};


const ResultOptionsWithState = withState(ResultOptions);

export { ResultOptionsWithState };