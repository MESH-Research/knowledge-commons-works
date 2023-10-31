import React from "react";

const ContentWarning = ({ record }) => {
  const contentWarning = record.custom_fields["kcr:content_warning"];

  if (!contentWarning) {
    return null;
  }

  return (
    <div className="content-warning">
      <h2>Content Warning</h2>
      <p>{contentWarning}</p>
    </div>
  );
};

export { ContentWarning };
