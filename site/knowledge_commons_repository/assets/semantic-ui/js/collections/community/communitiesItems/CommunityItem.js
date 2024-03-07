import React from "react";
import PropTypes from "prop-types";

import { CommunityItemComputer } from "./CommunityItemComputer";
import { CommunityItemMobile } from "./CommunityItemMobile";

export function CommunityItem({ result }) {
  return (
    <>
      <CommunityItemComputer result={result} />
      <CommunityItemMobile result={result} />
    </>
  );
}

CommunityItem.propTypes = {
  result: PropTypes.object.isRequired,
};
