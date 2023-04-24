import React from "react";
import ReactDOM from "react-dom";
import { Button, Form } from "semantic-ui-react";

const rootContainer = document.getElementById("root-container");

ReactDOM.render(
  <Form>
    <Form.Input label="Name" />
    <Form.TextArea label="Message" placeholder="Write your message here" />
    <Button type="submit">Submit</Button>
  </Form>,
  rootContainer // Target container on where to render the React components.
);