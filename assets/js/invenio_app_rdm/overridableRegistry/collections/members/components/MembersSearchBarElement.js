/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";
import { i18next } from "@translations/i18next";
import { withState } from "react-searchkit";

export const MembersSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    currentQueryState,
    updateQueryState,
    uiProps,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search in members ...");
    const onBtnSearchClick = () => {
      // NOTE: This fixes the pagination breaking when
      // the search bar is used because the current page is
      // reset to -1, etc.
      updateQueryState({ ...currentQueryState, queryString });
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        // NOTE: This fixes the pagination breaking when
        // the search bar is used because the current page is
        // reset to -1, etc.
        updateQueryState({ ...currentQueryState, queryString });
      }
    };
    return (
      <Input
        action={{
          icon: "search",
          onClick: onBtnSearchClick,
          className: "search",
          title: i18next.t("Search"),
        }}
        fluid
        placeholder={placeholder}
        onChange={(event, { value }) => {
          onInputChange(value);
        }}
        value={queryString}
        onKeyPress={onKeyPress}
        {...uiProps}
      />
    );
  }
);
