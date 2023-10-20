import React from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { SubjectHeadings } from "../components/Subjects";

function DetailMainSubjectsSection({ record, showKeywords = true }) {
  const subjects = record.metadata.subjects;

  const subjectHeadings = subjects?.filter((subject) => !!subject.scheme);
  const subjectLabels = subjectHeadings?.map(({ subject }) =>
    subject.toLowerCase()
  );

  const keywords = subjects
    ?.filter((subject) => !subject.scheme)
    .map(({ subject }) => subject)
    .concat(record.custom_fields["kcr:user_defined_tags"])
    .filter((keyword) => !subjectLabels.includes(keyword.toLowerCase()));
  // const groupedSubjects = subjectHeadings?.reduce((groups, subject) => {
  //   if (!groups[subject.scheme]) {
  //     groups[subject.scheme] = [];
  //   }
  //   groups[subject.scheme].push(subject);
  //   return groups;
  // }, {});

  return (
    <>
      {subjectHeadings?.length ? (
        <div
          id="subjects"
          className=""
          aria-label={i18next.t("Record subject headings")}
        >
          <h3 className="ui tiny header">{i18next.t("Subjects")}</h3>
          <SubjectHeadings
            passedClassNames="ui "
            subjectHeadings={subjectHeadings}
            keywords={keywords}
            showKeywords={showKeywords}
          />
        </div>
      ) : (
        ""
      )}
    </>
  );
}

export { DetailMainSubjectsSection };
