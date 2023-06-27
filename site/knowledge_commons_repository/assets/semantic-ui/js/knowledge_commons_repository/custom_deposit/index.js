// This file is part of InvenioRDM
// Copyright (C) 2020-2022 CERN.
// Copyright (C) 2020-2022 Northwestern University.
//
// Invenio App RDM is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState } from "react";
import ReactDOM from "react-dom";
import { getInputFromDOM } from "@js/invenio_rdm_records/";
import { RDMDepositForm } from "./vanilla_RDMDepositForm";
import { OverridableContext, overrideStore } from "react-overridable";
import { Button } from "semantic-ui-react";

const overriddenComponents = overrideStore.getAll();

const DepositPager = ({children}) => {
  const [ currentFormPage, setCurrentFormPage ] = useState("1");

  const handleFormPageChange = (event) => {
    console.log(event.target.value);
    setCurrentFormPage(event.target.value);
    event.preventDefault();
  };

  return(
    <>
    <div className="upload-form-pager">
      {["1", "2", "3", "4", "5"].map((pageNum) => (
        <Button
          key={`upload-form-pager-button-${pageNum}`}
          onClick={handleFormPageChange}
          className={`upload-form-pager-button page-${pageNum}`}
          labelPosition="left"
          content={`page ${pageNum}`}
          type="button"
          value={pageNum}
        />
      ))}
    </div>
    <RDMDepositForm
      record={getInputFromDOM("deposits-record")}
      preselectedCommunity={getInputFromDOM("deposits-draft-community")}
      files={getInputFromDOM("deposits-record-files")}
      config={getInputFromDOM("deposits-config")}
      permissions={getInputFromDOM("deposits-record-permissions")}
      currentFormPage={currentFormPage}
    />
    </>
  )
}

ReactDOM.render(
  <OverridableContext.Provider value={overriddenComponents}>
    <DepositPager />
  </OverridableContext.Provider>,
  document.getElementById("deposit-form")
);

