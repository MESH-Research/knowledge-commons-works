/*
* This file is part of Knowledge Commons Works.
*   Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
*   Copyright (C) 2020-2024 CERN.
*   Copyright (C) 2020-2024 Northwestern University.
*   Copyright (C) 2020-2024 T U Wien.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import { RequestLinksExtractor } from "@js/invenio_requests/api";
import React from "react";
import Overridable from "react-overridable";
import { RequestAction } from "@js/invenio_requests/request/actions/RequestAction";
import { Dropdown } from "semantic-ui-react";
import { AppMedia } from "@js/invenio_theme/Media";

const RequestActions = ({ request, size }) => {
  let actions = Object.keys(new RequestLinksExtractor(request).actions);
  const { MediaContextProvider, Media } = AppMedia;

  // FIXME: This is a temporary fix to hide the cancel action for
  // people other than the requester. This should be handled on the server side.
  if ( !request.expanded.created_by.is_current_user ) {
    actions = actions.filter(action => action !== "cancel");
  }

  return (
      <MediaContextProvider>
        <Media greaterThanOrEqual="tablet" className="media-inline-block">
          {actions.map((action) => (
            <RequestAction
              action={action}
              key={action}
              requestType={request.type}
              size={size}
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
            className="icon tiny"
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
  );
};

export { RequestActions };