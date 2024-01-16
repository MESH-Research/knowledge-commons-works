// This file is part of Invenio-RDM-Records
// Copyright (C) 2020-2023 CERN.
// Copyright (C) 2020-2022 Northwestern University.
// Copyright (C) 2021 Graz University of Technology.
//
// Invenio-RDM-Records is free software; you can redistribute it and/or modify it
// under the terms of the MIT License; see LICENSE file for more details.

import React, { useState, useEffect } from "react";
import PropTypes from "prop-types";
import { Field, useFormikContext } from "formik";
import { object } from "yup";

import { FieldLabel } from "react-invenio-forms";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  Checkbox,
  Dropdown,
  Form,
  Label,
  Icon,
  Message,
} from "semantic-ui-react";

//   original helpText:
//     "In case your upload was already published elsewhere, please use the date of the first publication. Format: YYYY-MM-DD, YYYY-MM, or YYYY. For intervals use DATE/DATE, e.g. 1939/1945."

const DateDropdown = ({
  name,
  unit,
  value,
  options,
  position,
  useRange,
  fieldPath,
  handleDropdownChange,
  error,
}) => {
  return (
    <Form.Field>
      <FieldLabel
        htmlFor={`${fieldPath}.inputs.${name}`}
        label={`${useRange ? i18next.t(position) + " " : ""}${i18next.t(
          unit
        )}`}
        id={`${fieldPath}.${name}.label`}
      />
      <Dropdown
        search
        selection
        id={`${fieldPath}.inputs.${name}`}
        name={name}
        options={options}
        value={value}
        onChange={handleDropdownChange}
        error={error}
      />
    </Form.Field>
  );
};

const PublicationDateField = ({
  fieldPath,
  label = i18next.t("Publication Date"),
  labelIcon = "calendar",
  required = true,
}) => {
  const helpText =
    "If this work is already published elsewhere, please use the date of the first publication.";
  const { setFieldValue, values, touched, setFieldTouched } =
    useFormikContext();
  const currentDate = new Date();
  const currentYear = String(currentDate.getFullYear());
  const currentDay = String(currentDate.getDate()).padStart(2, "0");
  const currentMonth = String(currentDate.getMonth() + 1).padStart(2, "0"); // Months are 0-based in JavaScript
  const [yearValue, setYearValue] = useState(currentYear);
  const [monthValue, setMonthValue] = useState(currentMonth);
  const [dayValue, setDayValue] = useState(currentDay);
  const [endYearValue, setEndYearValue] = useState(null);
  const [endMonthValue, setEndMonthValue] = useState(null);
  const [endDayValue, setEndDayValue] = useState(null);
  const [dateValue, setDateValue] = useState(
    [yearValue, monthValue, dayValue].join("-")
  );
  const [useRange, setUseRange] = useState(false);

  useEffect(() => {
    const publicationDate = values.metadata.publication_date;
    if (publicationDate) {
      const setDates = (year, month, day) => {
        setYearValue(year ? year : null);
        setMonthValue(month ? month : null);
        setDayValue(day ? day : null);
      };
      if (publicationDate.includes("/")) {
        const [start, end] = publicationDate.split("/");
        const [startYear, startMonth, startDay] = start.split("-");
        const [endYear, endMonth, endDay] = end.split("-");
        setDates(startYear, startMonth, startDay);
        setEndDayValue(endDay);
        setEndMonthValue(endMonth);
        setEndYearValue(endYear);
      } else {
        const [year, month, day] = publicationDate.split("-");
        setDates(year, month, day);
      }
    }
  }, []);

  useEffect(() => {
    let newDateValue = [yearValue, monthValue, dayValue]
      .filter((v) => !!v)
      .join("-");
    if (!!endYearValue) {
      newDateValue +=
        "/" +
        [endYearValue, endMonthValue, endDayValue]
          .filter((v) => !!v)
          .join("-");
    }
    setDateValue(newDateValue);
    setFieldValue(fieldPath, newDateValue);
    setFieldTouched(fieldPath, true);
  }, [
    yearValue,
    monthValue,
    dayValue,
    endYearValue,
    endMonthValue,
    endDayValue,
  ]);

  useEffect(() => {
    if (!useRange) {
      setEndYearValue(null);
      setEndMonthValue(null);
      setEndDayValue(null);
    }
  }, [useRange]);

  const years = Array.from({ length: currentYear - 1600 + 1 }, (_, i) =>
    (1600 + i).toString()
  );
  let yearOptions = years
    .map((year) => {
      return { key: year, value: year, text: year };
    })
    .reverse();
  yearOptions.unshift({ key: "None", value: null, text: "None" });
  const monthOptions = [
    { key: "None", value: null, text: "None", days: 31 },
    { key: "January", value: "01", text: "January", days: 31 },
    { key: "February", value: "02", text: "February", days: 29 },
    { key: "March", value: "03", text: "March", days: 31 },
    { key: "April", value: "04", text: "April", days: 30 },
    { key: "May", value: "05", text: "May", days: 31 },
    { key: "June", value: "06", text: "June", days: 30 },
    { key: "July", value: "07", text: "July", days: 31 },
    { key: "August", value: "08", text: "August", days: 31 },
    { key: "September", value: "09", text: "September", days: 30 },
    { key: "October", value: "10", text: "October", days: 31 },
    { key: "November", value: "11", text: "November", days: 30 },
    { key: "December", value: "12", text: "December", days: 31 },
  ];
  const days = Array.from({ length: 31 }, (_, i) => (i + 1).toString());
  let dayOptions = days.map((day) => {
    return {
      key: day.padStart(2, "0"),
      value: day.padStart(2, "0"),
      text: day,
    };
  });
  dayOptions.unshift({ key: "None", value: null, text: "None" });
  const selectedMonth = monthOptions.find(
    (month) => month.value === monthValue
  );
  const daysInSelectedMonth = selectedMonth ? selectedMonth.days : 31;
  const slicedDayOptions = dayOptions.slice(0, daysInSelectedMonth + 1);

  const handleDropdownChange = (e, { name, value }) => {
    const setters = {
      startYear: setYearValue,
      startMonth: setMonthValue,
      startDay: setDayValue,
      endYear: setEndYearValue,
      endMonth: setEndMonthValue,
      endDay: setEndDayValue,
    };
    setters[name](value);
    if (name === "startDay" && !monthValue) {
      setMonthValue("01");
    }
    if (name === "endDay" && !endMonthValue) {
      setEndMonthValue("01");
    }
    if (name === "startMonth" && value === null) {
      setDayValue(null);
    }
    if (name === "endMonth" && value === null) {
      setEndDayValue(null);
    }
    if (name === "startYear" && value === null) {
      setMonthValue(null);
      setDayValue(null);
    }
    if (name === "endYear" && value === null) {
      setEndMonthValue(null);
      setEndDayValue(null);
    }
  };

  const startDropdowns = [
    {
      name: "startYear",
      unit: "Year",
      value: yearValue,
      options: yearOptions,
    },
    {
      name: "startMonth",
      unit: "Month",
      value: monthValue,
      options: monthOptions,
    },
    {
      name: "startDay",
      unit: "Day",
      value: dayValue,
      options: slicedDayOptions,
    },
  ];
  const endDropdowns = [
    {
      name: "endYear",
      unit: "Year",
      value: endYearValue,
      options: yearOptions,
    },
    {
      name: "endMonth",
      unit: "Month",
      value: endMonthValue,
      options: monthOptions,
    },
    {
      name: "endDay",
      unit: "Day",
      value: endDayValue,
      options: slicedDayOptions,
    },
  ];
  return (
    <>
      <Field name={fieldPath} id={fieldPath}>
        {({
          field, // { name, value, onChange, onBlur }
          form: { touched, errors }, // also values, setXXXX, handleXXXX, dirty, isValid, status, etc.
          meta,
        }) => (
          <Form.Field required={!!required} error={!!meta.error}>
            <FieldLabel
              htmlFor={fieldPath}
              icon={labelIcon}
              label={label}
              id={`${fieldPath}.label`}
            />
            <Form.Group>
              {startDropdowns.map((dropdown, idx) => (
                <DateDropdown
                  key={idx}
                  {...dropdown}
                  position={"Start"}
                  useRange={useRange}
                  fieldPath={fieldPath}
                  handleDropdownChange={handleDropdownChange}
                  error={!!meta.error}
                  aria-describedby={`${fieldPath}.help-text`}
                />
              ))}
              <div>
                <Checkbox
                  label={`${!useRange ? "add" : "include"} end date`}
                  id="metadata.publication_date.controls.useRange"
                  onChange={(e, data) => setUseRange(data.checked)}
                  checked={useRange}
                />
              </div>
            </Form.Group>
            {!!useRange && (
              <Form.Group>
                {endDropdowns.map((dropdown, idx) => (
                  <DateDropdown
                    key={idx}
                    {...dropdown}
                    position={"End"}
                    useRange={useRange}
                    fieldPath={fieldPath}
                    handleDropdownChange={handleDropdownChange}
                    error={!!meta.error}
                    aria-describedby={`${fieldPath}.help-text`}
                  />
                ))}
              </Form.Group>
            )}
            {meta.error && (
              <Label className="prompt error" pointing>
                {meta.error}
              </Label>
            )}
            {helpText && (
              <div id={`${fieldPath}.helptext`} className="helptext">
                {helpText}
              </div>
            )}
          </Form.Field>
        )}
      </Field>
    </>
  );
};

PublicationDateField.propTypes = {
  fieldPath: PropTypes.string.isRequired,
  helpText: PropTypes.string,
  label: PropTypes.string,
  labelIcon: PropTypes.string,
  placeholder: PropTypes.string,
  required: PropTypes.bool,
};

export { PublicationDateField };
