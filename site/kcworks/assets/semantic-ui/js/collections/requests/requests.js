// This file is part of Invenio
// Copyright (C) 2022-2023 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_communities/i18next";
import PropTypes from "prop-types";
import React from "react";
import { withState } from "react-searchkit";
import { Input } from "semantic-ui-react";

import {
  MobileRequestItem,
  ComputerTabletRequestItem,
} from "@js/invenio_requests/search";

export const RecordSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    updateQueryState,
    currentQueryState,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search");

    const onSearch = () => {
      updateQueryState({ ...currentQueryState, queryString });
    };

    const onBtnSearchClick = () => {
      onSearch();
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        onSearch();
      }
    };
    return (
      <Input
        action={{
          "icon": "search",
          "onClick": onBtnSearchClick,
          "className": "search",
          "aria-label": i18next.t("Search"),
        }}
        fluid
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
      />
    );
  }
);

export const RequestsResultsItemTemplateCommunity = ({ result, community }) => {
  const ComputerTabletRequestsItemWithState = withState(ComputerTabletRequestItem);
  const MobileRequestsItemWithState = withState(MobileRequestItem);
  const detailsURL = `/communities/${community.slug}/requests/${result.id}`;
  return (
    <>
      <ComputerTabletRequestsItemWithState result={result} detailsURL={detailsURL} />
      <MobileRequestsItemWithState result={result} detailsURL={detailsURL} />
    </>
  );
};

RequestsResultsItemTemplateCommunity.propTypes = {
  result: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};
