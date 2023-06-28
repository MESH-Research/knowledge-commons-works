import React, { useEffect } from "react";
import {
    Form
} from "semantic-ui-react";
import {
    useFormikContext
} from "formik";

const DepositFormComponent = ({ handleResourceTypeChange, children }) => {
    const { values, submitForm } = useFormikContext();

    useEffect(() => {
        'loaded form'
        console.log(values);
        handleResourceTypeChange(values.metadata.resource_type);
    }, [values, submitForm]);

    return(
        <Form>
        {children}
        </Form>
    )
}

export default DepositFormComponent;