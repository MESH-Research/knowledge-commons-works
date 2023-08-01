// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

// import {
//   DRAFT_FETCHED,
//   FILE_DELETED_SUCCESS,
//   FILE_DELETE_FAILED,
//   FILE_IMPORT_FAILED,
//   FILE_IMPORT_STARTED,
//   FILE_IMPORT_SUCCESS,
//   FILE_UPLOAD_SAVE_DRAFT_FAILED,
// } from "../types";
// import { saveDraftWithUrlUpdate } from "./deposit";

export const DRAFT_FETCHED = "DRAFT_FETCHED";
export const FILE_DELETED_SUCCESS = "FILE_DELETED_SUCCESS";
export const FILE_DELETE_FAILED = "FILE_DELETE_FAILED";
export const FILE_IMPORT_STARTED = "FILE_IMPORT_STARTED";
export const FILE_IMPORT_SUCCESS = "FILE_IMPORT_SUCCESS";
export const FILE_IMPORT_FAILED = "FILE_IMPORT_FAILED";
export const FILE_UPLOAD_SAVE_DRAFT_FAILED = "FILE_UPLOAD_SAVE_DRAFT_FAILED";

async function changeURLAfterCreation(draftURL) {
  window.history.replaceState(undefined, "", draftURL);
}

export const saveDraftWithUrlUpdate = async (draft, draftsService) => {
  const hasAlreadyId = !!draft.id;
  const response = await draftsService.save(draft);
  if (!hasAlreadyId) {
    // draft was created, change URL to add the draft PID
    const draftURL = response.data.links.self_html;
    changeURLAfterCreation(draftURL);
  }
  return response;
};


export const uploadFiles = (draft, files) => {
  return async (dispatch, _, config) => {
    console.log('config');
    console.log(config);
    let response;
    try {
      response = await saveDraftWithUrlUpdate(draft, config.service.drafts);
      // update state with created draft
      dispatch({
        type: DRAFT_FETCHED,
        payload: { data: response.data },
      });

      // upload files
      const uploadFileUrl = response.data.links.files;
      for (const file of files) {
        config.service.files.upload(uploadFileUrl, file);
      }
    } catch (error) {
      dispatch({
        type: FILE_UPLOAD_SAVE_DRAFT_FAILED,
        payload: { errors: error.errors },
      });
      throw error;
    }
  };
};

export const deleteFile = (file) => {
  return async (dispatch, _, config) => {
    try {
      const fileLinks = file.links;
      await config.service.files.delete(fileLinks);

      dispatch({
        type: FILE_DELETED_SUCCESS,
        payload: {
          filename: file.name,
        },
      });
    } catch (error) {
      dispatch({ type: FILE_DELETE_FAILED });
      throw error;
    }
  };
};

export const importParentFiles = () => {
  return async (dispatch, getState, config) => {
    const draft = getState().deposit.record;
    if (!draft.id) return;

    dispatch({ type: FILE_IMPORT_STARTED });

    try {
      const draftLinks = draft.links;
      const files = await config.service.files.importParentRecordFiles(draftLinks);
      dispatch({
        type: FILE_IMPORT_SUCCESS,
        payload: { files: files },
      });
    } catch (error) {
      dispatch({ type: FILE_IMPORT_FAILED });
      throw error;
    }
  };
};
