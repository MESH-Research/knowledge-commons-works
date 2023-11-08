// This file is part of InvenioRDM
// Copyright (C) 2020-2021 CERN.
// Copyright (C) 2020-2021 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio RDM Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import axios from "axios";
import _get from "lodash/get";
import React, { useEffect, useState } from "react";
import {
  Button,
  Dropdown,
  Grid,
  Icon,
  Label,
  Message,
  Placeholder,
  List,
  Divider,
} from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import PropTypes from "prop-types";

const deserializeRecord = (record) => ({
  id: record.id,
  parent_id: record.parent.id,
  publication_date: record.ui.publication_date_l10n_medium,
  version: record.ui.version,
  links: record.links,
  pids: record.pids,
});

const NUMBER_OF_VERSIONS = 5;

const RecordVersionItem = ({ item, activeVersion }) => {
  const doi = _get(item.pids, "doi.identifier", "");
  return (
    <List.Item
      key={item.id}
      {...(activeVersion && { className: "version active" })}
    >
      <List.Content floated="left">
        {activeVersion ? (
          <span>
            {i18next.t("Version {{version}}", { version: item.version })}
          </span>
        ) : (
          <a href={`/records/${item.id}`}>
            {i18next.t("Version {{version}}", { version: item.version })}
          </a>
        )}

        {doi && (
          <a
            href={`https://doi.org/${doi}`}
            className={
              "doi" + (activeVersion ? " text-muted-darken" : " text-muted")
            }
          >
            {doi}
          </a>
        )}
      </List.Content>

      <List.Content floated="right">
        <small className={activeVersion ? "text-muted-darken" : "text-muted"}>
          {item.publication_date}
        </small>
      </List.Content>
    </List.Item>
  );
};

RecordVersionItem.propTypes = {
  item: PropTypes.object.isRequired,
  activeVersion: PropTypes.bool.isRequired,
};

const PreviewMessage = () => {
  return (
    <Grid className="container">
      <Grid.Row>
        <Grid.Column>
          <Message info>
            <Message.Header>
              <Icon name="eye" />
              {i18next.t("Preview")}
            </Message.Header>
            <p>{i18next.t("Only published versions are displayed.")}</p>
          </Message>
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

const VersionsContentDropdown = ({
  currentRecordInResults,
  isPreview,
  loading,
  recid,
  recordDeserialized,
  recordPublicationDate,
  recordVersions,
}) => {
  const [activeVersion, setActiveVersion] = useState(recid);
  console.log("****VersionsContentDropdown recordVersions", recordVersions);
  console.log(
    "****VersionsContentDropdown currentRecordInResults",
    currentRecordInResults
  );
  console.log(
    "****VersionsContentDropdown recordDeserialized",
    recordDeserialized
  );
  console.log("****VersionsContentDropdown isPreview", isPreview);

  let versionOptions = recordVersions?.hits?.map((item) => {
    let opt = {
      key: item.id,
      text: i18next.t(`Version ${item.version}`),
      href: `/records/${item.id}`,
      pubdate: item.publication_date,
    };
    const doi = _get(item.pids, "doi.identifier", "");
    if (doi) {
      opt.description = `https://doi.org/${doi}`;
    }
    return opt;
  });
  if (!versionOptions) {
    versionOptions = [];
  }
  if (isPreview && !currentRecordInResults) {
    versionOptions.push({
      key: recid,
      text: i18next.t(`Preview version`),
      href: `/records/${recid}`,
      pubdate: recordPublicationDate,
    });
  }

  return (
    <div
      className={`ui clearing segment rdm-sidebar pr-0 pt-0 pb-0 ${
        isPreview && "preview"
      }`}
    >
      <>
        <h3
          className={`version-label ${
            isPreview ? "preview" : ""
          } ui header tiny`}
        >
          {isPreview ? (
            <>
              {i18next.t("Preview")}
              <Icon name="eye" />
            </>
          ) : (
            <>
              {i18next.t("Version ")}
              {loading ? (
                <Icon loading name="spinner" size="tiny" />
              ) : (
                recordDeserialized.version
              )}
            </>
          )}
        </h3>
        {recordVersions.total > 1 && (
          <Dropdown
            button
            basic
            text="other versions"
            direction="left"
            className="right floated"
          >
            <Dropdown.Menu>
              {versionOptions.map((opt) => (
                <Dropdown.Item as="a" key={opt.key} href={opt.href}>
                  <span className="text">{opt.text}</span>
                  <small className="pubdate description">{opt.pubdate}</small>
                  <small className="doi description">{opt.description}</small>
                </Dropdown.Item>
              ))}
              <Dropdown.Divider />
              <Dropdown.Item
                href={`/search?q=parent.id:${recordDeserialized.parent_id}&sort=version&f=allversions:true`}
                text={i18next.t(`View all ${recordVersions.total} versions`)}
              />
            </Dropdown.Menu>
          </Dropdown>
        )}
      </>
    </div>
  );
};

const VersionsContentList = ({
  currentRecordInResults,
  isPreview,
  loading,
  recid,
  recordDeserialized,
  recordVersions,
}) => {
  return (
    <List divided>
      <>
        {loading ? (
          <Placeholder fluid>
            <Placeholder.Header>
              <Placeholder.Line />
              <Placeholder.Line />
              <Placeholder.Line />
              <Placeholder.Line />
            </Placeholder.Header>
          </Placeholder>
        ) : (
          <>
            {isPreview ? <PreviewMessage /> : null}
            {recordVersions.hits.map((item) => (
              <RecordVersionItem
                key={item.id}
                item={item}
                activeVersion={item.id === recid}
              />
            ))}
            {!currentRecordInResults && (
              <>
                <Divider horizontal>...</Divider>
                <RecordVersionItem item={recordDeserialized} activeVersion />
              </>
            )}
            {recordVersions.total > 1 && (
              <Grid className="mt-0">
                <Grid.Row centered>
                  <a
                    href={`/search?q=parent.id:${recordDeserialized.parent_id}&sort=version&f=allversions:true`}
                    className="font-small"
                  >
                    {i18next.t(`View all {{count}} versions`, {
                      count: recordVersions.total,
                    })}
                  </a>
                </Grid.Row>
              </Grid>
            )}
          </>
        )}
      </>
    </List>
  );
};

const RecordVersionsList = ({ record, isPreview, widgetStyle = "list" }) => {
  const recordDeserialized = deserializeRecord(record);
  const recid = recordDeserialized.id;
  const [loading, setLoading] = useState(true);
  const [currentRecordInResults, setCurrentRecordInResults] = useState(false);
  const [recordVersions, setRecordVersions] = useState({});

  useEffect(() => {
    async function fetchVersions() {
      const result = await axios(
        `${recordDeserialized.links.versions}?size=${NUMBER_OF_VERSIONS}&sort=version&allversions=true`,
        {
          headers: {
            Accept: "application/vnd.inveniordm.v1+json",
          },
          withCredentials: true,
        }
      );
      let { hits, total } = result.data.hits;
      hits = hits.map(deserializeRecord);
      setCurrentRecordInResults(hits.some((record) => record.id === recid));
      setRecordVersions({ hits, total });
      setLoading(false);
    }
    fetchVersions();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  return widgetStyle === "list" ? (
    <VersionsContentList
      isPreview={isPreview}
      loading={loading}
      recordDeserialized={recordDeserialized}
      recid={recid}
      recordVersions={recordVersions}
      currentRecordInResults={currentRecordInResults}
    />
  ) : (
    <VersionsContentDropdown
      isPreview={isPreview}
      loading={loading}
      recordDeserialized={recordDeserialized}
      recid={recid}
      recordPublicationDate={recordDeserialized.publication_date}
      recordVersions={recordVersions}
      currentRecordInResults={currentRecordInResults}
    />
  );
};

RecordVersionsList.propTypes = {
  record: PropTypes.object.isRequired,
  isPreview: PropTypes.bool.isRequired,
};

export { RecordVersionsList };
