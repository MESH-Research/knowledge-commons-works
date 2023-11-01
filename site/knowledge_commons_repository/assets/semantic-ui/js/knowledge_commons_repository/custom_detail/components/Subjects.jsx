import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Keywords } from "../components/Keywords";

function SubjectHeadings({
  passedClassNames,
  subjectHeadings,
  keywords,
  showKeywords,
}) {
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
      {!!showKeywords && keywords?.length && keywords[0] ? (
        <>
          <h3 className="ui header tiny mt-10">User-defined Keywords</h3>
          <Keywords
            passedClassNames="ui bottom attached segment rdm-sidebar pr-0 pt-0"
            keywords={keywords}
          />
        </>
      ) : (
        ""
      )}
    </div>
  );
}

export { SubjectHeadings };
