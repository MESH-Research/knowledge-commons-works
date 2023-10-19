import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";

function SubjectHeadings({ passedClassNames, subjectHeadings }) {
  return (
    <div className={`record-subjects ui ${passedClassNames}`}>
      {subjectHeadings.map(({ id, scheme, subject }) => (
        <ul className="ui horizontal list no-bullets subjects" key={id}>
          <li className="item">
            <a
              href={`/search?q=metadata.subjects.id:"${id}"`}
              className="subject"
              title={i18next.t("Search results for ") + subject}
            >
              {subject}
            </a>
          </li>
        </ul>
      ))}
    </div>
  );
}

export { SubjectHeadings };
