// This file is part of InvenioVocabularies
// Copyright (C) 2021-2023 CERN.
// Copyright (C) 2021 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import { i18next } from "@translations/invenio_rdm_records/i18next";
import React from "react";
import { useDrag, useDrop } from "react-dnd";
import { Button, Icon, Label, List, Ref } from "semantic-ui-react";

import FundingModal from "./FundingModal";
import PropTypes from "prop-types";

export const FundingFieldItem = ({
  compKey,
  index,
  fundingItem,
  awardType,
  moveFunding,
  replaceFunding,
  removeFunding,
  searchConfig,
  deserializeAward,
  deserializeFunder,
  computeFundingContents,
}) => {
  const dropRef = React.useRef(null);
  // eslint-disable-next-line no-unused-vars
  const [_, drag, preview] = useDrag({
    item: { index, type: "award" },
  });
  const [{ hidden }, drop] = useDrop({
    accept: "award",
    hover(item, monitor) {
      if (!dropRef.current) {
        return;
      }
      const dragIndex = item.index;
      const hoverIndex = index;

      // Don't replace items with themselves
      if (dragIndex === hoverIndex) {
        return;
      }

      if (monitor.isOver({ shallow: true })) {
        moveFunding(dragIndex, hoverIndex);
        item.index = hoverIndex;
      }
    },
    collect: (monitor) => ({
      hidden: monitor.isOver({ shallow: true }),
    }),
  });

  let { headerContent, descriptionContent, awardOrFunder } =
    computeFundingContents(fundingItem);

  // Initialize the ref explicitely
  drop(dropRef);
  return (
    <Ref innerRef={dropRef} key={compKey}>
      <List.Item
        key={compKey}
        className={hidden ? "deposit-drag-listitem hidden" : "deposit-drag-listitem"}
      >
        <List.Content floated="right">
          <FundingModal
            searchConfig={searchConfig}
            onAwardChange={(selectedFunding) => {
              replaceFunding(index, selectedFunding);
            }}
            mode={awardType}
            action="edit"
            trigger={
              <Button size="mini" primary type="button">
                {i18next.t("Edit")}
              </Button>
            }
            deserializeAward={deserializeAward}
            deserializeFunder={deserializeFunder}
            computeFundingContents={computeFundingContents}
            initialFunding={fundingItem}
          />
          <Button size="mini" type="button" onClick={() => removeFunding(index)}>
            {i18next.t("Remove")}
          </Button>
        </List.Content>

        <Ref innerRef={drag}>
          <List.Icon name="bars" className="drag-anchor" />
        </Ref>
        <Ref innerRef={preview}>
          <List.Content>
            <List.Header>
              <>
                <span className="mr-5">{headerContent}</span>

                {awardOrFunder === "award"
                  ? fundingItem?.award?.number && (
                      <Label basic size="mini" className="mr-5">
                        {fundingItem.award.number}
                      </Label>
                    )
                  : ""}
                {awardOrFunder === "award"
                  ? fundingItem?.award?.url && (
                      <a
                        href={`${fundingItem.award.url}`}
                        target="_blank"
                        rel="noopener noreferrer"
                        aria-label={i18next.t("Open external link")}
                      >
                        <Icon link name="external alternate" />
                      </a>
                    )
                  : ""}
              </>
            </List.Header>
            <List.Description>
              {descriptionContent ? descriptionContent : <br />}
            </List.Description>
          </List.Content>
        </Ref>
      </List.Item>
    </Ref>
  );
};

FundingFieldItem.propTypes = {
  compKey: PropTypes.any,
  index: PropTypes.number,
  fundingItem: PropTypes.object,
  awardType: PropTypes.string,
  moveFunding: PropTypes.func.isRequired,
  replaceFunding: PropTypes.func.isRequired,
  removeFunding: PropTypes.func.isRequired,
  searchConfig: PropTypes.object.isRequired,
  deserializeAward: PropTypes.func.isRequired,
  deserializeFunder: PropTypes.func.isRequired,
  computeFundingContents: PropTypes.func.isRequired,
};

FundingFieldItem.defaultProps = {
  compKey: undefined,
  index: undefined,
  fundingItem: undefined,
  awardType: undefined,
};
