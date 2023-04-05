// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_communities/i18next";
import { DateTime } from "luxon";

const timestampToRelativeTime = (timestamp) =>
  DateTime.fromISO(timestamp).setLocale(i18next.language).toRelative();

export const requestsResultProps = (result, updateQueryState, currentQueryState) => {
  const createdDate = new Date(result.created);
  const createdBy = result.created_by;
  let creatorName = "";
  const isCreatorUser = "user" in createdBy;
  const isCreatorCommunity = "community" in createdBy;
  if (isCreatorUser) {
    creatorName =
      result.expanded?.created_by.profile?.full_name ||
      result.expanded?.created_by.username ||
      createdBy.user;
  } else if (isCreatorCommunity) {
    creatorName = result.expanded?.created_by.metadata?.title || createdBy.community;
  }
  return {
    differenceInDays: timestampToRelativeTime(createdDate.toISOString()),
    isCreatorCommunity: isCreatorCommunity,
    creatorName: creatorName,
    refreshAfterAction: () => {
      updateQueryState(currentQueryState);
    },
  };
};
