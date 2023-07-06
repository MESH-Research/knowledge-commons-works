// This file is part of InvenioVocabularies
// Copyright (C) 2021-2023 CERN.
// Copyright (C) 2021 Northwestern University.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";

import { Dropdown } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { i18next } from "@translations/invenio_rdm_records/i18next";

export const FunderDropdown = withState(
  ({ currentResultsState: awardsList, updateQueryState, currentQueryState }) => {
    const [fundersFromFacets] = useFundersFromFacets(awardsList);

    /**
     * Trigger on funder selection.
     * Updated the query state to filter by the selected funder.
     *
     * @param {*} event
     * @param {*} data
     */
    function onFunderSelect(event, data) {
      let newFilter = [];

      if (data && data.value !== "") {
        newFilter = ["funders", data.value];
      }
      updateQueryState({ ...currentQueryState, filters: newFilter, page: 1 });
    }

    /**
     * Custom hook, triggered when the awards list changes.
     * It retrieves funders from new award's facets.
     *
     * @param {object} awards
     *
     * @returns {object[]} an array of objects, each representing a facetted funder.
     */
    function useFundersFromFacets(awards) {
      const [result, setResult] = React.useState([]);
      React.useEffect(() => {
        /**
         * Retrieves funders from awards facets and sets the result in state 'result'.
         */
        function getFundersFromAwardsFacet() {
          if (awards.loading) {
            setResult([]);
            return;
          }

          const funders = awards.data.aggregations?.funders?.buckets.map((agg) => {
            return {
              key: agg.key,
              value: agg.key,
              text: agg.label,
            };
          });
          setResult(funders);
        }

        getFundersFromAwardsFacet();
      }, [awards]);

      return [result];
    }

    return (
      <Dropdown
        placeholder={i18next.t("Funder")}
        search
        selection
        clearable
        scrolling
        multiple={false}
        options={fundersFromFacets || []}
        allowAdditions={false}
        onChange={onFunderSelect}
        fluid
        selectOnBlur={false}
        selectOnNavigation={false}
      />
    );
  }
);
