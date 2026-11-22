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
import { Grid, Form, Button } from "semantic-ui-react";

import { i18next } from "@translations/invenio_app_rdm/i18next";

import { EDITING_STEP, globusCollectionOverviewUrl } from "./common";
import { GlobusExternalLinkButton } from "./GlobusExternalLinkButton";

const SelectedGuestCollection = ({
  globusAppDomain,
  matchedCollections,
  selectedGuestCollection,
  setEditingStep,
}) => {
  return (
    <Grid.Row className="p-0 mb-5">
      <Grid.Column width="4">
        <Form.Field className="mb-0 pt-5 pb-5">
          <label className="invenio-field-label mb-0">Guest Collection</label>
        </Form.Field>
      </Grid.Column>
      <Grid.Column width="8">
        <Form.Field className="mb-0 pt-5 pb-5">
          {matchedCollections?.find((mc) => mc.id === selectedGuestCollection)?.display_name ||
            selectedGuestCollection}
          <GlobusExternalLinkButton
            href={globusCollectionOverviewUrl(selectedGuestCollection, globusAppDomain)}
          />
        </Form.Field>
      </Grid.Column>
      <Grid.Column width="4">
        <Form.Field className="right floated mb-0">
          <Button
            type="button"
            size="mini"
            negative
            icon="close"
            onClick={() => setEditingStep(EDITING_STEP.GUEST)}
            aria-label={i18next.t("Change")}
          />
        </Form.Field>
      </Grid.Column>
    </Grid.Row>
  );
};

export { SelectedGuestCollection };
