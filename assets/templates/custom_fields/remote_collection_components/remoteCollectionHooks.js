import React, { useCallback, useEffect, useState } from "react";
import apiClient from "@js/kcworks/utils/apiClient";
import { getIn, useFormikContext } from "formik";

import { EDITING_STEP } from "./common";

const useGlobusTokenFetch = () => {
  const [hasToken, setHasToken] = useState(false);
  const [endpoints, setEndpoints] = useState([]);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [netid, setNetid] = useState("");

  useEffect(() => {
    let cancelled = false;

    apiClient
      .get("/api/globus/endpoints")
      .then((response) => {
        if (cancelled) {
          return;
        }
        setHasToken(true);
        setEndpoints(response.data.endpoints || []);
        console.log("raw response", response.data.endpoints);
        setNetid(response.data.netid || "");
      })
      .catch(() => {
        if (!cancelled) {
          setHasToken(false);
        }
      })
      .finally(() => {
        if (!cancelled) {
          setLoadingInitial(false);
        }
      });

    return () => {
      cancelled = true;
    };
  }, []);

  return { endpoints, hasToken, loadingInitial, netid, setHasToken };
};

const useGlobusRootFiles = (selectedMappedCollection, setHasToken, setSelectedFolder) => {
  const [rootFiles, setRootFiles] = useState([]);
  const [loadingTree, setLoadingTree] = useState(false);
  const [treeError, setTreeError] = useState(null);
  const [searchQuery, setSearchQuery] = useState("");

  const fetchRootFiles = useCallback(
    async (endpointId) => {
      if (!endpointId) {
        return;
      }
      setLoadingTree(true);
      setTreeError(null);
      try {
        const response = await apiClient.get(`/api/globus/ls/${endpointId}`, {
          params: { path: "/" },
        });
        setRootFiles(response.data);
      } catch (err) {
        console.error("Failed to fetch root files for selected endpoint:", err);
        if (err.response?.status === 401) {
          setHasToken(false);
        } else {
          setTreeError("Failed to load directory contents. You may not have permission.");
        }
      } finally {
        setLoadingTree(false);
      }
    },
    [setHasToken]
  );

  useEffect(() => {
    if (!selectedMappedCollection) {
      return;
    }
    setSelectedFolder(null);
    setSearchQuery("");
    fetchRootFiles(selectedMappedCollection);
  }, [selectedMappedCollection, fetchRootFiles, setSelectedFolder]);

  return {
    rootFiles,
    loadingTree,
    treeError,
    searchQuery,
    setSearchQuery,
    fetchRootFiles,
  };
};

const useMatchedGuestCollections = (selectedMappedCollection) => {
  const [matchedCollections, setMatchedCollections] = useState(null);
  const [checkingCollections, setCheckingCollections] = useState(false);
  const [checkError, setCheckError] = useState(null);

  const fetchMatchedCollections = useCallback(async (endpointId) => {
    if (!endpointId) {
      setMatchedCollections(null);
      return;
    }
    setCheckingCollections(true);
    setCheckError(null);
    try {
      const response = await apiClient.get("/api/globus/collections/check", {
        params: { endpoint_id: endpointId },
      });
      setMatchedCollections(response.data.matches || []);
    } catch (err) {
      console.error("Failed to fetch guest collections:", err);
      setCheckError("Failed to fetch your guest collections");
    } finally {
      setCheckingCollections(false);
    }
  }, []);

  useEffect(() => {
    if (!selectedMappedCollection) {
      setMatchedCollections(null);
      return;
    }
    fetchMatchedCollections(selectedMappedCollection);
  }, [selectedMappedCollection, fetchMatchedCollections]);

  return {
    matchedCollections,
    checkingCollections,
    checkError,
    fetchMatchedCollections,
  };
};

/**
 * Hydrate local Globus UI state from an existing Formik field value when
 * local state is still empty (mount, or late restore e.g. localStorage).
 *
 * @param {string} fieldPath - Path to the Globus field in Formik
 * @param {object} globusState - Current local Globus UI state
 * @param {Function} setEditingStep - Setter for the collapsible editing step
 * @param {Function} updateGlobusState - Setter for nested Globus state
 * @param {object} values - Formik values
 */
const useFormikHydrate = (fieldPath, globusState, setEditingStep, updateGlobusState, values) => {
  useEffect(() => {
    if (typeof globusState !== "object" || Object.keys(globusState).length > 0) {
      return;
    }
    const initialFormikValue = getIn(values, fieldPath, null);
    if (initialFormikValue && typeof initialFormikValue === "object") {
      updateGlobusState(initialFormikValue);
      setEditingStep(EDITING_STEP.NONE);
    }
  }, [values]);
};

/**
 * Set empty record `files` to disabled when a globus collection value is added.
 *
 * This is to improve UI by streamlining the displayed fields when the file uploader
 * isn't needed. The user can still manually enable files again, and any prior
 * file entries will be respected.
 *
 * @param {object} globusState - Current local Globus UI state
 * @param {Function} setFieldValue - Formik functionn for field setting.
 * @param {object} values - Formik values
 *
 **/
const useFormikFilesDisable = (globusState, setFieldValue, values) => {
  useEffect(() => {
    if (Object.keys(globusState).length !== 0 && !getIn(values, "files.entries")) {
      setFieldValue("files.enabled", false);
    }
  }, [globusState]);
};

/**
 * Keep Formik field updated with current widget values.
 *
 * @param {string} fieldPath - the formik field's dot-separated path
 * @param {Function} setEditingStep - setter to update the UI editing state
 *
 * @returns {object} an object containing a function for updating the Formik field value
 *
 **/
const useGlobusFormikSync = (fieldPath, setEditingStep) => {
  const { values, setFieldValue } = useFormikContext();
  const [globusState, setGlobusState] = useState({});
  // watching for internal state changes and syncing them OUT to Formik
  useEffect(() => {
    if (Object.keys(globusState).length > 0) {
      setFieldValue(fieldPath, globusState);
    }
  }, [globusState, fieldPath, setFieldValue]);

  // helper function to safely update our internal React state
  const updateGlobusState = (newData) => {
    setGlobusState((prevState) => ({ ...prevState, ...newData }));
  };

  useFormikHydrate(fieldPath, globusState, setEditingStep, updateGlobusState, values);
  useFormikFilesDisable(globusState, setFieldValue, values);

  return { globusState, updateGlobusState };
};

export {
  useFormikFilesDisable,
  useFormikHydrate,
  useGlobusFormikSync,
  useGlobusTokenFetch,
  useGlobusRootFiles,
  useMatchedGuestCollections,
};
