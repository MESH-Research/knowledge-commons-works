import React from "react";
import ReactDOM from "react-dom";
import { CurationPolicyForm } from "./CurationPolicyForm";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const formConfig = JSON.parse(domContainer.dataset.formConfig);

ReactDOM.render(
  <CurationPolicyForm community={community} formConfig={formConfig} />,
  domContainer
);
