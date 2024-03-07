import CommunityPrivilegesForm from "./CommunityPriviledgesForm";
import ReactDOM from "react-dom";
import React from "react";

const domContainer = document.getElementById("app");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const community = JSON.parse(domContainer.dataset.community);

ReactDOM.render(
  <CommunityPrivilegesForm formConfig={formConfig} community={community} />,
  domContainer
);
