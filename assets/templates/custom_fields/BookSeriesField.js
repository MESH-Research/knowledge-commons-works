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
  <Grid key={index} inline>
    <Input
      fieldPath={`${fieldPathPrefix}.series_title`}
      label={i18next.t(series_title.label)}
      required={required}
      width={14}
      placeholder={series_title.placeholder}
      description={series_title.description}
    />
    <Input
      fieldPath={`${fieldPathPrefix}.series_volume`}
      label={i18next.t(series_volume.label)}
      required={required}
      width={4}
      placeholder={series_volume.placeholder}
      description={series_volume.description}
    />
    <Form.Field style={{ marginTop: "1.75rem", float: "right" }}>
      <Button
        aria-label={i18next.t("Remove field")}
        className="close-btn"
        icon="close"
        onClick={() => arrayHelpers.remove(index)}
        type="button"
      />
    </Form.Field>
  </Grid>
  )
}

const BookSeriesField = ({
      fieldPath, // injected by the custom field loader via the `field` config property
      series_title,
      series_volume,
      icon="list",
      description = "",
      required = false,
      label = i18next.t("Series"),
      showEmptyValue = true,
      addButtonLabel = "Add new series"
    }) => {
    const { values, submitForm } = useFormikContext();
    console.log(`working?????????${fieldPath}`);
    return (
      <Array
        fieldPath={fieldPath}
        // className="invenio-array-field"
        showEmptyValue={showEmptyValue}
        addButtonLabel={addButtonLabel}
        defaultNewValue={newSeries}
        description={description}
        icon={icon}
      >
        {/* <Form.Field required={required}>
          <FieldLabel htmlFor={fieldPath} labelIcon={icon} label={label} />
        </Form.Field> */}
        {({arrayHelpers, indexPath, arrayPath}) => {
              const fieldPathPrefix = `${arrayPath}.${indexPath}`;

              console.log(`working?????????${fieldPathPrefix}`);
              // const hasNumber = (!!my_volume || my_volume!=="");
              return(
                <Grid inline>
                  <Input
                    fieldPath={`${fieldPathPrefix}.series_title`}
                    label={i18next.t(series_title.label)}
                    required={required}
                    width={14}
                    placeholder={series_title.placeholder}
                    description={series_title.description}
                  />
                  <Input
                    fieldPath={`${fieldPathPrefix}.series_volume`}
                    label={i18next.t(series_volume.label)}
                    required={required}
                    width={4}
                    placeholder={series_volume.placeholder}
                    description={series_volume.description}
                  />
                  <Form.Field style={{ marginTop: "1.75rem", float: "right" }}>
                    <Button
                      aria-label={i18next.t("Remove field")}
                      className="close-btn"
                      icon="close"
                      onClick={() => arrayHelpers.remove(indexPath)}
                      type="button"
                    />
                  </Form.Field>
                </Grid>

                // <Grid key={index} inline>
                //   <Input
                //     fieldPath={`${fieldPathPrefix}.series_title`}
                //     label={i18next.t(series_title.label)}
                //     required={required}
                //     width={14}
                //     placeholder={series_title.placeholder}
                //     description={series_title.description}
                //   />
                //   <Input
                //     fieldPath={`${fieldPathPrefix}.series_volume`}
                //     label={i18next.t(series_volume.label)}
                //     required={required}
                //     width={4}
                //     placeholder={series_volume.placeholder}
                //     description={series_volume.description}
                //   />
                //   <Form.Field style={{ marginTop: "1.75rem", float: "right" }}>
                //     <Button
                //       aria-label={i18next.t("Remove field")}
                //       className="close-btn"
                //       icon="close"
                //       onClick={() => arrayHelpers.remove(index)}
                //       type="button"
                //     />
                //   </Form.Field>
                // </Grid>

                // <SeriesItem index={indexPath}
                //   key={indexPath}
                //   fieldPathPrefix={fieldPathPrefix}
                //   series_title={series_title}
                //   series_volume={series_volume}
                //   required={required}
                //   // hasNumber={hasNumber}
                //   arrayHelpers={arrayHelpers}
                // />

            )}}
            {/* : (!!showEmptyValue && ("" */}
                {/* // <SeriesItem index={-1} */}
                {/* //   fieldPathPrefix={`${fieldPath}.0`}
                //   series_title={series_title}
                //   series_volume={series_volume}
                //   required={required}
                //   arrayHelpers={arrayHelpers}
                // /> */}
            {/* {description && (
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
        )} */}
      </Array>
    )
}

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