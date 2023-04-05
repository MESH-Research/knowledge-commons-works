/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import { BucketAggregation, buildUID } from "react-searchkit";
import Overridable from "react-overridable";

export const SearchAppFacets = ({ aggs, appName }) => {
  const buildOverridableUID = (element) => buildUID(element, "", appName);
  return (
    <Overridable
      id={buildOverridableUID("SearchApp.facets", "", appName)}
      aggs={aggs}
      appName={appName}
    >
      <>
        {aggs.map((agg) => (
          <BucketAggregation key={agg.title} title={agg.title} agg={agg.agg} />
        ))}
      </>
    </Overridable>
  );
};
