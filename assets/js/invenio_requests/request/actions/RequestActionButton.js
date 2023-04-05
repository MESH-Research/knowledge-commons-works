// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import Overridable from "react-overridable";
import { Button } from "semantic-ui-react";

export const RequestActionButton = ({
  action,
  handleActionClick,
  loading,
  className,
  size,
  requestType,
}) => {
  return (
    <Overridable
      id={`RequestActionButton.${action}`}
      onClick={handleActionClick}
      loading={loading}
      className={className}
      size={size}
    >
      <Button
        onClick={handleActionClick}
        loading={loading}
        requestType={requestType}
      >
        <>{action}</>
      </Button>
    </Overridable>
  );
};

export default Overridable.component(
  "InvenioRequests.RequestActionButton",
  RequestActionButton
);
