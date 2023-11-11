import React from "react";
import { Dropdown } from "semantic-ui-react";

function ExportFormat({ name, exportUrl }) {
  return (
    <div>
      <a href={exportUrl} className="ui button">
        {name}
      </a>
    </div>
  );
}

function SidebarExportSection({ isPreview, recordExporters, record, show }) {
  const formats = [];
  for (const [fmt, val] of Object.entries(recordExporters)) {
    const name = val.name || fmt;
    const exportUrl = isPreview
      ? `/records/${record.id}/export/${fmt}?preview=1`
      : `/records/${record.id}/export/${fmt}`;
    formats.push({ name, exportUrl });
  }

  return (
    <div className={`sidebar-container ${show}`} id="record-export">
      {/* <h2 className="ui medium top attached header mt-0">Export</h2>
      <div
        id="export-record"
        className="ui segment bottom attached exports rdm-sidebar"
      > */}
      <Dropdown basic button fluid text="Export as..." className="">
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
      {/* </div> */}
    </div>
  );
}

export { SidebarExportSection };
