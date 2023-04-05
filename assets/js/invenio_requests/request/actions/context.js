import React from "react";

export const RequestActionContext = React.createContext({
  modalOpen: false,
  toggleModal: () => {},
  linkExtractor: undefined,
  requestApi: undefined,
  performAction: () => {},
  cleanError: () => {},
  error: undefined,
  loading: false,
});
