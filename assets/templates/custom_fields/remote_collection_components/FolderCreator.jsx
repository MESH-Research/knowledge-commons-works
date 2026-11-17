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
import { Button, Input, Message } from "semantic-ui-react";

import { i18next } from "@translations/invenio_app_rdm/i18next";
import apiClient from "@js/kcworks/utils/apiClient";

const FolderCreator = ({
  containerTerm,
  bucketName,
  setBucketName,
  selectedMappedCollection,
  fetchRootFiles,
  setSelectedFolder,
  setActiveTab,
  updateGlobusState,
}) => {
  const [provisionError, setProvisionError] = useState(null);
  const [isProvisioning, setIsProvisioning] = useState(false);

  const handleProvision = async () => {
    if (!bucketName || !selectedMappedCollection) return;
    setIsProvisioning(true);
    setProvisionError(null);

    try {
      const response = await apiClient.post("/api/globus/provision", {
        bucket_name: bucketName,
        mapped_collection_id: selectedMappedCollection,
      });

      // store new UUIDs into Formik JSON
      updateGlobusState({
        bucket_id: response.data.bucket_id,
        guest_collection_id: response.data.guest_collection_id,
        folder_path: response.data.path,
      });

      await fetchRootFiles(selectedMappedCollection);
      setSelectedFolder(response.data.path);
      setActiveTab("existing");
      setBucketName("");
    } catch (err) {
      setProvisionError(
        "Failed to provision bucket. Please try again or contact our support team."
      );
    } finally {
      setIsProvisioning(false);
    }
  };

  return (
    <div className="ui form">
      <div className="field">
        <label htmlFor="bucketNameInput">
          {i18next.t("New {{container}} Name", { container: containerTerm })}
        </label>
        <Input
          id="bucketNameInput"
          placeholder="e.g., my-research-dataset"
          value={bucketName}
          onChange={(e) => setBucketName(e.target.value)}
        />
      </div>
      {provisionError && <Message negative>{provisionError}</Message>}
      <Button
        primary
        loading={isProvisioning}
        disabled={isProvisioning || !bucketName}
        onClick={handleProvision}
      >
        {i18next.t("Provision {{container}}", { container: containerTerm })}
      </Button>
    </div>
  );
};

export { FolderCreator };
