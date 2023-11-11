import React from "react";

const FlagNewerVersion = ({ isPublished, isLatest, latestHtml }) => {
  if (isPublished && !isLatest) {
    return (
      <Message warning icon>
        <Icon name="exclamation circle" size="large" />
        <Message.Content>
          There is a{" "}
          <a href={latestHtml}>
            <b>newer version</b>
          </a>{" "}
          of this work.
        </Message.Content>
      </Message>
    );
  } else {
    return null;
  }
};

export { FlagNewerVersion };
