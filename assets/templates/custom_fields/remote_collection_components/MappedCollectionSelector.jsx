// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React, { useEffect } from "react";
import { Button, Form, Grid, Message } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

import { EDITING_STEP, globusCollectionOverviewUrl } from "./common";
import { GlobusExternalLinkButton } from "./GlobusExternalLinkButton";

const SelectedMappedCollection = ({
  endpoints,
  filteredMappedCollections,
  globusAppDomain,
  selectedMappedCollection,
  setEditingStep,
}) => {
  const selected = endpoints.find((ep) => ep.id === selectedMappedCollection);
  const domain = selected?.domain || globusAppDomain;
  console.log("filteredMappedCollections", filteredMappedCollections);
  return filteredMappedCollections.length > 1 ? (
    <Grid.Row className="p-0 mb-5">
      <Grid.Column width="4">
        <Form.Field className="mb-0 pt-5 pb-5">
          <label className="invenio-field-label mb-0">{i18next.t("Mapped collection")}</label>
        </Form.Field>
      </Grid.Column>
      <Grid.Column width="8">
        <Form.Field className="mb-0 pt-5 pb-5">
          {selected?.display_name || selectedMappedCollection}
          <GlobusExternalLinkButton
            href={globusCollectionOverviewUrl(selectedMappedCollection, domain)}
          />
        </Form.Field>
      </Grid.Column>
      <Grid.Column width="4">
        <Form.Field className="right floated mb-0">
          <Button
            size="mini"
            type="button"
            negative
            icon="close"
            onClick={() => setEditingStep(EDITING_STEP.MAPPED)}
            aria-label={i18next.t("Change")}
          />
        </Form.Field>
      </Grid.Column>
    </Grid.Row>
  ) : null;
};

const MappedCollectionSelector = ({
  editingStep,
  endpoints,
  globusAppDomain,
  selectedHostEndpoint,
  selectedMappedCollection,
  setSelectedFolder,
  setEditingStep,
  updateGlobusState,
}) => {
  const filteredMappedCollections = endpoints.filter((ep) => {
    const isGCP = ep.entity_type === "GCP_mapped_collection" || !ep.non_functional_endpoint_id;
    const hostId = isGCP ? ep.id : ep.non_functional_endpoint_id;
    return hostId === selectedHostEndpoint;
  });

  const updateSelectedCollection = (collection) => {
    updateGlobusState({
      mapped_collection_id: collection.id,
      guest_collection_id: "",
    });
    setSelectedFolder(null);
    setEditingStep(EDITING_STEP.GUEST);
  };

  useEffect(() => {
    if (!selectedMappedCollection && filteredMappedCollections?.length === 1) {
      const onlyMappedCollection = filteredMappedCollections[0];
      updateSelectedCollection(onlyMappedCollection);
    }
  }, [filteredMappedCollections]);

  return !selectedMappedCollection || editingStep === EDITING_STEP.MAPPED ? (
    <Form as="div" className="ml-10">
      <Form.Field className="ui header">{i18next.t("Select Mapped Collection")}</Form.Field>
      {filteredMappedCollections.length > 0 ? (
        <Button.Group vertical>
          {filteredMappedCollections.map((ep) => (
            <Button
              key={ep.id}
              id={`radio-mapped-${ep.id}`}
              className="ml-0 text-align-left"
              basic
              name="mapped-collection-selector"
              value={ep.id}
              onClick={() => updateSelectedCollection(ep)}
            >
              {ep.display_name || ep.id}
            </Button>
          ))}
        </Button.Group>
      ) : (
        <Message info>{i18next.t("No collections found on your account.")}</Message>
      )}
    </Form>
  ) : (
    <SelectedMappedCollection
      {...{
        endpoints,
        filteredMappedCollections,
        globusAppDomain,
        selectedMappedCollection,
        setEditingStep,
      }}
    />
  );
};

export { MappedCollectionSelector };
