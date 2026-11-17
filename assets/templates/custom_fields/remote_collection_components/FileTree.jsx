// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React, { useEffect, useState } from "react";
import {
  Accordion,
  AccordionTitle,
  AccordionContent,
  Button,
  Icon,
  Popup,
} from "semantic-ui-react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import apiClient from "@js/kcworks/utils/apiClient";

import { globusFileManagerUrl as buildGlobusFileManagerUrl } from "./common";

const TreeItem = ({
  item,
  endpointId,
  path = "/",
  depth = 0,
  autoOpen = false,
  autoCheckAccess = false,
  globusAppDomain,
  selectedFolder,
  onSelectFolder,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [children, setChildren] = useState([]);
  const [loading, setLoading] = useState(false);
  const [accessStatus, setAccessStatus] = useState("unknown");
  const [isHovered, setIsHovered] = useState(false);

  useEffect(() => {
    let isMounted = true;
    if (autoCheckAccess && isDirectory && accessStatus === "unknown") {
      const checkAccess = async () => {
        try {
          await apiClient.get(`/api/globus/ls/${endpointId}`, {
            params: { path: currentItemPath },
          });
          if (isMounted) setAccessStatus("allowed");
        } catch (err) {
          if (isMounted && (err.response?.status === 403 || err.response?.status === 401)) {
            setAccessStatus("denied");
          }
        }
      };
      checkAccess();
    }
    return () => {
      isMounted = false;
    };
  }, [autoCheckAccess, isDirectory, endpointId, currentItemPath, accessStatus]);

  const isDirectory = item.type === "dir";
  const currentItemPath = path === "/" ? `/${item.name}` : `${path}/${item.name}`;

  useEffect(() => {
    let isMounted = true;
    const autoFetchChildren = async () => {
      if (autoOpen && isDirectory && !isOpen && children.length === 0) {
        setLoading(true);
        try {
          const response = await apiClient.get(`/api/globus/ls/${endpointId}`, {
            params: { path: currentItemPath },
          });
          if (isMounted) {
            setChildren(response.data);
            setIsOpen(true);
          }
        } catch (err) {
          console.error("Failed to auto-fetch folder contents:", err);
        } finally {
          if (isMounted) setLoading(false);
        }
      }
    };

    autoFetchChildren();

    return () => {
      isMounted = false;
    };
  }, [autoOpen, isDirectory, endpointId, currentItemPath]);

  const globusFileManagerUrl = isDirectory
    ? buildGlobusFileManagerUrl(endpointId, `${currentItemPath}/`, globusAppDomain)
    : null;

  const handleGlobusLinkClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      await apiClient.get(`/api/globus/ls/${endpointId}`, {
        params: { path: currentItemPath },
      });
      window.open(globusFileManagerUrl, "_blank");
    } catch (err) {
      const status = err.response?.status;

      if (status === 403) {
        const confirmContinue403 = window.confirm(
          "You do not have permission to view this folder's contents. " +
            "If you continue to the Globus File Manager, you will see an empty directory. " +
            "\n\nDo you still want to continue?"
        );
        if (confirmContinue403) {
          window.open(globusFileManagerUrl, "_blank");
        }
      } else if (status === 401) {
        const confirm401 = window.confirm(
          "Your session has expired or you are unauthorized to perform this action. " +
            "\n\nWould you like to be redirected to the login page?"
        );
        if (confirm401) {
          window.location.href = "/globus/login";
        }
      } else {
        window.open(globusFileManagerUrl, "_blank");
      }
    }
  };

  const handleToggle = async () => {
    if (!isDirectory) return;

    const nextOpenState = !isOpen;
    setIsOpen(nextOpenState);

    if (nextOpenState && children.length === 0) {
      setLoading(true);
      try {
        const response = await apiClient.get(`/api/globus/ls/${endpointId}`, {
          params: { path: currentItemPath },
        });
        console.log("Fetched folder contents:", response.data);
        setChildren(response.data);
      } catch (err) {
        console.error("Failed to fetch folder contents:", err);
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSelectClick = async (e) => {
    e.stopPropagation();
    e.preventDefault();

    if (accessStatus === "allowed") {
      onSelectFolder(currentItemPath);
      return;
    }

    setLoading(true);
    try {
      await apiClient.get(`/api/globus/ls/${endpointId}`, { params: { path: currentItemPath } });
      setAccessStatus("allowed");
      onSelectFolder(currentItemPath);
    } catch (err) {
      if (err.response?.status === 403 || err.response?.status === 401) {
        setAccessStatus("denied");
      }
    } finally {
      setLoading(false);
    }
  };

  if (!isDirectory) {
    return (
      <div
        style={{
          padding: "5px 0",
          marginLeft: `${depth > 0 ? 25 : 0}px`,
          display: "flex",
          alignItems: "center",
        }}
      >
        <Icon name="file outline" />
        <span style={{ flexGrow: 1, textAlign: "left" }}>{item.name}</span>
        <Popup
          content="Open in Globus"
          trigger={
            <a href={globusFileManagerUrl} onClick={handleGlobusLinkClick}>
              <Icon name="external alternate" style={{ marginLeft: "12px", color: "#2185d0" }} />
            </a>
          }
        />
      </div>
    );
  }

  const showSelect =
    isHovered || selectedFolder === currentItemPath || loading || accessStatus === "denied";

  return (
    <>
      <AccordionTitle
        active={isOpen}
        onClick={handleToggle}
        onMouseEnter={() => setIsHovered(true)}
        onMouseLeave={() => setIsHovered(false)}
        className={`ui fluid transparent button file-tree-btn ${depth > 0 ? "ml-15" : ""} mt-0`}
        style={{
          padding: "5px 0",
          display: "flex",
          alignItems: "center",
          cursor: accessStatus === "denied" ? "not-allowed" : "pointer",
        }}
      >
        <Icon name={isOpen ? "folder open" : "folder"} />

        {item.name}

        {isOpen && !loading && children.length === 0 && <span>(Empty)</span>}

        {loading ? (
          <Icon name="spinner" loading color="blue" />
        ) : accessStatus === "denied" ? (
          <span className="ui label warning">Denied</span>
        ) : (
          <Button
            size="mini"
            compact
            color={selectedFolder === currentItemPath ? "blue" : null}
            onClick={handleSelectClick}
            className={"right floated"}
          >
            {selectedFolder === currentItemPath ? "Selected" : "Select"}
          </Button>
        )}

        {selectedFolder === currentItemPath && (
          <Popup
            content="Open in Globus"
            trigger={
              <a href={globusFileManagerUrl} onClick={handleGlobusLinkClick}>
                <Icon name="external alternate" style={{ marginLeft: "12px", color: "#2185d0" }} />
              </a>
            }
          />
        )}
      </AccordionTitle>

      <AccordionContent active={isOpen} style={{ paddingTop: "0", paddingBottom: "0" }}>
        {loading ? (
          <div style={{ marginLeft: "25px", padding: "5px 0" }}>
            <Icon name="spinner" loading /> Loading...
          </div>
        ) : (
          children.map((child, idx) => (
            <TreeItem
              key={`${depth}-${idx}`}
              item={child}
              endpointId={endpointId}
              path={currentItemPath}
              depth={depth + 1}
              autoOpen={false}
              autoCheckAccess={false}
              globusAppDomain={globusAppDomain}
              selectedFolder={selectedFolder}
              onSelectFolder={onSelectFolder}
            />
          ))
        )}
      </AccordionContent>
    </>
  );
};

const FileTree = ({
  initialFiles,
  endpointId,
  fieldPath,
  globusAppDomain,
  selectedFolder,
  onSelectFolder,
  netid,
  searchQuery,
  containerTerm,
}) => {
  let filteredFiles = initialFiles || [];
  if (searchQuery) {
    filteredFiles = filteredFiles.filter((f) =>
      f.name.toLowerCase().includes(searchQuery.toLowerCase())
    );
  }

  const suggestedFiles = [];
  const otherFiles = [];

  if (netid) {
    filteredFiles.forEach((f) => {
      if (f.name.toLowerCase().startsWith(netid.toLowerCase())) {
        suggestedFiles.push(f);
      } else {
        otherFiles.push(f);
      }
    });
  } else {
    otherFiles.push(...filteredFiles);
  }

  const autoCheck = initialFiles && initialFiles.length < 15;

  return (
    <div className="field mt-10">
      {/* Suggested Buckets */}
      {suggestedFiles.length > 0 && (
        <>
          <h5 className="ui dividing header" style={{ color: "#2185d0" }}>
            {i18next.t("Suggested {{container}}s (Your NetID)", { container: containerTerm })}
          </h5>
          <Accordion as="div">
            {suggestedFiles.map((item, index) => (
              <TreeItem
                key={`suggested-${index}`}
                item={item}
                endpointId={endpointId}
                autoOpen={false}
                autoCheckAccess={autoCheck}
                globusAppDomain={globusAppDomain}
                selectedFolder={selectedFolder}
                onSelectFolder={onSelectFolder}
              />
            ))}
          </Accordion>
        </>
      )}

      {/* All Other Buckets */}
      {otherFiles.length > 0 && (
        <>
          {suggestedFiles.length > 0 && (
            <h5 className="ui dividing header">
              {i18next.t("All Other {{container}}s", { container: containerTerm })}
            </h5>
          )}
          <Accordion>
            {otherFiles.map((item, index) => (
              <TreeItem
                key={`other-${index}`}
                item={item}
                endpointId={endpointId}
                autoOpen={false}
                autoCheckAccess={autoCheck}
                globusAppDomain={globusAppDomain}
                selectedFolder={selectedFolder}
                onSelectFolder={onSelectFolder}
              />
            ))}
          </Accordion>
        </>
      )}

      {filteredFiles.length === 0 && (
        <div className="ui message info">No files found matching your search.</div>
      )}
    </div>
  );
};

export { FileTree };
