import React, { } from 'react'
import { Button, Header, Icon, Modal } from "semantic-ui-react";

const NoFilesModal = ({handleCancel, handlePositive, open=false}) => {
  return (
    <Modal
    closeIcon
    open={open}
  //   trigger={<Button>Show Modal</Button>}
    onClose={() => setOpen(false)}
    onOpen={() => setOpen(true)}
  >
    <Header icon='archive' content='No files included' />
    <Modal.Content>
      <p>
        Are you sure you want to save this draft without any uploaded files?
      </p>
    </Modal.Content>
    <Modal.Actions>
      <Button color='red' onClick={handleCancel}>
        <Icon name='remove' /> No, let me add files
      </Button>
      <Button color='green' onClick={handlePositive}>
        <Icon name='checkmark' /> Yes, continue without files
      </Button>
    </Modal.Actions>
  </Modal>
)
}

export { NoFilesModal };