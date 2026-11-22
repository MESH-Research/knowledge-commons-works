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
import { Grid } from "semantic-ui-react";

import { GuestCollectionCreator } from "./GuestCollectionCreator";
// import { GuestCollectionSelector } from "./GuestCollectionSelector";
import { FolderPicker } from "./FolderPicker";

const ExistingFolderUI = ({
  bucketName,
  checkingCollections,
  checkError,
  containerTerm,
  fetchMatchedCollections,
  fieldPath,
  globusAppDomain,
  isPublic,
  loadingTree,
  matchedCollections,
  rootFiles,
  searchQuery,
  selectedFolder,
  selectedGuestCollection,
  selectedMappedCollection,
  setActiveTab,
  setBucketName,
  setEditingStep,
  setIsPublic,
  setSearchQuery,
  setSelectedFolder,
  treeError,
  updateGlobusState,
}) => {
  return (
    <Grid divided>
      <Grid.Row>
        {/* LEFT COLUMN: FILE TREE */}
        <Grid.Column width={8}>
          <FolderPicker
            {...{
              containerTerm,
              fieldPath,
              globusAppDomain,
              loadingTree,
              rootFiles,
              searchQuery,
              selectedFolder,
              selectedMappedCollection,
              setSearchQuery,
              setSelectedFolder,
              treeError,
            }}
          />
        </Grid.Column>

        {/* RIGHT COLUMN: GUEST COLLECTIONS & CREATION */}
        <Grid.Column width={8}>
          {
            selectedFolder ? (
              <GuestCollectionCreator
                {...{
                  bucketName,
                  containerTerm,
                  fetchMatchedCollections,
                  isPublic,
                  selectedFolder,
                  selectedMappedCollection,
                  setBucketName,
                  setActiveTab,
                  setEditingStep,
                  setIsPublic,
                  setSelectedFolder,
                  updateGlobusState,
                }}
              />
            ) : null
            /*<GuestCollectionSelector
              {...{
                checkingCollections,
                checkError,
                matchedCollections,
                selectedGuestCollection,
                setEditingStep,
                updateGlobusState,
              }}
            />*/
          }
        </Grid.Column>
      </Grid.Row>
    </Grid>
  );
};

export { ExistingFolderUI };
