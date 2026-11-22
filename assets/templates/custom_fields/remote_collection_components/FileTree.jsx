// Part of Knowledge Commons Works
// Copyright (C) 2023-2026, MESH Research
//
// Knowledge Commons Works is an instance of InvenioRDM, which is
// Copyright (c) 2019-2026, CERN
//
// Knowledge Commons Works and InvenioRDM are both free software;
// You can redistribute and/or modify them under the terms of the
// MIT License; see LICENSE file for more details.

import React, { useCallback, useEffect, useMemo, useRef, useState } from "react";
import { Button, Icon, List, Popup } from "semantic-ui-react";
import { Trans } from "react-i18next";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import apiClient from "@js/kcworks/utils/apiClient";
import { formatSizeGb } from "@js/kcworks/utils/formatSizeGb";

import { kcworksAuthStartURL } from "./common";
import { globusFileManagerUrl as buildGlobusFileManagerUrl } from "./common";

/**
 * Build an absolute path for a child entry under `parentPath`.
 *
 * @param {string} parentPath
 * @param {string} name
 * @returns {string}
 */
const childItemPath = (parentPath, name) =>
  parentPath === "/" ? `/${name}` : `${parentPath}/${name}`;

/**
 * Stable key for list membership / ordering.
 *
 * @param {{ name: string, type?: string }} item
 * @returns {string}
 */
const itemKey = (item) => `${item.type || "file"}:${item.name}`;

/**
 * List a folder via Globus. Used for access probes and child prefetch.
 *
 * @param {string} endpointId
 * @param {string} path
 * @returns {Promise<{ ok: boolean, children: object[]|null }>}
 */
const fetchFolderListing = async (endpointId, path) => {
  try {
    const response = await apiClient.get(`/api/globus/ls/${endpointId}`, {
      params: { path },
    });
    return { ok: true, children: response.data || [] };
  } catch (err) {
    const status = err.response?.status;
    if (status !== 401 && status !== 403) {
      console.error("Failed to list folder:", err);
    }
    return { ok: false, children: null };
  }
};

/**
 * Single-pass visibility classification for a directory listing.
 *
 * - Files: always visible (no probe).
 * - Directories with `is_eligible` set: visible only when true (no probe).
 * - Directories without `is_eligible`: need a Globus `ls` probe.
 *
 * @param {object[]} list
 * @returns {{ visible: object[], toProbe: object[], order: Map<string, number> }}
 */
const classifyItems = (list) => {
  const visible = [];
  const toProbe = [];
  const order = new Map();

  list.forEach((item, index) => {
    order.set(itemKey(item), index);
    if (item.type !== "dir") {
      visible.push(item);
      return;
    }
    if (Object.prototype.hasOwnProperty.call(item, "is_eligible")) {
      if (item.is_eligible) {
        visible.push(item);
      }
      return;
    }
    toProbe.push(item);
  });

  return { visible, toProbe, order };
};

/**
 * Insert `item` into `prev` preserving original listing order.
 *
 * @param {object[]} prev
 * @param {object} item
 * @param {Map<string, number>} order
 * @returns {object[]}
 */
const insertInOriginalOrder = (prev, item, order) => {
  const key = itemKey(item);
  if (prev.some((entry) => itemKey(entry) === key)) {
    return prev;
  }
  const itemIndex = order.get(key);
  const next = [...prev];
  const insertAt = next.findIndex((entry) => order.get(itemKey(entry)) > itemIndex);
  if (insertAt === -1) {
    next.push(item);
  } else {
    next.splice(insertAt, 0, item);
  }
  return next;
};

/**
 * Resolve which items may appear in the tree.
 *
 * Classifies once, seeds visible rows, then inserts probed folders as they succeed.
 *
 * @param {object[]|null|undefined} items
 * @param {string} endpointId
 * @param {string} [parentPath="/"]
 * @returns {{ accessibleItems: object[], isChecking: boolean }}
 */
const useAccessibleItems = (items, endpointId, parentPath = "/") => {
  const [accessibleItems, setAccessibleItems] = useState([]);
  const [isChecking, setIsChecking] = useState(false);

  // Stabilize dependency when parents rebuild arrays each render.
  const itemsSignature = useMemo(
    () =>
      (items || [])
        .map(
          (item) =>
            `${itemKey(item)}:${
              Object.prototype.hasOwnProperty.call(item, "is_eligible")
                ? String(!!item.is_eligible)
                : ""
            }`
        )
        .join("|"),
    [items]
  );

  useEffect(() => {
    let cancelled = false;
    const { visible, toProbe, order } = classifyItems(items || []);

    setAccessibleItems(visible);

    if (!endpointId || toProbe.length === 0) {
      setIsChecking(false);
      return () => {
        cancelled = true;
      };
    }

    setIsChecking(true);

    Promise.all(
      toProbe.map(async (item) => {
        const path = childItemPath(parentPath, item.name);
        const { ok, children } = await fetchFolderListing(endpointId, path);
        if (ok && !cancelled) {
          setAccessibleItems((prev) =>
            insertInOriginalOrder(prev, { ...item, prefetchedChildren: children }, order)
          );
        }
      })
    ).finally(() => {
      if (!cancelled) {
        setIsChecking(false);
      }
    });

    return () => {
      cancelled = true;
    };
    // itemsSignature captures items contents; `items` used inside intentionally.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [itemsSignature, endpointId, parentPath]);

  return { accessibleItems, isChecking };
};

const TreeItem = ({
  item,
  endpointId,
  path = "/",
  autoOpen = false,
  globusAppDomain,
  selectedFolder,
  onSelectFolder,
  depth = 0,
}) => {
  const [isOpen, setIsOpen] = useState(false);
  const [rawChildren, setRawChildren] = useState(() => item.prefetchedChildren ?? null);
  const [loading, setLoading] = useState(false);
  const childrenFetchRef = useRef(null);

  const isDirectory = item.type === "dir";
  const currentItemPath = childItemPath(path, item.name);
  // Directory Globus opens: this folder, or the parent for files.
  const currentDirectoryPath = isDirectory ? currentItemPath : path === "/" ? "/" : path;
  const globusFileManagerUrl = buildGlobusFileManagerUrl(
    endpointId,
    currentDirectoryPath === "/" ? "/" : `${currentDirectoryPath}/`,
    globusAppDomain
  );

  const childItems = isOpen && rawChildren ? rawChildren : [];
  const { accessibleItems: accessibleChildren, isChecking: isCheckingChildren } =
    useAccessibleItems(childItems, endpointId, currentItemPath);

  const ensureChildren = useCallback(async () => {
    if (rawChildren !== null) {
      return rawChildren;
    }
    if (childrenFetchRef.current) {
      return childrenFetchRef.current;
    }
    childrenFetchRef.current = (async () => {
      const { ok, children } = await fetchFolderListing(endpointId, currentItemPath);
      const listing = ok ? children || [] : [];
      if (ok) {
        console.log("Fetched folder contents:", listing);
      }
      setRawChildren(listing);
      return listing;
    })().finally(() => {
      childrenFetchRef.current = null;
    });
    return childrenFetchRef.current;
  }, [rawChildren, endpointId, currentItemPath]);

  // Prefer children captured during the access probe when the row appears.
  useEffect(() => {
    if (item.prefetchedChildren && rawChildren === null) {
      setRawChildren(item.prefetchedChildren);
    }
  }, [item.prefetchedChildren, rawChildren]);

  // Prefetch children for visible folders (e.g. is_eligible) so expand is instant.
  useEffect(() => {
    if (!isDirectory || !endpointId || rawChildren !== null || item.prefetchedChildren) {
      return;
    }
    ensureChildren();
  }, [isDirectory, endpointId, rawChildren, item.prefetchedChildren, ensureChildren]);

  useEffect(() => {
    if (!autoOpen || !isDirectory || isOpen) {
      return;
    }
    let cancelled = false;
    (async () => {
      setLoading(true);
      try {
        await ensureChildren();
        if (!cancelled) {
          setIsOpen(true);
        }
      } finally {
        if (!cancelled) {
          setLoading(false);
        }
      }
    })();
    return () => {
      cancelled = true;
    };
  }, [autoOpen, isDirectory, isOpen, ensureChildren]);

  const handleGlobusLinkClick = async (e) => {
    e.preventDefault();
    e.stopPropagation();

    try {
      await apiClient.get(`/api/globus/ls/${endpointId}`, {
        params: { path: currentDirectoryPath },
      });
      window.open(globusFileManagerUrl, "_blank");
    } catch (err) {
      const code = err.response?.data?.code;
      const message = err.response?.data?.message;

      if (code === "globus_forbidden") {
        const confirmContinue403 = window.confirm(
          (message ||
            "You do not have permission to view this folder's contents.") +
            " If you continue to the Globus File Manager, you will see an empty directory." +
            "\n\nDo you still want to continue?"
        );
        if (confirmContinue403) {
          window.open(globusFileManagerUrl, "_blank");
        }
      } else if (code === "globus_auth_required") {
        const confirm401 = window.confirm(
          (message ||
            "Your Globus session has expired or Globus authorization is required.") +
            "\n\nWould you like to reconnect Globus?"
        );
        if (confirm401) {
          window.location.href = kcworksAuthStartURL(
            window.location.pathname + window.location.search
          );
        }
      } else if (err.response?.status === 401 && !code) {
        window.alert(
          "Your KCWorks session has expired. Please sign in again."
        );
      } else {
        window.alert(
          message ||
            "Could not verify access to this folder in Globus. The File Manager was not opened."
        );
      }
    }
  };

  const handleToggle = async () => {
    if (!isDirectory) return;

    const nextOpenState = !isOpen;
    setIsOpen(nextOpenState);

    if (nextOpenState && rawChildren === null) {
      setLoading(true);
      try {
        await ensureChildren();
      } finally {
        setLoading(false);
      }
    }
  };

  const handleSelectClick = (e) => {
    e.stopPropagation();
    e.preventDefault();
    // Visible directories are already access-gated.
    onSelectFolder(currentItemPath);
  };

  const sizeLabel = formatSizeGb(item.size_gb);
  const childrenReady = !loading && rawChildren !== null;
  const showEmpty =
    isOpen && childrenReady && !isCheckingChildren && accessibleChildren.length === 0;

  const globusLink = (
    <Popup
      content="Open in Globus"
      trigger={
        <a href={globusFileManagerUrl} onClick={handleGlobusLinkClick} className="right floated">
          <Icon name="external alternate" color="blue" />
        </a>
      }
    />
  );

  if (!isDirectory) {
    return (
      <List.Item
        role="treeitem"
        aria-level={depth + 1}
        className="middle aligned file-tree-row pt-5 pb-5"
      >
        <Icon name="file outline" />
        <List.Content>
          <List.Header as="span">{item.name}</List.Header>
          {globusLink}
        </List.Content>
      </List.Item>
    );
  }

  return (
    <List.Item
      role="treeitem"
      aria-expanded={isOpen}
      aria-level={depth + 1}
      className="middle aligned file-tree-row mt-0 pt-5 pb-5"
      style={{ paddingLeft: `${10 * depth}px` }}
      onClick={handleToggle}
    >
      <List.Content floated="right">
        <Button
          size="mini"
          compact
          color={selectedFolder === currentItemPath ? "blue" : null}
          onClick={handleSelectClick}
          className="right floated"
        >
          {selectedFolder === currentItemPath ? "Selected" : "Select"}
        </Button>
      </List.Content>
      <Icon name={isOpen ? "folder open" : "folder"} />
      <List.Content>
        <List.Header as="span">
          {item.name}
          {globusLink}
        </List.Header>
        {sizeLabel && <List.Description>({sizeLabel})</List.Description>}
        {showEmpty && <span>(Empty)</span>}
      </List.Content>

      {isOpen && (
        <List.List role="group">
          {(loading || rawChildren === null || isCheckingChildren) && (
            <List.Item>
              <div className="ui active centered inline loader mt-10 mb-10" />
            </List.Item>
          )}
          {childrenReady &&
            accessibleChildren.map((child, idx) => (
              <TreeItem
                key={`${depth}-${itemKey(child)}-${idx}`}
                item={child}
                endpointId={endpointId}
                path={currentItemPath}
                depth={depth + 1}
                globusAppDomain={globusAppDomain}
                selectedFolder={selectedFolder}
                onSelectFolder={onSelectFolder}
              />
            ))}
        </List.List>
      )}
    </List.Item>
  );
};

const FileTree = ({
  initialFiles,
  endpointId,
  fieldPath,
  globusAppDomain,
  selectedFolder,
  onSelectFolder,
  searchQuery,
  containerTerm,
  depth = 0,
}) => {
  const filteredFiles = useMemo(() => {
    const files = initialFiles || [];
    if (!searchQuery) {
      return files;
    }
    return files.filter((f) => f.name.toLowerCase().includes(searchQuery.toLowerCase()));
  }, [initialFiles, searchQuery]);

  const { accessibleItems, isChecking } = useAccessibleItems(filteredFiles, endpointId, "/");

  // Keep API compat for callers that pass fieldPath.
  void fieldPath;

  const effectiveContainerTerm = depth === 0 ? containerTerm : i18next.t("folder");

  return (
    <div className="field mt-10">
      {isChecking && <div className="ui active centered inline loader mt-10 mb-10" />}

      {accessibleItems.length > 0 && (
        <List relaxed divided verticalAlign="middle" role="tree" className="file-tree">
          {accessibleItems.map((item, index) => (
            <TreeItem
              key={`suggested-${itemKey(item)}-${index}`}
              item={item}
              endpointId={endpointId}
              globusAppDomain={globusAppDomain}
              selectedFolder={selectedFolder}
              onSelectFolder={onSelectFolder}
              depth={depth}
            />
          ))}
        </List>
      )}

      {!isChecking && !!searchQuery && filteredFiles.length === 0 && (
        <div className="ui message info">
          <Trans
            default="No {{container}} found matching your search."
            values={{ container: effectiveContainerTerm }}
          />
        </div>
      )}

      {!isChecking && filteredFiles.length > 0 && accessibleItems.length === 0 && (
        <div className="ui message info">
          <Trans
            default="No {{container}} for which you have permissions."
            values={{ container: containerTerm }}
          />
        </div>
      )}
    </div>
  );
};

export { FileTree };
