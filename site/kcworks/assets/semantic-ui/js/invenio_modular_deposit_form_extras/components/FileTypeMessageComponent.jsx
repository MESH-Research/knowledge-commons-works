// This file is part of Knowledge Commons Works
// Copyright (C) 2024 MESH Research.
//
// Knowledge Commons Works is free software; you can redistribute it
// and/or modify it under the terms of the MIT License; see LICENSE
// file for more details.

/**
 * @module FileTypeMessageComponent
 * Adjacent deposit form component rendered below the file uploader.
 * Shows a reactive warning listing any uploaded files whose extensions are
 * not in the platform's previewable set, then offers a collapsible table
 * categorising all supported / unsupported extensions.
 */

import React, { useState } from "react";
import { useSelector } from "react-redux";
import { Accordion, Icon, Message, Table } from "semantic-ui-react";
import { i18next } from "@translations/i18next";

/**
 * Categorisation guide for the accordion table.
 * Extensions that appear here (lower-cased) are mapped to named categories;
 * everything else falls into "other".
 */
const SUPPORTED_EXTENSIONS = {
  text: ["txt", "pdf", "pdfa", "md"],
  image: ["jpg", "jpeg", "png", "gif", "tif", "tiff", "jp2"],
  video: ["mp4", "webm"],
  audio: ["mp3", "wav", "flac", "aac"],
  structuredData: ["json", "xml", "csv", "dsv"],
  sourceCode: ["py", "js", "java", "cpp", "ipynb"],
  archive: ["zip"],
};

const UNSUPPORTED_EXTENSIONS = {
  text: ["doc", "docx"],
  image: [],
  video: ["avi", "mov"],
  audio: [],
  structuredData: [],
  sourceCode: [],
  archive: ["tar", "gz"],
  other: [],
};

const CATEGORY_LABELS = {
  text: "Text files",
  image: "Images",
  video: "Video files",
  audio: "Audio files",
  structuredData: "Structured data",
  sourceCode: "Source code",
  archive: "File archives",
  other: "Other",
};

/**
 * Partition a flat list of extensions into per-category supported / not-supported
 * buckets, using the SUPPORTED_EXTENSIONS / UNSUPPORTED_EXTENSIONS guides above.
 *
 * @param {string[]} extensions - Flat list of previewable extensions from config.
 * @returns {Object} Category map: `{ category: { supported: [], unsupported: [] } }`
 */
function categorizeExtensions(extensions) {
  const categories = Object.keys(SUPPORTED_EXTENSIONS).reduce((acc, cat) => {
    acc[cat] = {
      supported: [],
      unsupported: [...UNSUPPORTED_EXTENSIONS[cat]],
    };
    return acc;
  }, {});
  categories.other = { supported: [], unsupported: [] };

  extensions.forEach((ext) => {
    const lower = ext.toLowerCase();
    let placed = false;
    for (const [cat, exts] of Object.entries(SUPPORTED_EXTENSIONS)) {
      if (exts.includes(lower)) {
        categories[cat].supported.push(ext);
        placed = true;
        break;
      }
    }
    if (!placed) {
      const knownUnsupported = Object.values(UNSUPPORTED_EXTENSIONS).some((list) =>
        list.includes(lower)
      );
      if (!knownUnsupported) {
        categories.other.unsupported.push(ext);
      }
    }
  });

  // Preserve the order defined in SUPPORTED_EXTENSIONS within each category.
  for (const cat in categories) {
    if (cat !== "other") {
      categories[cat].supported.sort(
        (a, b) =>
          (SUPPORTED_EXTENSIONS[cat] ?? []).indexOf(a.toLowerCase()) -
          (SUPPORTED_EXTENSIONS[cat] ?? []).indexOf(b.toLowerCase())
      );
    }
  }

  return categories;
}

const CategoryRow = ({ category, types }) => {
  if (!types.supported.length && !types.unsupported.length) return null;
  return (
    <Table.Row>
      <Table.Cell>
        <strong>{i18next.t(CATEGORY_LABELS[category] ?? category)}</strong>
      </Table.Cell>
      <Table.Cell className="">{types.supported.join(", ")}</Table.Cell>
      <Table.Cell className="">{types.unsupported.join(", ")}</Table.Cell>
    </Table.Row>
  );
};

/**
 * Adjacent component rendered directly below the file uploader field.
 *
 * Behaviour:
 * - If any uploaded files have non-previewable extensions, a warning message
 *   listing those filenames is shown at the top.
 * - A collapsible accordion shows all previewable / non-previewable extensions
 *   organised by category.
 * - Returns null when `previewable_extensions` is absent from the deposit config.
 */
const FileTypeMessageComponent = () => {
  const previewableExtensions = useSelector(
    (state) => state.deposit?.config?.previewable_extensions ?? []
  );
  const fileEntries = useSelector((state) => state.files?.entries ?? {});
  const [isOpen, setIsOpen] = useState(false);

  if (!previewableExtensions.length) return null;

  const previewableSet = new Set(previewableExtensions.map((e) => e.toLowerCase()));

  const nonPreviewableFiles = Object.values(fileEntries).filter((file) => {
    const ext = file.name?.split(".").pop()?.toLowerCase();
    return ext && !previewableSet.has(ext);
  });

  const fileCategories = categorizeExtensions(previewableExtensions);

  console.log("nonPreviewableFiles", nonPreviewableFiles);
  console.log("nonPreviewableFiles", nonPreviewableFiles.length);
  console.log("nonPreviewableFiles", nonPreviewableFiles.length > 0);

  return (
    <>
      {nonPreviewableFiles.length > 0 && (
        <Message icon className="negative mt-0 mb-0">
          <Icon name="warning sign" />
          <Message.Content>
            <Message.Header>{i18next.t("Some files will not be previewable")}</Message.Header>
            <p className="mb-5">
              {i18next.t(
                "The following files will be listed on the work detail page for download, but will not have a preview:"
              )}
            </p>
            <ul className="mt-0 mb-0 pl-15">
              {nonPreviewableFiles.map((f) => (
                <li key={f.name}>
                  <strong>{f.name}</strong>
                </li>
              ))}
            </ul>
            <p className="mt-5">
              {i18next.t("Please consider using supported file types instead (listed below).")}
            </p>
          </Message.Content>
        </Message>
      )}

      <Accordion className="pl-0 pr-0 mt-0 message">
        <Accordion.Title as="button" active={isOpen} onClick={() => setIsOpen(!isOpen)}>
          <Icon name="dropdown" />
          {i18next.t("Supported file types...")}
        </Accordion.Title>
        <Accordion.Content active={isOpen} className="rel-pl-1 rel-pr-1">
          <p>
            {i18next.t("Supported file types ")}
            <b>{i18next.t("can be previewed")}</b>
            {i18next.t(" on the work detail page. Unsupported file types ")}
            <b>{i18next.t("can still be uploaded")}</b>
            {i18next.t(" but will not be displayed.")}
          </p>
          <Table celled>
            <Table.Header>
              <Table.Row>
                <Table.HeaderCell>{i18next.t("File Type")}</Table.HeaderCell>
                <Table.HeaderCell className="">{i18next.t("Previewable")}</Table.HeaderCell>
                <Table.HeaderCell className="">
                  {i18next.t("Not Previewable (Uploadable)")}
                </Table.HeaderCell>
              </Table.Row>
            </Table.Header>
            <Table.Body>
              {Object.entries(fileCategories).map(([cat, types]) => (
                <CategoryRow key={cat} category={cat} types={types} />
              ))}
            </Table.Body>
          </Table>
        </Accordion.Content>
      </Accordion>
    </>
  );
};

export { FileTypeMessageComponent };
