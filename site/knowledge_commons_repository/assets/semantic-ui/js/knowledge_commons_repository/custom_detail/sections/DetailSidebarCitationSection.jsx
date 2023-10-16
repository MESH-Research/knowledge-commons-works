// This file is part of Knowledge Commons Repository
// Copyright (C) 2023 MESH Research
//
// It is modified from files provided in InvenioRDM
// Copyright (C) 2021 CERN.
// Copyright (C) 2021 Graz University of Technology.
// Copyright (C) 2021 TU Wien
//
// Knowledge Commons Repository and Invenio RDM Records are both free software;
// you can redistribute them and/or modify them under the terms of the MIT
// License; see LICENSE file for more details.

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Citation } from "../components/Citation";

const CitationSection = ({ record, citationStyles, citationStyleDefault }) => {
  return (
    <div
      id="citation"
      className="sidebar-container"
      aria-label={i18next.t("Record citations")}
    >
      <h2 className="ui medium top attached header mt-0">
        {i18next.t("Citation")}
      </h2>
      <Citation
        passedClassNames="ui bottom attached segment rdm-sidebar pr-0 pt-0"
        record={record}
        citationStyles={citationStyles}
        citationStyleDefault={citationStyleDefault}
      />
    </div>
  );
};

CitationSection.propTypes = {
  citationStyles: PropTypes.array.isRequired,
  record: PropTypes.object.isRequired,
  citationStyleDefault: PropTypes.string.isRequired,
};

export { CitationSection };
