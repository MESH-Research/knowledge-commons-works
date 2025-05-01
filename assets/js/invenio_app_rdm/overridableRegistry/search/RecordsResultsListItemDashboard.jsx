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
*
* FIXME: This should be merged with RecordsResultsListItem.js
*/

import React from "react";
import { ComputerTabletUploadsItem } from "../user_dashboard/uploads_items/ComputerTabletUploadsItem";
import _get from "lodash/get";
import { i18next } from "@translations/i18next";
import { http } from "react-invenio-forms";
import PropTypes from "prop-types";

const statuses = {
  in_review: { color: "warning", title: i18next.t("In review") },
  declined: { color: "negative", title: i18next.t("Declined") },
  expired: { color: "expired", title: i18next.t("Expired") },
  draft_with_review: { color: "neutral", title: i18next.t("Draft") },
  draft: { color: "neutral", title: i18next.t("Draft") },
  new_version_draft: { color: "neutral", title: i18next.t("New version draft") },
  published: { color: "positive", title: i18next.t("Published") },
};

const RecordResultsListItemDashboard = ({ currentQueryState, result, key, appName }) => {
  console.log(currentQueryState);
  console.log("appName", appName);
  const editRecord = () => {
    http
      .post(
        `/api/records/${result.id}/draft`,
        {},
        {
          headers: {
            "Content-Type": "application/json",
            "Accept": "application/vnd.inveniordm.v1+json",
          },
        }
      )
      .then(() => {
        window.location = `/uploads/${result.id}`;
      })
      .catch((error) => {
        console.error(error.response.data);
      });
  };

  const filters = currentQueryState && Object.fromEntries(currentQueryState.filters);
  const isPublished = result.is_published;
  const access = {
    accessStatusId: _get(result, "ui.access_status.id", i18next.t("open")),
    accessStatus: _get(result, "ui.access_status.title_l10n", i18next.t("Open")),
    accessStatusIcon: _get(result, "ui.access_status.icon", i18next.t("unlock")),
  };
  const versions = _get(result, "versions");
  const uiMetadata = {
    descriptionStripped: _get(
      result,
      "ui.description_stripped",
      i18next.t("No description")
    ),
    title: _get(result, "metadata.title", i18next.t("No title")),
    creators: _get(result, "ui.creators.creators", []).slice(0, 3),
    subjects: _get(result, "ui.subjects", []),
    publicationDate: _get(
      result,
      "ui.publication_date_l10n_long",
      i18next.t("No publication date found.")
    ),
    resourceType: _get(
      result,
      "ui.resource_type.title_l10n",
      i18next.t("No resource type")
    ),
    createdDate: result.ui?.created_date_l10n_long,
    version: result.ui?.version ?? "",
    versions: versions,
    isPublished: isPublished,
    viewLink: isPublished ? `/records/${result.id}` : `/records/${result.id}?preview=1`,
    publishingInformation: _get(result, "ui.publishing_information.journal", ""),
    allVersionsVisible: filters?.allversions,
    numOtherVersions: versions.index - 1,
  };


  return (
      <ComputerTabletUploadsItem
        result={result}
        editRecord={editRecord}
        statuses={statuses}
        access={access}
        uiMetadata={uiMetadata}
      />
  );
};

RecordResultsListItemDashboard.propTypes = {
  result: PropTypes.object.isRequired,
};

export { RecordResultsListItemDashboard };