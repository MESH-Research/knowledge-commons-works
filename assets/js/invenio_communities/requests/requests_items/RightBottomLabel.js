// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import { Icon } from "semantic-ui-react";
import { DateTime } from "luxon";
import PropTypes from "prop-types";

export const RightBottomLabel = ({ result, className }) => {
  return (
    <small className={className}>
      {result.receiver.community && result.expanded?.receiver.metadata.title && (
        <>
          <Icon className="default-margin" name="users" />
          <span className="ml-5">{result.expanded?.receiver.metadata.title}</span>
        </>
      )}
      {result.expires_at && (
        <span>
          {i18next.t("Expires at:")}{" "}
          {DateTime.fromISO(result.expires_at).toLocaleString(i18next.language)}
        </span>
      )}
    </small>
  );
};

RightBottomLabel.propTypes = {
  result: PropTypes.object.isRequired,
  className: PropTypes.string.isRequired,
};
