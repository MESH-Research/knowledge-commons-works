// This file is part of Invenio
// Copyright (C) 2022 CERN.
//
// Invenio is free software; you can redistribute it and/or modify it under the
// terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/kcworks/i18next";
import React from "react";
import { withState } from "react-searchkit";
import { Input } from "semantic-ui-react";

export const CommunityRecordsSingleSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    updateQueryState,
    currentQueryState,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search");
    const onBtnSearchClick = () => {
      // Preserve current query state (including page and size) when updating search
      updateQueryState({ ...currentQueryState, queryString, filters: [] });
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        // Preserve current query state (including page and size) when updating search
        updateQueryState({ ...currentQueryState, queryString, filters: [] });
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
