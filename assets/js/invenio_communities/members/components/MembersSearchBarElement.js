/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { Input } from "semantic-ui-react";
import { i18next } from "@translations/invenio_communities/i18next";
import { withState } from "react-searchkit";

export const MembersSearchBarElement = withState(
  ({
    placeholder: passedPlaceholder,
    queryString,
    onInputChange,
    updateQueryState,
    uiProps,
  }) => {
    const placeholder = passedPlaceholder || i18next.t("Search in members ...");
    const onBtnSearchClick = () => {
      updateQueryState({ queryString });
    };
    const onKeyPress = (event) => {
      if (event.key === "Enter") {
        updateQueryState({ queryString });
      }
    };
    return (
      <Input
        action={{
          icon: "search",
          onClick: onBtnSearchClick,
          className: "search",
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
