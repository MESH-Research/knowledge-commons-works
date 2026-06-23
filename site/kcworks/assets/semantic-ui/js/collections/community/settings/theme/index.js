import React from "react";
import ReactDOM from "react-dom";
import CommunityThemeForm from "./CommunityThemeForm";

const domContainer = document.getElementById("app");
const community = JSON.parse(domContainer.dataset.community);
const defaultTheme = JSON.parse(domContainer.dataset.defaultTheme);

ReactDOM.render(
  <CommunityThemeForm community={community} defaultTheme={defaultTheme} />,
  domContainer
);
