// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React from "react";
import { Button, Form, Grid, Message } from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

import { EDITING_STEP, globusCollectionOverviewUrl, globusConsoleEndpointUrl } from "./common";
import { GlobusExternalLinkButton } from "./GlobusExternalLinkButton";

const ServerSelector = ({
  editingStep,
  serverEndpoints,
  selectedHostEndpoint,
  updateGlobusState,
  setEditingStep,
  setSelectedFolder,
}) => {
  const handleChange = (serverId) => {
    updateGlobusState({
      host_endpoint_id: serverId,
      mapped_collection_id: "",
      guest_collection_id: "",
    });
    setEditingStep(EDITING_STEP.MAPPED);
    setSelectedFolder(null);
  };
  return !selectedHostEndpoint || editingStep === EDITING_STEP.HOST ? (
    <Form as="div" className="ml-10">
      <Form.Field className="ui header">{i18next.t("Select Globus Server")}</Form.Field>
      {serverEndpoints.length > 0 ? (
        <Button.Group vertical>
          {serverEndpoints.map((host) => (
            <Button
              key={host.id}
              id={`radio-host-${host.id}`}
              className="ml-0 text-align-left"
              basic
              name={`server-selector`}
              value={host.id}
              onClick={() => handleChange(host.id)}
            >
              {host.display_name}
            </Button>
          ))}
        </Button.Group>
      ) : (
        <Message info>
          {i18next.t("We couldn't find a server for which you have permissions.")}
        </Message>
      )}
    </Form>
  ) : (
    <SelectedServer
      {...{
        hostEndpoints: serverEndpoints,
        selectedHostEndpoint,
        setEditingStep,
        updateGlobusState,
      }}
    />
  );
};

const SelectedServer = ({
  hostEndpoints,
  selectedHostEndpoint,
  setEditingStep,
  updateGlobusState,
}) => {
  const clearGlobusState = () => {
    updateGlobusState({
      host_endpoint_id: "",
      mapped_collection_id: "",
      guest_collection_id: "",
    });
  };
  const selected = hostEndpoints.find((h) => h.id === selectedHostEndpoint);
  const externalHref = selected?.isGCP
    ? globusCollectionOverviewUrl(selectedHostEndpoint, selected?.domain)
    : globusConsoleEndpointUrl(selectedHostEndpoint, selected?.domain);
  return (
    <Grid.Row className="p-0 mb-5">
      <Grid.Column width="4">
        <Form.Field className="mb-0 pt-5 pb-5">
          <label className="invenio-field-label mb-0">{i18next.t("Server")}</label>
        </Form.Field>
      </Grid.Column>
      <Grid.Column width="8">
        <Form.Field className="mb-0 pt-5 pb-5">
          {selected?.display_name}
          <GlobusExternalLinkButton href={externalHref} />
        </Form.Field>
      </Grid.Column>
      {hostEndpoints?.length > 1 ? (
        <Grid.Column width="4">
          <Form.Field className="right floated mb-0">
            <Button
              size="mini"
              type="button"
              icon="close"
              negative
              onClick={() => {
                setEditingStep(EDITING_STEP.HOST);
                clearGlobusState();
              }}
              aria-label={i18next.t("Change")}
            />
          </Form.Field>
        </Grid.Column>
      ) : null}
    </Grid.Row>
  );
};

export { ServerSelector };
