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
import { Icon, Input, Message } from "semantic-ui-react";
import { Trans } from "react-i18next";

import { i18next } from "@translations/invenio_app_rdm/i18next";

import { FileTree } from "./FileTree";

const FolderPicker = ({
  containerTerm,
  fieldPath,
  globusAppDomain,
  loadingTree,
  netid,
  rootFiles,
  searchQuery,
  selectedFolder,
  selectedMappedCollection,
  setSearchQuery,
  setSelectedFolder,
  treeError,
}) => {
  console.log("rootFiles", rootFiles);
  return loadingTree ? (
    <div className="ui active centered inline loader"></div>
  ) : treeError ? (
    <Message negative>{treeError}</Message>
  ) : (
    <>
      <div
        className="field-label-class invenio-field-label ml-5"
        id={`${fieldPath}.fileTree.label`}
        style={{ fontWeight: "bold" }}
      >
        {/*<Icon name="sitemap" />{" "}*/}
        <Trans
          defaults="Choose a {{container}} or subfolder"
          values={{ container: containerTerm.toLowerCase() }}
        />
      </div>
      {rootFiles?.length > 6 ? (
        <Input
          icon="search"
          placeholder={i18next.t("Search {{container}}s...", {
            container: containerTerm.toLowerCase(),
          })}
          value={searchQuery}
          onChange={(e) => setSearchQuery(e.target.value)}
          fluid
          style={{ marginBottom: "15px" }}
        />
      ) : null}
      <div
        style={{
          maxHeight: "400px",
          overflowY: "auto",
          paddingRight: "10px",
        }}
      >
        <FileTree
          initialFiles={rootFiles}
          endpointId={selectedMappedCollection}
          fieldPath={fieldPath}
          globusAppDomain={globusAppDomain}
          selectedFolder={selectedFolder}
          onSelectFolder={setSelectedFolder}
          netid={netid}
          searchQuery={searchQuery}
          containerTerm={containerTerm}
        />
      </div>
    </>
  );
};

export { FolderPicker };
