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
import { Button, Modal } from "semantic-ui-react";
import { Citation } from "../components/Citation";

const CitationSection = ({ record, citationStyles, citationStyleDefault }) => {
  const [open, setOpen] = useState(false);

  return (
    <div
      id="citation"
      className="sidebar-container"
      aria-label={i18next.t("Cite this")}
    >
      <Modal
        trigger={
          <Button
            fluid
            content={i18next.t("Cite this")}
            icon="quote right"
            labelPosition="right"
          ></Button>
        }
        open={open}
        onOpen={() => setOpen(true)}
        onClose={() => setOpen(false)}
      >
        <Modal.Header>Generate a citation for this work</Modal.Header>
        <Modal.Content>
          <Citation
            passedClassNames="ui"
            record={record}
            citationStyles={citationStyles}
            citationStyleDefault={citationStyleDefault}
          />
        </Modal.Content>
      </Modal>
    </div>
  );
};

CitationSection.propTypes = {
  citationStyles: PropTypes.array.isRequired,
  record: PropTypes.object.isRequired,
  citationStyleDefault: PropTypes.string.isRequired,
};

export { CitationSection };
