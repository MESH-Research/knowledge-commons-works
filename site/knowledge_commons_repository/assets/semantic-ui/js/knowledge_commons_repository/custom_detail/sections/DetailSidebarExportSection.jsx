import React from "react";
import { Dropdown } from "semantic-ui-react";

const ExportDropdown = ({
  asButton = true,
  asFluid = true,
  asItem = false,
  icon = "dropdown",
  id = "export-dropdown",
  text = "Export metadata as...",
  classNames = "",
  record,
  recordExporters,
  isPreview,
}) => {
  const formats = [];
  for (const [fmt, val] of Object.entries(recordExporters)) {
    const name = val.name || fmt;
    const exportUrl = isPreview
      ? `/records/${record.id}/export/${fmt}?preview=1`
      : `/records/${record.id}/export/${fmt}`;
    formats.push({ name, exportUrl });
  }

  return (
    <Dropdown
      basic
      button={asButton}
      fluid={asFluid}
      id={id}
      item={asItem}
      text={text}
      icon={icon}
      className={classNames}
    >
      <Dropdown.Menu>
        {formats.map((format, index) => (
          <Dropdown.Item
            as="a"
            key={index}
            text={format.name}
            href={format.exportUrl}
          />
        ))}
      </Dropdown.Menu>
    </Dropdown>
  );
};

function SidebarExportSection({ isPreview, recordExporters, record, show }) {
  return (
    <div className={`sidebar-container ${show}`} id="record-export">
      {/* <h2 className="ui medium top attached header mt-0">Export</h2>
      <div
        id="export-record"
        className="ui segment bottom attached exports rdm-sidebar"
      > */}
      <ExportDropdown {...{ record, isPreview, recordExporters }} />
      {/* </div> */}
    </div>
  );
}

export { ExportDropdown, SidebarExportSection };
