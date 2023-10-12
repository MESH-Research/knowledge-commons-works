import React from 'react';
import { i18next } from '@translations/invenio_app_rdm/i18next';

const BadgesFormatsList = ({imageFilename, target, alternative='DOI'}) => {
  return (
    <>
    <h4> <small>{i18next.t("Markdown")}</small> </h4>
    <h4>
        <pre>[![{alternative}]({imageFilename})]({target})</pre>
    </h4>
    <h4>
        <small>{i18next.t("reStructedText")}</small>
    </h4>
    <h4>
        <pre>.. image:: {imageFilename}
   :target: {target}</pre>
    </h4>
    <h4>
        <small>{i18next.t("HTML")}</small>
    </h4>
    <h4>
      <pre>&lt;a href="{target}"&gt;&lt;img src="{imageFilename}" alt="{alternative}"&gt;&lt;/a&gt;</pre>
    </h4>

    <h4>
        <small>{i18next.t("Image URL")}</small>
    </h4>
    <h4>
      <pre>{imageFilename}</pre>
    </h4>

    <h4>
        <small>{i18next.t("Target URL")}</small>
    </h4>
    <h4>
      <pre>{target}</pre>
    </h4>
    </>
  );
};

export { BadgesFormatsList };
