/*
 * This file is part of Invenio.
 * Copyright (C) 2020 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import { overrideStore } from "react-overridable";
import _isString from "lodash/isString";

export async function importTemplate(templateName) {
  const module = await import(
    /* webpackMode: "eager" */
    `@templates/${templateName}`
  );
  return module.default;
}

export async function registerComponent(prefix, componentId, defaultComponent) {
  let component = null;
  try {
    // First look into the prefixed path for the component
    component = await importTemplate(`${prefix}/${componentId}.jsx`);
  } catch (error) {
    if (defaultComponent) {
      // If a string was specified, try to import it
      if (_isString(defaultComponent)) {
        try {
          component = await importTemplate(`${defaultComponent}.jsx`);
        } catch (error) {
          console.error(
            `Failed to import default component ${defaultComponent}.jsx`
          );
        }
      } else {
        component = defaultComponent;
      }
    }
  } finally {
    if (component) {
      overrideStore.add(componentId, component);
      return component;
    }
  }
}

export function loadComponents(prefix, defaultComponents) {
  const tplPromises = [];
  for (const [componentId, component] of Object.entries(defaultComponents)) {
    tplPromises.push(registerComponent(prefix, componentId, component));
  }
  return Promise.all(tplPromises);
}
