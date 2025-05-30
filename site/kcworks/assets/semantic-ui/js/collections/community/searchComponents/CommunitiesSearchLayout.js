import {
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/kcworks/i18next";
import PropTypes from "prop-types";
import React from "react";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { SearchBar, Sort } from "react-searchkit";
import { Button, Container, Grid, Icon } from "semantic-ui-react";

export const CommunitiesSearchLayout = ({ config, appName }) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  return (
    <Container>
      <Grid>
        {/* Mobile/tablet search header */}
        <Grid.Row className="mobile tablet only">
          <Grid.Column
            mobile={16}
            tablet={16}
            floated="right"
            className="mt-10"
          >
            <SearchBar placeholder={i18next.t("Search collections...")} />
          </Grid.Column>
        </Grid.Row>

        <Grid.Row className="mobile tablet only">
          <Grid.Column
            mobile={2}
            tablet={1}
            verticalAlign="middle"
            className=""
          >
            <Button
              basic
              icon="sliders"
              onClick={() => setSidebarVisible(true)}
              aria-label={i18next.t("Filter results")}
            />
          </Grid.Column>
          <Grid.Column mobile={14} tablet={15} align="right">
            {config.sortOptions && (
              <Sort
                values={config.sortOptions}
                label={(cmp) => (
                  <>
                    {/* FIXME: Work out layout placement */}
                    {/* <label className="mr-10">Sort by</label> */}
                    {cmp}
                  </>
                )}
              />
            )}
          </Grid.Column>
        </Grid.Row>
        {/* End mobile/tablet search header */}

        {/* Desktop search header */}
        <Grid.Row className="computer widescreen large-monitor only communities-search-bar">
          <Grid.Column width={12}>
            <SearchBar placeholder={i18next.t("Search collections...")} />
          </Grid.Column>
          <Grid.Column width={4} />
        </Grid.Row>
        {config.sortOptions && (
          <Grid.Row className="computer widescreen large-monitor only communities-search-options">
            <Grid.Column width={12}>
              <Sort
                values={config.sortOptions}
                label={(cmp) => (
                  <>
                    {/* FIXME: Work out layout placement
                    <label className="mr-10">{i18next.t("Sort by")}</label> */}
                    {cmp}
                  </>
                )}
              />
            </Grid.Column>
            <Grid.Column width={4} />
          </Grid.Row>
        )}
        {/* End desktop search header */}

        <Grid.Row>
          <Grid.Column mobile={16} tablet={16} computer={12}>
            <SearchAppResultsPane
              layoutOptions={config.layoutOptions}
              appName={appName}
            />
          </Grid.Column>
          <GridResponsiveSidebarColumn
            width={4}
            open={sidebarVisible}
            onHideClick={() => setSidebarVisible(false)}
            // eslint-disable-next-line react/no-children-prop
            children={
              <>
                <h2 className="ui header mobile tablet only">{i18next.t("Search filters")}</h2>
                <SearchAppFacets aggs={config.aggs} appName={appName} />
              </>
            }
          />
        </Grid.Row>
      </Grid>
    </Container>
  );
};

CommunitiesSearchLayout.propTypes = {
  config: PropTypes.object.isRequired,
  appName: PropTypes.string,
};

CommunitiesSearchLayout.defaultProps = {
  appName: "",
};
