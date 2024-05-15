import React, { useContext } from "react";
import Overridable from "react-overridable";
import { Count, Sort } from "react-searchkit";
import { Grid } from "semantic-ui-react";
import { LayoutSwitcher } from "react-searchkit";
import { SearchConfigurationContext } from "@js/invenio_search_ui/components/context";
import i18next from "i18next";

export const ResultOptions = ({
  currentResultsState = {},
  ...rest
}) => {
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
        <Grid>
          <Grid.Row verticalAlign="middle" className="stackable sort-options-row">
            <Grid.Column textAlign="left" width={multipleLayouts ? 5 : 8}>
              <Count label={(cmp) => <>{cmp} work(s) found</>} />
              <br />
            </Grid.Column>
            <Grid.Column mobile={10} tablet={8} computer={8} textAlign="right">
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
                        <label className="mr-10">{i18next.t("Sort by")}</label>
                        {cmp}
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
    )
  );
};
