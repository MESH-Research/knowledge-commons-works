// This file is part of InvenioRDM
// Copyright (C) 2022 CERN.
//
// Invenio Search Ui is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_search_ui/i18next";
import React, { useState } from "react";
import {
  Accordion,
  Button,
  Card,
  Checkbox,
  Label,
  List,
} from "semantic-ui-react";
import Overridable from "react-overridable";
import PropTypes from "prop-types";
import { BucketAggregation, Toggle, buildUID } from "react-searchkit";

export const ContribSearchAppFacets = ({ aggs, toogle, help, appName }) => {
  return (
    <aside aria-label={i18next.t("filters")} id="search-filters">
      {toogle && (
        <Toggle
          title={i18next.t("Versions")}
          label={i18next.t("View all versions")}
          filterValue={["allversions", "true"]}
        />
      )}

      {aggs.map((agg) => {
        return (
          <div className="facet-container" key={agg.title}>
            <BucketAggregation title={agg.title} agg={agg} />
          </div>
        );
      })}
      {help && (
        <Card className="borderless facet mt-0">
          <Card.Content>
            <Card.Header as="h2">{i18next.t("Help")}</Card.Header>
            <ContribSearchHelpLinks appName={appName}/>
          </Card.Content>
        </Card>
      )}
    </aside>
  );
};

ContribSearchAppFacets.propTypes = {
  aggs: PropTypes.array.isRequired,
  toggle: PropTypes.bool,
  help: PropTypes.bool,
  appName: PropTypes.string,
};

ContribSearchAppFacets.defaultProps = {
  toggle: false,
  help: true,
  appName: "",
};

export const ContribSearchHelpLinks = (props) => {
  const { appName } = props;
  return (
    <Overridable id={buildUID("SearchHelpLinks", "", appName)}>
      <List>
        <List.Item>
          <a href="/help/search">{i18next.t("Search guide")}</a>
        </List.Item>
      </List>
    </Overridable>
  );
};

ContribSearchHelpLinks.propTypes = {
  appName: PropTypes.string,
};

ContribSearchHelpLinks.defaultProps = {
  appName: "",
};

export const ContribParentFacetValue = ({
  bucket,
  keyField,
  isSelected,
  childAggCmps,
  onFilterClicked,
}) => {
  const [isActive, setIsActive] = useState(false);

  return (
    <Accordion>
      <Accordion.Title
        onClick={() => { }}
        key={`panel-${bucket.label}`}
        active={isActive}
        className="facet-wrapper parent"
      >
        <List.Content className="facet-wrapper">
          <Button
            icon="angle right"
            className="transparent"
            onClick={() => setIsActive(!isActive)}
            aria-label={
              i18next.t("Show all sub facets of ") + bucket.label || keyField
            }
          />
          <Checkbox
            label={bucket.label || keyField}
            id={`${keyField}-facet-checkbox`}
            aria-describedby={`${keyField}-count`}
            value={keyField}
            checked={isSelected}
            onClick={() => onFilterClicked(keyField)}
          />
          <Label circular id={`${keyField}-count`} className="facet-count">
            {bucket.doc_count}
          </Label>
        </List.Content>
      </Accordion.Title>
      <Accordion.Content active={isActive}>{childAggCmps}</Accordion.Content>
    </Accordion>
  );
};

ContribParentFacetValue.propTypes = {
  bucket: PropTypes.object.isRequired,
  keyField: PropTypes.string.isRequired,
  isSelected: PropTypes.bool.isRequired,
  childAggCmps: PropTypes.node.isRequired,
  onFilterClicked: PropTypes.func.isRequired,
};

export const ContribFacetValue = ({
  bucket,
  keyField,
  isSelected,
  onFilterClicked,
}) => {
  return (
    <List.Content className="facet-wrapper">
      <Checkbox
        onClick={() => onFilterClicked(keyField)}
        label={bucket.label || keyField}
        id={`${keyField}-facet-checkbox`}
        aria-describedby={`${keyField}-count`}
        value={keyField}
        checked={isSelected}
      />
      <Label circular id={`${keyField}-count`} className="facet-count">
        {bucket.doc_count}
      </Label>
    </List.Content>
  );
};

ContribFacetValue.propTypes = {
  bucket: PropTypes.object.isRequired,
  keyField: PropTypes.string.isRequired,
  isSelected: PropTypes.bool.isRequired,
  onFilterClicked: PropTypes.func.isRequired,
};

export const ContribBucketAggregationValuesElement = ({
  bucket,
  isSelected,
  onFilterClicked,
  childAggCmps,
}) => {
  const hasChildren = childAggCmps && childAggCmps.props.buckets.length > 0;
  const keyField = bucket.key_as_string ? bucket.key_as_string : bucket.key;
  return (
    <List.Item key={bucket.key}>
      {hasChildren ? (
        <ContribParentFacetValue
          bucket={bucket}
          keyField={keyField}
          isSelected={isSelected}
          childAggCmps={childAggCmps}
          onFilterClicked={onFilterClicked}
        />
      ) : (
        <ContribFacetValue
          bucket={bucket}
          keyField={keyField}
          isSelected={isSelected}
          onFilterClicked={onFilterClicked}
        />
      )}
    </List.Item>
  );
};

ContribBucketAggregationValuesElement.propTypes = {
  bucket: PropTypes.object.isRequired,
  childAggCmps: PropTypes.node,
  isSelected: PropTypes.bool.isRequired,
  onFilterClicked: PropTypes.func.isRequired,
};

ContribBucketAggregationValuesElement.defaultProps = {
  childAggCmps: null,
};

export const ContribBucketAggregationElement = ({
  agg,
  title,
  containerCmp,
  updateQueryFilters,
}) => {
  const clearFacets = () => {
    if (containerCmp.props.selectedFilters.length) {
      updateQueryFilters([agg.aggName, ""], containerCmp.props.selectedFilters);
    }
  };

  const hasSelections = () => {
    return !!containerCmp.props.selectedFilters.length;
  };

  return (
    <Card className="borderless facet">
      <Card.Content>
        <Card.Header as="h2">
          {title}

          {hasSelections() && (
            <Button
              basic
              icon
              size="mini"
              floated="right"
              onClick={clearFacets}
              aria-label={i18next.t("Clear selection")}
              title={i18next.t("Clear selection")}
            >
              {i18next.t("Clear")}
            </Button>
          )}
        </Card.Header>
        {containerCmp}
      </Card.Content>
    </Card>
  );
};

ContribBucketAggregationElement.propTypes = {
  agg: PropTypes.object.isRequired,
  title: PropTypes.string.isRequired,
  containerCmp: PropTypes.node,
  updateQueryFilters: PropTypes.func.isRequired,
};

ContribBucketAggregationElement.defaultProps = {
  containerCmp: null,
};
