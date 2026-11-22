// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import { Button, Checkbox, Input, Message } from "semantic-ui-react";

import { i18next } from "@translations/invenio_app_rdm/i18next";
import apiClient from "@js/kcworks/utils/apiClient";

import { EDITING_STEP } from "./common";
import { GUEST_COLLECTION_TABS } from "./GuestCollectionUI";

const GuestCollectionCreator = ({
  bucketName,
  containerTerm,
  fetchMatchedCollections,
  isPublic,
  selectedFolder,
  selectedMappedCollection,
  setActiveTab,
  setBucketName,
  setEditingStep,
  setIsPublic,
  setSelectedFolder,
  updateGlobusState,
}) => {
  const [isCreatingGC, setIsCreatingGC] = useState(false);
  const [gcCreationError, setGcCreationError] = useState(null);

  const handleCreateGuestCollection = async () => {
    if (!bucketName || !selectedFolder || !selectedMappedCollection) return;
    setIsCreatingGC(true);
    setGcCreationError(null);

    try {
      const response = await apiClient.post("/api/globus/guest-collections/create", {
        mapped_collection_id: selectedMappedCollection,
        display_name: bucketName,
        collection_base_path: selectedFolder,
        public: isPublic,
      });

      updateGlobusState({
        guest_collection_id: response.data.guest_collection_id,
      });

      setBucketName("");
      await fetchMatchedCollections(selectedMappedCollection);
    } catch (err) {
      setGcCreationError(err.response?.data?.error || "Failed to create Guest Collection.");
    } finally {
      setIsCreatingGC(false);
    }
  };

  return (
    <div
      style={{
        padding: "15px",
        backgroundColor: "#f8f8f9",
        border: "1px solid #d4d4d5",
        borderRadius: "4px",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
          marginBottom: "15px",
        }}
      >
        <h5 className="ui header" style={{ margin: 0 }}>
          Create a New Guest Collection
        </h5>
        <Button size="mini" basic onClick={() => setSelectedFolder(null)}>
          Cancel
        </Button>
      </div>
      <div style={{ marginBottom: "15px" }}>
        <strong>
          {i18next.t("Target {{container}}:", {
            container: containerTerm,
          })}
        </strong>{" "}
        <code style={{ color: "#2185d0" }}>{selectedFolder}</code>
      </div>
      <div className="field">
        <label htmlFor="newGuestCollectionName">Guest Collection Name</label>
        <Input
          id="newGuestCollectionName"
          placeholder="e.g., My Research Data"
          value={bucketName}
          onChange={(e) => setBucketName(e.target.value)}
          fluid
        />
      </div>
      <div className="field" style={{ marginTop: "15px", marginBottom: "15px" }}>
        <Checkbox
          toggle
          label={isPublic ? "Public Collection" : "Private Collection"}
          checked={isPublic}
          onChange={(e, { checked }) => setIsPublic(checked)}
        />
        <p
          style={{
            fontSize: "0.85em",
            color: "gray",
            marginTop: "5px",
          }}
        >
          {isPublic
            ? "Anyone with the link can access this collection."
            : "Only you and users you grant access to can view this."}
        </p>
      </div>
      {gcCreationError && <Message negative>{gcCreationError}</Message>}
      <Button
        primary
        disabled={!bucketName || isCreatingGC}
        loading={isCreatingGC}
        onClick={async () => {
          await handleCreateGuestCollection();
          setActiveTab(GUEST_COLLECTION_TABS.EXISTING_GUEST);
          setEditingStep(EDITING_STEP.NONE);
        }}
      >
        Create & Link Collection
      </Button>
    </div>
  );
};

export { GuestCollectionCreator };
