// This file is part of InvenioVocabularies
// Copyright (C) 2021-2023 CERN.
// Copyright (C) 2021 Northwestern University.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React from "react";
import PropTypes from "prop-types";
import _get from "lodash/get";
import { Item, Header, Radio, Label, Icon } from "semantic-ui-react";
import { withState } from "react-searchkit";
import { FastField } from "formik";

export const AwardResults = withState(
  ({
    currentResultsState: results,
    deserializeAward,
    deserializeFunder,
    computeFundingContents,
  }) => {
    return (
      <FastField name="selectedFunding">
        {({ form: { values, setFieldValue } }) => {
          return (
            <Item.Group>
              {results.data.hits.map((award) => {
                let funder = award?.funder;
                const deserializedAward = deserializeAward(award);
                const deserializedFunder = deserializeFunder(funder);
                const funding = {
                  award: deserializedAward,
                  funder: deserializedFunder,
                };
                let { headerContent, descriptionContent, awardOrFunder } =
                  computeFundingContents(funding);

                return (
                  <Item
                    key={deserializedAward.id}
                    onClick={() => setFieldValue("selectedFunding", funding)}
                    className="license-item"
                  >
                    <Radio
                      checked={
                        _get(values, "selectedFunding.award.id") === funding.award.id
                      }
                      onChange={() => setFieldValue("selectedFunding", funding)}
                    />
                    <Item.Content className="license-item-content">
                      <Header size="small">
                        {headerContent}
                        {awardOrFunder === "award"
                          ? award.number && (
                              <Label basic size="mini">
                                {award.number}
                              </Label>
                            )
                          : ""}
                        {awardOrFunder === "award"
                          ? award.url && (
                              <a
                                href={`${award.url}`}
                                target="_blank"
                                rel="noopener noreferrer"
                              >
                                <Icon
                                  link
                                  name="external alternate"
                                  className="spaced-left"
                                />
                              </a>
                            )
                          : ""}
                      </Header>
                      <Item.Description className="license-item-description">
                        {descriptionContent}
                      </Item.Description>
                    </Item.Content>
                  </Item>
                );
              })}
            </Item.Group>
          );
        }}
      </FastField>
    );
  }
);

AwardResults.propTypes = {
  deserializeAward: PropTypes.func.isRequired,
  deserializeFunder: PropTypes.func.isRequired,
  computeFundingContents: PropTypes.func.isRequired,
};
