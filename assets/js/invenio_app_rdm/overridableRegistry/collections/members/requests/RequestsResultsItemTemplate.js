import PropTypes from "prop-types";
import React from "react";
import { withState } from "react-searchkit";
import { parametrize } from "react-overridable";
import {
  ComputerTabletRequestItem,
} from "../../../requests/ComputerTabletRequestItem";
import { MobileRequestItem } from "../../../requests/MobileRequestItem";

const RequestsResultsItemTemplateCommunity = ({ result, community }) => {
  const ComputerTabletRequestsItemWithState = withState(
    ComputerTabletRequestItem
  );
  const MobileRequestsItemWithState = withState(MobileRequestItem);
  const detailsURL = `/collections/${community.slug}/requests/${result.id}`;

  return (
    <>
      <ComputerTabletRequestsItemWithState
        result={result}
        detailsURL={detailsURL}
      />
      <MobileRequestsItemWithState result={result} detailsURL={detailsURL} />
    </>
  );
};

RequestsResultsItemTemplateCommunity.propTypes = {
  result: PropTypes.object.isRequired,
  community: PropTypes.object.isRequired,
};

// FIXME: This is a workaround to access the community
// object without overriding the root invenio_communities/requests/index.js
// file where the container is defined. We just override this componennt
const domContainer = document.getElementById("communities-request-search-root");
const community = domContainer ? JSON.parse(domContainer.dataset.community) : undefined;

const RequestsResultsItemTemplateWithCommunity = parametrize(
  RequestsResultsItemTemplateCommunity,
  {
    community: community,
  }
);

export {
  RequestsResultsItemTemplateCommunity,
  RequestsResultsItemTemplateWithCommunity,
};
