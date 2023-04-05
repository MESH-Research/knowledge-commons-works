/*
 * This file is part of Invenio.
 * Copyright (C) 2022 CERN.
 *
 * Invenio is free software; you can redistribute it and/or modify it
 * under the terms of the MIT License; see LICENSE file for more details.
 */
import React from "react";

export const ModalContext = React.createContext({
  closeModal: () => {},
  openModal: () => {},
  modalMode: null,
  modalAction: null,
  modalOpen: false,
});
