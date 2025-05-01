import { combineReducers, configureStore } from '@reduxjs/toolkit';
// import configureStore from '@js/invenio_rdm_records/src/deposit/store';
import rootReducer from "@js/invenio_rdm_records/src/deposit/state/reducers";
// included reducers in the rootReducer:
// import { computeDepositState } from "@js/invenio_rdm_records/src/deposit/store/state/reducers/deposit";
// import { UploadState } from "@js/invenio_rdm_records/src/deposit/store/state/reducers/files";

export const sampleState = {
    deposit: {
        config: {
            custom_fields: {
                error_labels: {},
            },
        },
        record: {},
        editorState: {},
        files: [],
        permissions: {},
        actionState: null,
        actionStateExtra: {},
    },
    files: {},
};

export const setupStore = preloadedState => {
  return configureStore({
    reducer: rootReducer,
    preloadedState
  })
}

// const sampleStore = setupStore(
//     record, preselectedCommunity, files, config, permissions,
// );

// sampleStore.dispatch(setRecord(record));
// sampleStore.dispatch(setPreselectedCommunity(preselectedCommunity));
// sampleStore.dispatch(setFiles(files));
// sampleStore.dispatch(setConfig(config));
// sampleStore.dispatch(setPermissions(permissions));