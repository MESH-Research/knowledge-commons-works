import PropTypes from "prop-types";
import React, { useEffect, useState } from "react";
import {
  FieldLabel,
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

const BookSeriesField = ({
  fieldPath, // injected by the custom field loader via the `field` config property
  series_title,
  series_volume,
  icon = "list",
  description = "",
  required = false,
  label = "",
  showEmptyValue = true,
  addButtonLabel = "Add new series",
}) => {
  const { values, setFieldValue } = useFormikContext();
  const [seriesLength, setSeriesLength] = useState(0);
  const [haveChangedNumber, setHaveChangedNumber] = useState(false);

  useEffect(() => {
    if (!!haveChangedNumber) {
      if (seriesLength < 0) {
        // console.log(document.getElementById(`${fieldPath}.add-button`));
        document.getElementById(`${fieldPath}.add-button`)?.focus();
      } else {
        document
          .getElementById(`${fieldPath}.${seriesLength}.series_title`)
          ?.focus();
        // console.log(document.getElementById(`${fieldPath}.${seriesLength}.series_title`));
      }
    }
  }, [seriesLength]);

  useEffect(() => {
    if (
      showEmptyValue === true &&
      (!values.custom_fields || !values.custom_fields["kcr:book_series"])
    ) {
      setFieldValue(fieldPath, [newSeries]);
    }
  });

  const handleAddNew = (arrayHelpers, newItem) => {
    console.log(arrayHelpers);
    setHaveChangedNumber(true);
    arrayHelpers.push(newItem);
    setSeriesLength(seriesLength + 1);
  };

  const handleRemove = (arrayHelpers, index) => {
    setHaveChangedNumber(true);
    arrayHelpers.remove(index);
    setSeriesLength(seriesLength - 1);
  };

  return (
    <FieldArray
      name={fieldPath}
      className="invenio-array-field"
      // showEmptyValue={showEmptyValue}
      // addButtonLabel={addButtonLabel}
      defaultNewValue={newSeries}
      // description={description}
      // icon={icon}
      // label={""}
      render={(arrayHelpers) => (
        <>
          {/* <Form.Field required={required}>
              <FieldLabel htmlFor={fieldPath} icon={labelIcon} label={label} />
            </Form.Field> */}

          {!!values.custom_fields
            ? values.custom_fields["kcr:book_series"]?.map(
                ({ title, volume }, index) => {
                  const fieldPathPrefix = `${fieldPath}.${index}`;
                  // const hasNumber = (!!my_volume || my_volume!=="");
                  return (
                    <Form.Group key={index}>
                      <TextField
                        fieldPath={`${fieldPathPrefix}.series_title`}
                        id={`${fieldPathPrefix}.series_title`}
                        label={
                          <label>
                            <Icon name={icon} />
                            {i18next.t(series_title.label)}
                          </label>
                        }
                        required={required}
                        placeholder={series_title.placeholder}
                        description={series_title.description}
                        width={11}
                      />
                      <TextField
                        fieldPath={`${fieldPathPrefix}.series_volume`}
                        id={`${fieldPathPrefix}.series_title`}
                        label={i18next.t(series_volume.label)}
                        required={required}
                        placeholder={series_volume.placeholder}
                        description={series_volume.description}
                        width={4}
                      />
                      <Form.Field>
                        <Button
                          aria-label={i18next.t("Remove field")}
                          className="close-btn"
                          icon="close"
                          onClick={() => handleRemove(arrayHelpers, index)}
                          type="button"
                          width={2}
                        />
                      </Form.Field>
                    </Form.Group>
                  );
                }
              )
            : ""}
          <Button
            type="button"
            onClick={() => handleAddNew(arrayHelpers, newSeries)}
            icon
            className="align-self-end add-button"
            labelPosition="left"
            id={`${fieldPath}.add-button`}
          >
            <Icon name="add" />
            {addButtonLabel}
          </Button>
        </>
      )}
    />
  );
};

BookSeriesField.propTypes = {
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

export { BookSeriesField };
