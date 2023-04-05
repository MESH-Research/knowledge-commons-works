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
import PropTypes from "prop-types";

export const InvitationsSearchBarElement = ({
  onBtnSearchClick,
  onInputChange,
  onKeyPress,
  queryString,
  uiProps,
}) => {
  return (
    <Input
      className="invitation-searchbar rel-ml-2"
      action={{
        icon: "search",
        onClick: onBtnSearchClick,
        className: "search",
      }}
      fluid
      placeholder={i18next.t("Search in invitations...")}
      onChange={(_, { value }) => {
        onInputChange(value);
      }}
      value={queryString}
      onKeyPress={onKeyPress}
      {...uiProps}
    />
  );
};

InvitationsSearchBarElement.propTypes = {
  onBtnSearchClick: PropTypes.func.isRequired,
  onInputChange: PropTypes.func.isRequired,
  onKeyPress: PropTypes.func.isRequired,
  queryString: PropTypes.string.isRequired,
  uiProps: PropTypes.object.isRequired,
};
