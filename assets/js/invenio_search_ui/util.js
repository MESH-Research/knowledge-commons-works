/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { loadComponents } from "@js/invenio_theme/templates";
import _camelCase from "lodash/camelCase";
import React from "react";
import ReactDOM from "react-dom";
import { SearchApp } from "./components";

/**
 * Initialize React search application.
 * @function
 * @param {object} defaultComponents - default components to load if no overriden have been registered.
 * @param {boolean} autoInit - if true then the application is getting registered to the DOM.
 * @param {string} autoInitDataAttr - data attribute to register application to DOM and retrieve config.
 * @param {object} multi - enable multiple search application support.
 *    If true, the application is namespaced using `config.appId`. That allows
 *    users to override each application's components using `appId` as a prefix.
 * @returns {object} frontend compatible record object
 */
export function createSearchAppInit(
  defaultComponents,
  autoInit = true,
  autoInitDataAttr = "invenio-search-config",
  multi = false,
  ContainerComponent = React.Fragment,
) {

  const initSearchApp = (rootElement) => {
    const { appId, ...config } = JSON.parse(
      rootElement.dataset[_camelCase(autoInitDataAttr)]
    );
    loadComponents(appId, defaultComponents).then((res) => {
      ReactDOM.render(
        <ContainerComponent>
          <SearchApp
            config={config}
            // Use appName to namespace application components when overriding
            {...(multi && { appName: appId })}
          />
        </ContainerComponent>,
        rootElement
      );
    });
  };

  if (autoInit) {
    const searchAppElements = document.querySelectorAll(
      `[data-${autoInitDataAttr}]`
    );
    for (const appRootElement of searchAppElements) {
      initSearchApp(appRootElement);
    }
  } else {
    return initSearchApp;
  }
}
