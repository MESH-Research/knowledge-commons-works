import PropTypes from "prop-types";
import React, { Component } from "react";
import { FieldLabel,
         GroupField,
         Input,
         Array,
         TextField,
} from "react-invenio-forms";
import { Grid, Form, Button, Icon } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import { FieldArray, useFormikContext } from "formik";

const newSeries = {
  series_title: "",
  series_volume: "",
};

const SeriesItem = ({index, fieldPathPrefix, series_title, series_volume, required, arrayHelpers}) => {
  console.log('series item *******');
  console.log(fieldPathPrefix);
  return(
  <GroupField key={index} inline>
    <TextField
      fieldPath={`${fieldPathPrefix}.series_title`}
      label={i18next.t(series_title.label)}
      required={required}
      width={14}
      placeholder={series_title.placeholder}
      description={series_title.description}
    />
    <TextField
      fieldPath={`${fieldPathPrefix}.series_volume`}
      label={i18next.t(series_volume.label)}
      required={required}
      width={4}
      placeholder={series_volume.placeholder}
      description={series_volume.description}
    />
    <Form.Field>
      <Button
        aria-label={i18next.t("Remove field")}
        className="close-btn"
        icon="close"
        onClick={() => arrayHelpers.remove(index)}
      />
    </Form.Field>
  </GroupField>
  )
}

const SeriesField = ({
      fieldPath, // injected by the custom field loader via the `field` config property
      series_title,
      series_volume,
      icon="list",
      description = "",
      required = false,
      label = i18next.t("Series"),
      showEmptyValue = true
    }) => {
    const { values, submitForm } = useFormikContext();

    return (
      <FieldArray
        name={fieldPath}
        className="invenio-array-field"
        showEmptyValue={showEmptyValue}
        render={arrayHelpers => (
          <>
            <Form.Field required={required}>
              <FieldLabel htmlFor={fieldPath} labelIcon={icon} label={label} />
            </Form.Field>
            {!!values.custom_fields['kcr:series'] && values.custom_fields['kcr:series'].length > 0 ? (
            values.custom_fields['kcr:series'].map(({my_title, my_volume}, index) => {
              const fieldPathPrefix = `${fieldPath}.${index}`;
              const hasNumber = (!!my_volume || my_volume!=="");
              return(
                <SeriesItem index={index}
                  key={index}
                  fieldPathPrefix={fieldPathPrefix}
                  series_title={series_title}
                  series_volume={series_volume}
                  required={required}
                  hasNumber={hasNumber}
                  arrayHelpers={arrayHelpers}
                />
            )}))
            : (!!showEmptyValue && (""
                // <SeriesItem index={-1}
                //   fieldPathPrefix={`${fieldPath}.0`}
                //   series_title={series_title}
                //   series_volume={series_volume}
                //   required={required}
                //   arrayHelpers={arrayHelpers}
                // />
            )
            )
            }
            {description && (
              <label className="helptext mb-0">{description}</label>
            )}
            <Button
              type="button"
              onClick={() => arrayHelpers.push(newSeries)}
              icon
              className="align-self-end"
              labelPosition="left"
            >
              <Icon name="add" />
              Add another series
            </Button>
          </>
        )}
      />
    )
}

SeriesField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  label: PropTypes.string,
  series_title: PropTypes.object,
  series_volume: PropTypes.object,
  required: PropTypes.bool,
  showEmptyValue: PropTypes.bool,
  icon: PropTypes.string,
  description: PropTypes.string,
  placeholder: PropTypes.string,
};

export { SeriesField };