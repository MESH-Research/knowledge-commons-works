// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_app_rdm/i18next";
import React from "react";
import RequestTypeLabel from "@js/invenio_requests/request/RequestTypeLabel";
import RequestStatusLabel from "@js/invenio_requests/request/RequestStatusLabel";
import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import { Icon, Item } from "semantic-ui-react";
import { RightBottomLabel } from "./RightBottomLabel";
import PropTypes from "prop-types";
import { requestsResultProps } from "./RequestsResultProps";

export const ComputerTabletRequestsItem = ({
  result,
  community,
  updateQueryState,
  currentQueryState,
}) => {
  const { differenceInDays, isCreatorCommunity, creatorName, refreshAfterAction } =
    requestsResultProps(result, updateQueryState, currentQueryState);
  return (
    <Item key={community.id} className="community-item computer tablet only flex">
      <div className="status-icon mr-10">
        <Item.Content verticalAlign="top">
          <Item.Extra>
            <Icon color="black" name="conversation" />
          </Item.Extra>
        </Item.Content>
      </div>
      <Item.Content>
        <Item.Extra>
          {result.type && <RequestTypeLabel type={result.type} />}
          {result.status && result.is_closed && (
            <RequestStatusLabel status={result.status} />
          )}
          <div className="right floated">
            <RequestActionController
              request={result}
              actionSuccessCallback={refreshAfterAction}
            />
          </div>
        </Item.Extra>
        <Item.Header className="truncate-lines-2">
          <a
            className="header-link"
            href={`/communities/${community.slug}/requests/${result.id}`}
          >
            {result.title}
          </a>
        </Item.Header>
        <Item.Meta>
          <small>
            {i18next.t(`Opened {{difference}} by`, {
              difference: differenceInDays,
            })}{" "}
            {isCreatorCommunity && <Icon className="default-margin" name="users" />}{" "}
            {creatorName}
          </small>
          <RightBottomLabel className="right floated" result={result} />
        </Item.Meta>
      </Item.Content>
    </Item>
  );
};

ComputerTabletRequestsItem.propTypes = {
  result: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
  updateQueryState: PropTypes.func.isRequired,
  currentQueryState: PropTypes.object.isRequired,
};
