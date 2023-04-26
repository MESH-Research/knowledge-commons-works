import React from "react";
import { Button, Form } from "semantic-ui-react";

const GuidesForm = () => {
    return(
        <Form>
            <span>Hello world</span>
            <Form.Input label="Name" />
            <Form.TextArea label="Message" placeholder="Write your message here" />
            <Button type="submit" role="button">Submit</Button>
        </Form>
    )
}

function sum(a, b) {
  return a + b;
}

export {
  sum
}
export default GuidesForm;