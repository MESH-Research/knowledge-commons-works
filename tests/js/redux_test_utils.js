import React from 'react'
import { render } from '@testing-library/react'
import { Provider } from 'react-redux'

import { configureStore } from '@js/invenio_rdm_records/src/deposit/store'
import { setupStore } from './redux_store'
import {
  RDMDepositRecordSerializer,
} from "@js/invenio_rdm_records/src/deposit/api/DepositRecordSerializer";
import {
  RDMDepositApiClient,
  RDMDepositFileApiClient,
} from "@js/invenio_rdm_records/src/deposit/api/DepositApiClient";

function renderWithProviders(
  ui,
  {
    preloadedState = {},
    // Automatically create a store instance if no store was passed in
    store = setupStore(preloadedState),
    ...renderOptions
  } = {}
) {
  function Wrapper({ children }) {
    return <Provider store={store}>{children}</Provider>
  }
  return { store, ...render(ui, { wrapper: Wrapper, ...renderOptions }) }
}

export { renderWithProviders }
