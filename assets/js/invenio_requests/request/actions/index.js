// This file is part of InvenioRequests

import { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
import PropTypes from "prop-types";
import ReactDOM from "react-dom";
import React from "react";
import Overridable from "react-overridable";

const element = document.getElementById("request-actions");

const RequestActionsPortalCmp = ({ request, actionSuccessCallback }) => {
  return ReactDOM.createPortal(
    <RequestActionController
      request={request}
      actionSuccessCallback={actionSuccessCallback}
    />,
    element
  );
};

RequestActionsPortalCmp.propTypes = {
  request: PropTypes.object.isRequired,
  actionSuccessCallback: PropTypes.func.isRequired,
};

export default Overridable.component(
  "InvenioRequests.RequestActionsPortal",
  RequestActionsPortalCmp
);

export { RequestActionController } from "@js/invenio_requests/request/actions/RequestActionController";
