import React, { useContext, useState } from "react";
import { Accordion, Icon, Table, Message } from "semantic-ui-react";
import { i18next } from "@translations/i18next";
import { FormUIStateContext } from "@js/invenio_modular_deposit_form/InnerDepositForm";
import PropTypes from "prop-types";
import { supportedExtensions, unsupportedExtensions } from "./index";

const categorizeFileTypes = (extensions) => {
  const categories = Object.keys(supportedExtensions).reduce(
    (acc, category) => {
      acc[category] = {
        supported: [],
        unsupported: [...unsupportedExtensions[category]],
      };
      return acc;
    },
    {}
  );
  categories.other = { supported: [], unsupported: [] };

  extensions.forEach((ext) => {
    const lowerExt = ext.toLowerCase();
    let categorized = false;

    for (const [category, exts] of Object.entries(supportedExtensions)) {
      if (exts.includes(lowerExt)) {
        categories[category].supported.push(ext);
        categorized = true;
        break;
      }
    }

    if (!categorized) {
      let foundUnsupported = false;
      for (const [category, unsupportedExts] of Object.entries(
        unsupportedExtensions
      )) {
        if (unsupportedExts.includes(lowerExt)) {
          foundUnsupported = true;
          break;
        }
      }
      if (!foundUnsupported) {
        categories.other.unsupported.push(ext);
      }
    }
  });

  // Sort supported extensions based on the order in supportedExtensions
  for (const category in categories) {
    if (category !== "other") {
      categories[category].supported.sort((a, b) => {
        return (
          supportedExtensions[category].indexOf(a.toLowerCase()) -
          supportedExtensions[category].indexOf(b.toLowerCase())
        );
      });
    }
  }

  return categories;
};

const FileTypeRow = ({ category, types }) => {
  return types.supported.length === 0 &&
    types.unsupported.length === 0 ? null : (
    <Table.Row>
      <Table.Cell>
        <strong>{i18next.t(category)}</strong>
      </Table.Cell>
      <Table.Cell className="positive">{types.supported.join(", ")}</Table.Cell>
      <Table.Cell className="negative">{types.unsupported.join(", ")}</Table.Cell>
    </Table.Row>
  );
};

FileTypeRow.propTypes = {
  category: PropTypes.string.isRequired,
  types: PropTypes.shape({
    supported: PropTypes.arrayOf(PropTypes.string),
    unsupported: PropTypes.arrayOf(PropTypes.string),
  }).isRequired,
};

const FileTypeMessage = () => {
  const { previewableExtensions } = useContext(FormUIStateContext);
  const [isOpen, setIsOpen] = useState(false);

  if (!previewableExtensions || previewableExtensions.length === 0)
    return null;

  const fileCategories = categorizeFileTypes(previewableExtensions);

  const handleAccordionClick = () => {
    setIsOpen(!isOpen);
  };

  return (
    <Message info icon className="file-type-message mt-0">
      <Icon name="file" size="large" />
      <Message.Content>
        <Accordion>
          <Accordion.Title active={isOpen} onClick={handleAccordionClick}>
            <Icon name="dropdown" />
            {i18next.t("List of supported file types with KCWorks previews...")}
          </Accordion.Title>
          <Accordion.Content active={isOpen}>
            <p>
              {i18next.t(
                "Supported file types ")}
              <b>{i18next.t("can be previewed")}</b>
              {i18next.t(" on the work detail page. Unsupported file types ")}
              <b>{i18next.t("can still be uploaded")}</b>
              {i18next.t(" but will not be displayed.")}
            </p>
            <Table celled>
              <Table.Header>
                <Table.Row>
                  <Table.HeaderCell>{i18next.t("File Type")}</Table.HeaderCell>
                  <Table.HeaderCell className="positive">
                    {i18next.t("Previewable")}
                  </Table.HeaderCell>
                  <Table.HeaderCell className="negative">
                    {i18next.t("Not Previewable (Uploadable)")}
                  </Table.HeaderCell>
                </Table.Row>
              </Table.Header>
              <Table.Body>
                <FileTypeRow
                  category="Text files"
                  types={fileCategories.text}
                />
                <FileTypeRow category="Images" types={fileCategories.image} />
                <FileTypeRow
                  category="Video files"
                  types={fileCategories.video}
                />
                <FileTypeRow
                  category="Audio files"
                  types={fileCategories.audio}
                />
                <FileTypeRow
                  category="Structured data"
                  types={fileCategories.structuredData}
                />
                <FileTypeRow
                  category="Source code"
                  types={fileCategories.sourceCode}
                />
                <FileTypeRow
                  category="File archives"
                  types={fileCategories.archive}
                />
                <FileTypeRow category="Other" types={fileCategories.other} />
              </Table.Body>
            </Table>
          </Accordion.Content>
        </Accordion>
      </Message.Content>
    </Message>
  );
};

FileTypeMessage.propTypes = {
  // No props for this component, but we can add an empty object for consistency
};

export { FileTypeMessage };
