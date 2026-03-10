// kcworks override for the community selection search in the deposit modal.
// Reintroduces ResultsList.item parametrization with a kcworks-specific list item
// that uses CommunityCompactItem from @js/kcworks/collections/...

import { i18next } from "@translations/invenio_modular_deposit_form/i18next";
import React, { Component, useState, useEffect, useRef } from "react";
import { OverridableContext, parametrize } from "react-overridable";
import {
  EmptyResults,
  Error,
  InvenioSearchApi,
  Pagination,
  ReactSearchKit,
  ResultsList,
  ResultsLoader,
  withState,
} from "react-searchkit";
import { Grid, Input, Menu, Modal, Button, Icon, Label } from "semantic-ui-react";
import _capitalize from "lodash/capitalize";
import { CommunityCompactItem } from "@js/kcworks/collections/community/communitiesItems/CommunityCompactItem";
import { CommunityContext } from "@js/invenio_rdm_records/src/deposit/components/CommunitySelectionModal/CommunityContext";
import PropTypes from "prop-types";

const KcworksCommunityListItem = ({ result, permissionsPerField }) => {
  const {
    setLocalCommunity,
    getChosenCommunity,
    userCommunitiesMemberships,
    displaySelected,
  } = React.useContext(CommunityContext);

  const { metadata } = result;
  const itemSelected = getChosenCommunity()?.id === result.id;
  const userMembership = userCommunitiesMemberships[result["id"]];

  const actions = (
    <Button
      content={
        displaySelected && itemSelected ? i18next.t("Selected") : i18next.t("Select")
      }
      size="small"
      positive={displaySelected && itemSelected}
      onClick={() => setLocalCommunity(result)}
      aria-label={i18next.t("Select {{title}}", { title: metadata.title })}
    />
  );

  const extraLabels = userMembership && (
    <Label size="small" horizontal color="teal">
      <Icon name="key" />
      {_capitalize(userMembership)}
    </Label>
  );

  return (
    <CommunityCompactItem
      result={result}
      actions={actions}
      extraLabels={extraLabels}
      showPermissionLabel
      permissionsPerField={permissionsPerField}
    />
  );
};

KcworksCommunityListItem.propTypes = {
  result: PropTypes.object.isRequired,
  permissionsPerField: PropTypes.object,
};

KcworksCommunityListItem.defaultProps = {
  permissionsPerField: undefined,
};

const Element = ({
  actionProps,
  autofocus,
  onBtnSearchClick,
  onInputChange,
  onKeyPress,
  placeholder,
  queryString,
}) => {
  const focusInput = useRef(null);

  useEffect(() => {
    if (autofocus && focusInput.current) {
      focusInput.current.focus();
    }
  }, []);

  return (
    <Input
      action={{
        content: "Search",
        onClick: onBtnSearchClick,
        ...actionProps,
      }}
      fluid
      placeholder={placeholder || "Type something"}
      onChange={(_, { value }) => {
        onInputChange(value);
      }}
      value={queryString}
      onKeyPress={onKeyPress}
      ref={focusInput}
    />
  );
};

const CommunitySearchBarElement = ({
  toggleText,
  currentQueryState,
  updateQueryState,
}) => {
  const [currentValue, setCurrentValue] = useState("");

  const executeSearch = () => {
    // Allow for '/' in query string, e.g. for ARLIS/NA
    currentQueryState["queryString"] = currentValue.replace('/', '%2F');
    // FIXME: Hack to remove sortBy from currentQueryState to avoid it
    // constantly reverting to "newest" when searching from deposit form.
    currentQueryState["sortBy"] = null;
    updateQueryState(currentQueryState);
  };

  const onInputChange = (queryString) => {
    setCurrentValue(queryString);
  };

  const onKeyPress = (e) => {
    if (e.key === "Enter") {
      executeSearch();
    }
  };

  return (
    <Element
      actionProps={{
        icon: "search",
        content: null,
        className: "search",
        "aria-label": i18next.t("Search"),
      }}
      autofocus={true}
      onBtnSearchClick={executeSearch}
      onInputChange={onInputChange}
      onKeyPress={onKeyPress}
      placeholder={toggleText}
      queryString={currentValue}
    />
  );
};

const CommunitySearchBar = withState(CommunitySearchBarElement);

export class CommunitySelectionSearch extends Component {
  constructor(props) {
    super(props);
    const {
      apiConfigs: { allCommunities },
    } = this.props;

    this.state = {
      selectedConfig: allCommunities,
    };
  }

  render() {
    const {
      selectedConfig: {
        searchApi: selectedsearchApi,
        appId: selectedAppId,
        initialQueryState: selectedInitialQueryState,
        toggleText,
      },
    } = this.state;

    const {
      apiConfigs: { allCommunities, myCommunities },
      record,
      isInitialSubmission,
      permissionsPerField,
    } = this.props;

    const searchApi = new InvenioSearchApi(selectedsearchApi);

    const overriddenComponents = {
      [`${selectedAppId}.ResultsList.item`]: parametrize(KcworksCommunityListItem, {
        record: record,
        isInitialSubmission: isInitialSubmission,
        permissionsPerField: permissionsPerField,
      }),
    };

    return (
      <OverridableContext.Provider value={overriddenComponents}>
        <ReactSearchKit
          appName={selectedAppId}
          urlHandlerApi={{ enabled: false }}
          searchApi={searchApi}
          key={selectedAppId}
          initialQueryState={selectedInitialQueryState}
          defaultSortingOnEmptyQueryString={
            this.state.selectedConfig.defaultSortingOnEmptyQueryString
          }
        >
          <>
            <Modal.Content as={Grid} verticalAlign="middle" className="m-0 pb-0">
              <Grid.Column
                tablet={8}
                computer={8}
                mobile={16}
                textAlign="left"
                floated="left"
                className="pt-0 pl-0"
              >
                <Menu role="tablist" compact>
                  <Menu.Item
                    as="button"
                    role="tab"
                    id="all-communities-tab"
                    aria-selected={selectedAppId === allCommunities.appId}
                    aria-controls={allCommunities.appId}
                    name="All"
                    active={selectedAppId === allCommunities.appId}
                    onClick={() =>
                      this.setState({
                        selectedConfig: allCommunities,
                      })
                    }
                  >
                    {i18next.t("All")}
                  </Menu.Item>
                  <Menu.Item
                    as="button"
                    role="tab"
                    id="my-communities-tab"
                    aria-selected={selectedAppId === myCommunities.appId}
                    aria-controls={myCommunities.appId}
                    name="My collections"
                    active={selectedAppId === myCommunities.appId}
                    onClick={() =>
                      this.setState({
                        selectedConfig: myCommunities,
                      })
                    }
                  >
                    {i18next.t("My collections")}
                  </Menu.Item>
                </Menu>
              </Grid.Column>
              <Grid.Column
                tablet={8}
                computer={8}
                mobile={16}
                floated="right"
                verticalAlign="middle"
                className="pt-0 pr-0 pl-0"
              >
                <CommunitySearchBar toggleText={toggleText} />
              </Grid.Column>
            </Modal.Content>

            <Modal.Content
              role="tabpanel"
              id={selectedAppId}
              scrolling
              className="community-list-results"
            >
              <ResultsLoader>
                <EmptyResults />
                <Error />
                <ResultsList />
              </ResultsLoader>
            </Modal.Content>

            <Modal.Content className="text-align-center">
              <Pagination />
            </Modal.Content>
          </>
        </ReactSearchKit>
      </OverridableContext.Provider>
    );
  }
}

CommunitySelectionSearch.propTypes = {
  apiConfigs: PropTypes.shape({
    allCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
    myCommunities: PropTypes.shape({
      appId: PropTypes.string.isRequired,
      initialQueryState: PropTypes.object.isRequired,
      searchApi: PropTypes.object.isRequired,
    }),
  }),
  record: PropTypes.object.isRequired,
  isInitialSubmission: PropTypes.bool,
  permissionsPerField: PropTypes.object,
};

CommunitySelectionSearch.defaultProps = {
  apiConfigs: {
    allCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.AllCommunities",
      toggleText: "Search in all collections",
    },
    myCommunities: {
      initialQueryState: { size: 5, page: 1, sortBy: "bestmatch" },
      searchApi: {
        axios: {
          url: "/api/user/communities",
          headers: { Accept: "application/vnd.inveniordm.v1+json" },
        },
      },
      appId: "ReactInvenioDeposit.CommunitySelectionSearch.MyCommunities",
      toggleText: "Search in my collections",
    },
  },
};

