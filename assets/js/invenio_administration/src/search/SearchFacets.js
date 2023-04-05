/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */

import React from "react";
import PropTypes from "prop-types";
import { BucketAggregation } from "react-searchkit";

export const SearchFacets = ({ aggs }) => {
  return (
    <>
      {aggs.map((agg) => {
        return (
          <div className="facet-container" key={agg.title}>
            <BucketAggregation title={agg.title} agg={agg} />
          </div>
        );
      })}
    </>
  );
};

SearchFacets.propTypes = {
  aggs: PropTypes.array.isRequired,
};
