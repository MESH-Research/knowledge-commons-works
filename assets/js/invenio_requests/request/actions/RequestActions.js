// This file is part of InvenioRequests
// Copyright (C) 2022 CERN.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { RequestLinksExtractor } from "../../api";
import React from "react";
import Overridable from "react-overridable";
import { RequestAction } from "./RequestAction";
import { Dropdown } from "semantic-ui-react";
import { AppMedia } from "@js/invenio_theme/Media";

export const RequestActions = ({ request }) => {
  const actions = Object.keys(new RequestLinksExtractor(request).actions);
  const { MediaContextProvider, Media } = AppMedia;
  return (
    <Overridable
      id="InvenioRequests.RequestActions.layout"
      request={request}
      actions={actions}
    >
      <MediaContextProvider>
        <Media greaterThanOrEqual="tablet" className="media-inline-block">
          {actions.map((action) => (
            <RequestAction
              action={action}
              key={action}
              requestType={request.type}
            />
          ))}
        </Media>
        <Media lessThan="tablet">
          <Dropdown
            text="Actions"
            icon="caret down"
            floating
            labeled
            button
            className="icon rel-mt-1"
          >
            <Dropdown.Menu>
              {actions.map((action) => {
                return (
                  <RequestAction
                    key={action}
                    action={action}
                    requestType={request.type}
                  />
                );
              })}
            </Dropdown.Menu>
          </Dropdown>
        </Media>
      </MediaContextProvider>
    </Overridable>
  );
};

export default Overridable.component(
  "InvenioRequests.RequestActions",
  RequestActions
);
