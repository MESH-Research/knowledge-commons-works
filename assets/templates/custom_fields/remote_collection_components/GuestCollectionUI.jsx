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
import { Grid, Icon, Menu, Message, Segment } from "semantic-ui-react";

import { i18next } from "@translations/invenio_app_rdm/i18next";

import { EDITING_STEP } from "./common";
import { SelectedGuestCollection } from "./SelectedGuestCollection";
import { FolderCreator } from "./FolderCreator";
import { ExistingFolderUI } from "./ExistingFolderUI";
import { GuestCollectionSelector } from "./GuestCollectionSelector";

const GUEST_COLLECTION_TABS = {
  NEW_FOLDER: "newFolder",
  EXISTING_FOLDER: "existingFolder",
  EXISTING_GUEST: "existingGuest",
};

const GuestCollectionUI = ({
  activeTab,
  bucketName,
  checkingCollections,
  checkError,
  currentEndpoint,
  editingStep,
  fetchMatchedCollections,
  fetchRootFiles,
  fieldPath,
  globusAppDomain,
  isPublic,
  loadingTree,
  matchedCollections,
  netid,
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
  const containerTerm = i18next.t(currentEndpoint?.container_term || "Folder");

  console.log("Active tab is", activeTab);

  return (
    <>
      {selectedGuestCollection && editingStep !== EDITING_STEP.GUEST ? (
        <SelectedGuestCollection
          {...{
            globusAppDomain,
            matchedCollections,
            selectedGuestCollection,
            setEditingStep,
          }}
        />
      ) : (
        <Grid.Row>
          <Grid.Column>
            <div className="description">
              {i18next.t(
                `To share files, you must have a {{container}} and must share its 
                 contents via a Globus "guest collection". Below you can choose or 
                 create a guest collection on an existing {{container}}, or you can 
                 create a new (empty) {{container}} along with a guest collection to 
                 share its contents.`,
                { container: containerTerm.toLowerCase() }
              )}
            </div>

            <Segment className="p-0">
              <Menu pointing secondary className="mt-0 mb-0">
                {activeTab === GUEST_COLLECTION_TABS.EXISTING_GUEST ? (
                  <>
                    <Menu.Item
                      name={i18next.t("Link existing guest collection")}
                      active={activeTab === GUEST_COLLECTION_TABS.EXISTING_GUEST}
                      onClick={() => setActiveTab(GUEST_COLLECTION_TABS.EXISTING_GUEST)}
                    />
                    <Menu.Item
                      name={i18next.t("Create a new guest collection")}
                      active={activeTab === GUEST_COLLECTION_TABS.EXISTING_FOLDER}
                      onClick={() => setActiveTab(GUEST_COLLECTION_TABS.EXISTING_FOLDER)}
                    />
                  </>
                ) : (
                  <>
                    <Menu.Item
                      active={activeTab === GUEST_COLLECTION_TABS.EXISTING_GUEST}
                      onClick={() => setActiveTab(GUEST_COLLECTION_TABS.EXISTING_GUEST)}
                    >
                      <Icon name="chevron left" />
                    </Menu.Item>
                    <Menu.Item
                      name={i18next.t("Share existing {{container}}", {
                        container: containerTerm.toLowerCase(),
                      })}
                      active={activeTab === GUEST_COLLECTION_TABS.EXISTING_FOLDER}
                      onClick={() => setActiveTab(GUEST_COLLECTION_TABS.EXISTING_FOLDER)}
                    />
                    <Menu.Item
                      name={i18next.t("Create new {{container}}", {
                        container: containerTerm.toLowerCase(),
                      })}
                      active={activeTab === GUEST_COLLECTION_TABS.NEW_FOLDER}
                      onClick={() => setActiveTab(GUEST_COLLECTION_TABS.NEW_FOLDER)}
                    />
                  </>
                )}
              </Menu>
              <Segment basic>
                {activeTab === GUEST_COLLECTION_TABS.EXISTING_GUEST && (
                  <GuestCollectionSelector
                    {...{
                      checkingCollections,
                      checkError,
                      matchedCollections,
                      selectedGuestCollection,
                      setEditingStep,
                      showAll: true,
                      showHeading: false,
                      updateGlobusState,
                    }}
                  />
                )}

                {activeTab === GUEST_COLLECTION_TABS.EXISTING_FOLDER && (
                  <ExistingFolderUI
                    {...{
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
                      netid,
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
                    }}
                  />
                )}

                {/* FIXME: ensure underscores etc. are disallowed in bucket names */}
                {activeTab === GUEST_COLLECTION_TABS.NEW_FOLDER && (
                  <FolderCreator
                    {...{
                      containerTerm,
                      bucketName,
                      setBucketName,
                      selectedMappedCollection,
                      fetchRootFiles,
                      setSelectedFolder,
                      setActiveTab,
                      updateGlobusState,
                    }}
                  />
                )}
              </Segment>
            </Segment>
            <div className="helptext">
              {i18next.t(
                `Files from your collection remain on your server. This KCWorks record 
                 provides information about and links to that content. It also makes your 
                 data discoverable in searches and on the record detail page.`,
                { container: containerTerm.toLowerCase() }
              )}
            </div>
          </Grid.Column>
        </Grid.Row>
      )}
    </>
  );
};

export { GuestCollectionUI, GUEST_COLLECTION_TABS };
