import React, { useState } from "react";
import { i18next } from "@translations/invenio_app_rdm/i18next";
import { Button } from "semantic-ui-react";

const Descriptions = ({
  description,
  additional_descriptions,
  hasFiles,
  permissions,
}) => {
  const [open, setOpen] = useState(false);
  return (
    <>
      {description && (
        <>
          <h2 id="description-heading">{i18next.t("Description")}</h2>
          {description.length > 240 &&
          hasFiles &&
          permissions?.can_read_files ? (
            <>
              <p>
                {open ? (
                  description
                ) : (
                  <>
                    {`${description.substring(0, 240)}`}&hellip;&nbsp;&nbsp;
                    <a
                      as="a"
                      onClick={() => setOpen(!open)}
                      href="#description-heading"
                      size="tiny"
                      className="show-more"
                    >
                      Show more
                    </a>
                  </>
                )}
              </p>
            </>
          ) : (
            <p>{description}</p>
          )}
          {additional_descriptions &&
            open &&
            additional_descriptions.map((add_description, idx) => (
              <section
                id={`additional-description-${idx}`}
                key={`additional-description-${idx}`}
                className="rel-mt-2"
                aria-label={i18next.t(add_description.type.title_l10n)}
              >
                <h2>
                  {i18next.t(add_description.type.title_l10n)}
                  <span className="text-muted language">
                    {add_description.lang
                      ? `(${add_description.lang.title_l10n})`
                      : ""}
                  </span>
                </h2>
                <p>{add_description.description}</p>
              </section>
            ))}
          {open && (
            <Button
              onClick={() => setOpen(!open)}
              size="tiny"
              className="show-less"
            >
              Show less
            </Button>
          )}
        </>
      )}
    </>
  );
};

export { Descriptions };
