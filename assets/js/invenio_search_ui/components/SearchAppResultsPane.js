/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import { Results } from "./Results";
import React from "react";
import {
  EmptyResults,
  Error,
  ResultsLoader,
  withState,
  buildUID,
} from "react-searchkit";
import Overridable from "react-overridable";

const OnResults = withState(Results);

export const SearchAppResultsPane = ({ layoutOptions, appName }) => {
  const buildOverridableUID = (element) => buildUID(element, "", appName);
  return (
    <Overridable
      id={buildOverridableUID("SearchApp.resultsPane", "", appName)}
      layoutOptions={layoutOptions}
    >
      <ResultsLoader>
        <EmptyResults />
        <Error />
        <OnResults />
      </ResultsLoader>
    </Overridable>
  );
};
