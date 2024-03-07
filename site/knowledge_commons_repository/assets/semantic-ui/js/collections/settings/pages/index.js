import { CommunityPagesForm } from "./CommunityPagesForm";
import ReactDOM from "react-dom";
import React from "react";

const domContainer = document.getElementById("community-settings-pages");
const formConfig = JSON.parse(domContainer.dataset.formConfig);
const community = JSON.parse(domContainer.dataset.community);

ReactDOM.render(
  <CommunityPagesForm formConfig={formConfig} community={community} />,
  domContainer
);
