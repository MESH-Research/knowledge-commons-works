/*
* This file is part of Knowledge Commons Works.
*   Copyright (C) 2024 Mesh Research.
*
* Knowledge Commons Works is based on InvenioRDM, and
* this file is based on code from InvenioRDM. InvenioRDM is
*   Copyright (C) 2020-2024 CERN.
*   Copyright (C) 2020-2024 Northwestern University.
*   Copyright (C) 2020-2024 T U Wien.
*   Copyright (C) 2020-2024 New York University.
*
* InvenioRDM and Knowledge Commons Works are both free software;
* you can redistribute and/or modify them under the terms of the
* MIT License; see LICENSE file for more details.
*/

import PropTypes from "prop-types";
import React from "react";
import { withState } from "react-searchkit";
import {
  MobileRequestItem,
} from "../requests/MobileRequestItem";
import { ComputerTabletRequestItem } from "../requests/ComputerTabletRequestItem";

function RequestsResultsItemTemplateDashboard({ result }) {
  const ComputerTabletRequestsItemWithState = withState(ComputerTabletRequestItem);
  const MobileRequestsItemWithState = withState(MobileRequestItem);
  let detailsURL;
  if (result.type === "user-access-request") {
    detailsURL = `/access/requests/${result.id}`;
  } else {
    detailsURL = `/me/requests/${result.id}`;
  }
  return (
    <>
      <ComputerTabletRequestsItemWithState result={result} detailsURL={detailsURL} />
      <MobileRequestsItemWithState result={result} detailsURL={detailsURL} />
    </>
  );
}

RequestsResultsItemTemplateDashboard.propTypes = {
  result: PropTypes.object.isRequired,
};

export { RequestsResultsItemTemplateDashboard };
