import {
  SearchAppFacets,
  SearchAppResultsPane,
} from "@js/invenio_search_ui/components";
import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React from "react";
import { GridResponsiveSidebarColumn } from "react-invenio-forms";
import { SearchBar, Sort } from "react-searchkit";
import { Button, Container, Grid } from "semantic-ui-react";

export const CommunitiesSearchLayout = ({ config, appName }) => {
  const [sidebarVisible, setSidebarVisible] = React.useState(false);
  return (
    <Container>
      <Grid>
        {/* Mobile/tablet search header */}
        <Grid.Row className="mobile tablet only">
          <Grid.Column mobile={2} tablet={1} verticalAlign="middle" className="mt-10">
            <Button
              basic
              icon="sliders"
              onClick={() => setSidebarVisible(true)}
              aria-label={i18next.t("Filter results")}
            />
          </Grid.Column>

          <Grid.Column mobile={14} tablet={15} floated="right" className="mt-10">
            <SearchBar placeholder={i18next.t("Search collections...")} />
          </Grid.Column>
        </Grid.Row>

        <Grid.Row className="mobile tablet only">
          <Grid.Column width={16} textAlign="right">
            {config.sortOptions && (
              <Sort
                values={config.sortOptions}
                label={(cmp) => (
                  <>
                    {/* FIXME: Work out layout placement */}
                    {/* <label className="mr-10">{i18next.t("Sort by")}</label> */}
                    {cmp}
                  </>
                )}
              />
            )}
          </Grid.Column>
        </Grid.Row>
        {/* End mobile/tablet search header */}

        {/* Desktop search header */}
        <Grid.Row className="computer only">
          <Grid.Column width={8} floated="right">
            <SearchBar placeholder={i18next.t("Search collections...")} />
          </Grid.Column>

          <Grid.Column width={4} textAlign="right">
            {config.sortOptions && (
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
            )}
          </Grid.Column>
        </Grid.Row>
        {/* End desktop search header */}

        <Grid.Row>
          <GridResponsiveSidebarColumn
            width={4}
            open={sidebarVisible}
            onHideClick={() => setSidebarVisible(false)}
            // eslint-disable-next-line react/no-children-prop
            children={<SearchAppFacets aggs={config.aggs} appName={appName} />}
          />
          <Grid.Column mobile={16} tablet={16} computer={12}>
            <SearchAppResultsPane
              layoutOptions={config.layoutOptions}
              appName={appName}
            />
          </Grid.Column>
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
