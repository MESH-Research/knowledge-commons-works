import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Dropdown, Icon } from "semantic-ui-react";
import { RecordVersionsList } from "../components/RecordVersionList";

const VersionsListSection = ({ isPreview, record, showHeader = false }) => {
  return (
    <div id="record-versions" className="sidebar-container">
      <h2 className="ui medium top attached header mt-0">
        {i18next.t("Versions")}
      </h2>
      <div className="ui segment rdm-sidebar bottom attached pl-0 pr-0 pt-0">
        <div className="versions">
          <div
            id="recordVersions"
            data-record={record}
            data-preview={isPreview}
          >
            <RecordVersionsList record={record} isPreview={isPreview} />
          </div>
        </div>
      </div>
    </div>
  );
};

const VersionsDropdownSection = ({ isPreview, record }) => {
  return (
    <div className="sidebar-container" id="record-versions">
      <RecordVersionsList
        record={record}
        isPreview={isPreview}
        widgetStyle="dropdown"
      />
    </div>
  );
};

export { VersionsListSection, VersionsDropdownSection };
