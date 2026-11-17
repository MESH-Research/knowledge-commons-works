import React, { useState } from "react";
import { Form, Grid } from "semantic-ui-react";
import { FieldGroupLabel } from "@js/invenio_modular_deposit_form/field_components/patched/input_controls/FieldGroupLabel";
import { i18next } from "@translations/invenio_app_rdm/i18next";

import { EDITING_STEP } from "./remote_collection_components/common";
import { GuestCollectionUI } from "./remote_collection_components/GuestCollectionUI";
import { MappedCollectionSelector } from "./remote_collection_components/MappedCollectionSelector";
import {
  useGlobusFormikSync,
  useGlobusTokenFetch,
  useGlobusRootFiles,
  useMatchedGuestCollections,
} from "./remote_collection_components/remoteCollectionHooks";
import { ServerSelector } from "./remote_collection_components/ServerSelector";

const GlobusLoginButton = () => {
  const currentURL = window.location.pathname + window.location.search;
  const nextUrl = encodeURIComponent(currentURL);
  return (
    <>
      <div className="description">
        {i18next.t("You must connect your Globus account to link a dataset to this record.")}
      </div>
      <a href={`/globus/login/start?next=${nextUrl}`} className="ui primary button">
        Log in with Globus
      </a>
    </>
  );
};

const assembleServerEndpoints = (endpoints) => {
  const hostEndpoints = [];
  const hostMap = new Map();

  endpoints.forEach((ep) => {
    const isGCP = ep.entity_type === "GCP_mapped_collection" || !ep.non_functional_endpoint_id;
    const hostId = isGCP ? ep.id : ep.non_functional_endpoint_id;
    const hostName = isGCP
      ? ep.display_name
      : ep.non_functional_endpoint_display_name || "Unknown Server";

    if (!hostId) {
      return;
    }

    const existing = hostMap.get(hostId);
    if (!existing) {
      const host = { id: hostId, display_name: hostName, isGCP, domain: ep.domain };
      hostMap.set(hostId, host);
      hostEndpoints.push(host);
    } else if (!existing.domain && ep.domain) {
      existing.domain = ep.domain;
    }
  });

  return hostEndpoints;
};

const RemoteDataCollectionField = ({
  fieldPath,
  description = i18next.t("Link an existing Globus data collection or create a new one."),
  helpText = "",
  label = i18next.t("Big Data Collection"),
  labelIcon = "database",
}) => {
  const { endpoints, hasToken, loadingInitial, netid, setHasToken } = useGlobusTokenFetch();
  console.log("endpoints", endpoints);
  // Default to HOST; hydrate sets NONE once Formik already has a linked collection
  // (including late localStorage restore after this state has initialized).
  const [editingStep, setEditingStep] = useState(EDITING_STEP.HOST);
  const { globusState, updateGlobusState } = useGlobusFormikSync(fieldPath, setEditingStep);

  const selectedHostEndpoint = globusState.host_endpoint_id || "";
  const selectedMappedCollection = globusState.mapped_collection_id || "";
  const selectedGuestCollection = globusState.guest_collection_id || "";
  const [selectedFolder, setSelectedFolder] = useState(null);
  const [activeTab, setActiveTab] = useState("existingGuest");
  const [isPublic, setIsPublic] = useState(false);
  const [bucketName, setBucketName] = useState("");

  // Keep these at the field root so collapsing the mapped-collection step
  // (unmounting CollectionSelector) does not drop tree/guest/tab draft state.
  const { rootFiles, loadingTree, treeError, searchQuery, setSearchQuery, fetchRootFiles } =
    useGlobusRootFiles(selectedMappedCollection, setHasToken, setSelectedFolder);
  const { matchedCollections, checkingCollections, checkError, fetchMatchedCollections } =
    useMatchedGuestCollections(selectedMappedCollection);

  const currentEndpoint = endpoints.find((ep) => ep.id === selectedMappedCollection);
  const serverEndpoints = assembleServerEndpoints(endpoints);
  const selectedServer = serverEndpoints.find((s) => s.id === selectedHostEndpoint);
  const globusAppDomain = currentEndpoint?.domain || selectedServer?.domain;

  return (
    <Form.Field>
      <FieldGroupLabel icon={labelIcon} label={label} />
      <div className={`${fieldPath} description`}>{description}</div>
      {loadingInitial ? (
        <div className="ui active centered inline loader"></div>
      ) : !hasToken ? (
        <GlobusLoginButton {...{ fieldPath, label, labelIcon }} />
      ) : (
        <Grid relaxed className="field mb-20">
          <ServerSelector
            {...{
              editingStep,
              serverEndpoints,
              selectedHostEndpoint,
              updateGlobusState,
              setEditingStep,
              setSelectedFolder,
            }}
          />

          {/* 1. MAPPED COLLECTION SELECTOR (COLLAPSIBLE) */}
          {selectedHostEndpoint && editingStep !== EDITING_STEP.HOST && (
            <>
              <MappedCollectionSelector
                {...{
                  editingStep,
                  endpoints,
                  globusAppDomain,
                  selectedHostEndpoint,
                  selectedMappedCollection,
                  setSelectedFolder,
                  setEditingStep,
                  updateGlobusState,
                }}
              />
              {selectedMappedCollection && editingStep !== EDITING_STEP.MAPPED && (
                <GuestCollectionUI
                  {...{
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
                  }}
                />
              )}
            </>
          )}
        </Grid>
      )}
    </Form.Field>
  );
};

export default RemoteDataCollectionField;
