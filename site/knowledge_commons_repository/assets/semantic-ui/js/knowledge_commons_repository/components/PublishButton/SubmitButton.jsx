import { i18next } from "@translations/invenio_rdm_records/i18next";
import React, { useState, useContext } from "react";
// import { Trans } from "react-i18next";
import { connect } from "react-redux";
import { useFormikContext } from "formik";
import {
  DepositFormSubmitActions,
  DepositFormSubmitContext,
} from "@js/invenio_rdm_records";
// import { DepositStatus } from "../../state/reducers/deposit";
import { Button, Header, Icon, Message, Modal } from "semantic-ui-react";
import _omit from "lodash/omit";
import PropTypes from "prop-types";
import { SubmitReviewModal } from "./SubmitReviewModal";

const DRAFT_PREVIEW_STARTED = "DRAFT_PREVIEW_STARTED";
const DRAFT_SAVE_STARTED = "DRAFT_SAVE_STARTED";
const DRAFT_PUBLISH_STARTED = "DRAFT_PUBLISH_STARTED";
const DRAFT_SUBMIT_REVIEW_STARTED = "DRAFT_SUBMIT_REVIEW_STARTED";

class DepositStatus {
  static DRAFT = "draft";
  static NEW_VERSION_DRAFT = "new_version_draft";
  static DRAFT_WITH_REVIEW = "draft_with_review";
  static IN_REVIEW = "in_review";
  static DECLINED = "declined";
  static EXPIRED = "expired";
  static PUBLISHED = "published";

  static allowsReviewDeletionStates = [
    DepositStatus.DRAFT_WITH_REVIEW,
    DepositStatus.DECLINED,
    DepositStatus.EXPIRED,
  ];

  static allowsReviewUpdateStates = [
    DepositStatus.DRAFT_WITH_REVIEW,
    DepositStatus.DECLINED,
    DepositStatus.EXPIRED,
    DepositStatus.DRAFT,
  ];

  static disallowsSubmitForReviewStates = [
    DepositStatus.PUBLISHED,
    DepositStatus.IN_REVIEW,
    DepositStatus.NEW_VERSION_DRAFT,
  ];
}

const SubmitButtonComponent = ({actionName,
                       actionState=undefined,
                       actionStateExtra,
                       record,
                       publishWithoutCommunity,
                       numberOfFiles=undefined,
                       publishModalExtraContent=undefined,
                       handleConfirmNoFiles,
                       handleConfirmNeedsFiles,
                       sanitizeDataForSaving,
                       missingFiles,
                       community=undefined,
                       changeSelectedCommunityFn,
                       showChangeCommunityButton,
                       showDirectPublishButton,
                       showSubmitForReviewButton,
                       disableSubmitForReviewButton=undefined,
                       isRecordSubmittedForReview,
                       ...ui
                      }) => {

  const { values, handleSubmit, isSubmitting } = useFormikContext();
  const { setSubmitContext } = useContext(DepositFormSubmitContext);
  const [ noFilesOpen, setNoFilesOpen ] = useState(false);
  const [ publishConfirmOpen, setPublishConfirmOpen ] = useState(false);
  const uiProps = _omit(ui, ["dispatch"]);

  const handleNoFilesOpen = () => setNoFilesOpen(true);
  const handlePublishConfirmOpen = () => setPublishConfirmOpen(true);

  const handleNoFilesCancel = () => {
    if ( missingFiles ) {
        handleConfirmNeedsFiles();
    }
    setNoFilesOpen(false);
  };
  const handlePublishConfirmCancel = () => {
    setPublishConfirmOpen(false);
    setNoFilesOpen(false);
  };

  const actions = {
    preview: {
      name: "preview",
      buttonLabel: i18next.t("Preview"),
      actionText: i18next.t("preview this deposit"),
      icon: "eye",
      action: [DepositFormSubmitActions.PREVIEW],
      newActionState: DRAFT_PREVIEW_STARTED,
    },
    saveDraft: {
      name: "save",
      buttonLabel: i18next.t("Save draft"),
      actionText: i18next.t("save this draft"),
      icon: "save",
      action: [DepositFormSubmitActions.SAVE],
      newActionState: DRAFT_SAVE_STARTED,
    },
    publish: {
      name: "publish",
      buttonLabel: i18next.t("Publish"),
      actionText: i18next.t("publish this deposit"),
      icon: "upload",
      action: [publishWithoutCommunity
        ? DepositFormSubmitActions.PUBLISH_WITHOUT_COMMUNITY
        : DepositFormSubmitActions.PUBLISH],
      newActionState: DRAFT_PUBLISH_STARTED,
    },
    submitForReview: {
      name: "SubmitReview",
      buttonLabel: isRecordSubmittedForReview
        ? i18next.t("Submitted for review")
        : i18next.t("Submit for review"),
      actionText: i18next.t("submit this deposit for community review"),
      icon: "upload",
      action: [DepositFormSubmitActions.SUBMIT_REVIEW, {
        reviewComment: actionStateExtra.reviewComment,
        directPublish: showDirectPublishButton,
      }],
      newActionState: DRAFT_SUBMIT_REVIEW_STARTED,
    },
    directPublish: {
      name: "SubmitReview",
      buttonLabel: i18next.t("Publish to community"),
      actionText: i18next.t("publish this deposit"),
      icon: "upload",
      action: [DepositFormSubmitActions.SUBMIT_REVIEW, {
        reviewComment: actionStateExtra.reviewComment,
        directPublish: showDirectPublishButton,
      }],
      newActionState: DRAFT_SUBMIT_REVIEW_STARTED,
    },
  }

  let currentActionName = actionName;
  if ( actionName==="publish" && showSubmitForReviewButton ) {
    currentActionName = !showDirectPublishButton ? "submitForReview" : "directPublish";
  }

  const { name, buttonLabel, actionText, icon, action, newActionState
  } = actions[currentActionName];

  const handleSaveOrSubmit = (event) => {
    sanitizeDataForSaving().then(handleConfirmNoFiles()).then(() => {
      setSubmitContext(...action);
      handleSubmit(event);
      setNoFilesOpen(false);
      setPublishConfirmOpen(false);
    });
  }

  // const handlePublishOrSubmit = (event) => {
  //   sanitizeDataForSaving().then(handleConfirmNoFiles()).then(() => {
  //     setSubmitContext(...action);
  //     handleSubmit(event);
  //     setNoFilesOpen(false);
  //     setPublishConfirmOpen(false);
  //   });
  // };

  // const handleSubmitReview = () => {
  //   setSubmitContext(...action);
  //   handleSubmit();
  //   setPublishConfirmOpen(false);
  // }

  const handlePositiveNoFiles = (event) => {
    if ( actionName==="publish" ) {
      setNoFilesOpen(false);
      handlePublishConfirmOpen();
    } else {
      handleSaveOrSubmit(event);
    }
  };

  return (
    <>
    <Button
      name={name}
      disabled={isSubmitting || (actionName==="publish" && disableSubmitForReviewButton)}
      onClick={missingFiles ? handleNoFilesOpen : handlePositiveNoFiles}
      loading={isSubmitting && actionState === newActionState}
      icon={icon}
      labelPosition="left"
      content={buttonLabel}
      type={(missingFiles || showSubmitForReviewButton) ? "button" : "submit"}
      // positive={showDirectPublishButton}
      // primary={!showDirectPublishButton}
      {...uiProps}
    />

    {/* Modal to confirm submission with no files */}
    <Modal
      closeIcon
      open={noFilesOpen}
    //   trigger={<Button>Show Modal</Button>}
      onClose={() => setNoFilesOpen(false)}
      onOpen={() => setNoFilesOpen(true)}
    >
      <Header icon='archive' content='No files included' />
      <Modal.Content>
        <p>
          {i18next.t("Are you sure you want to {{actionText}} without any uploaded files?", {actionText: actionText})}
        </p>
      </Modal.Content>
      <Modal.Actions>
        <Button negative onClick={handleNoFilesCancel}>
          <Icon name='remove' /> No, let me add files
        </Button>
        <Button positive onClick={handlePositiveNoFiles}>
          <Icon name='checkmark' /> Yes, continue without files
        </Button>
      </Modal.Actions>
    </Modal>

    {/* Modal to confirm publishing */}
    <Modal
      open={publishConfirmOpen && !showSubmitForReviewButton}
      size="small"
      closeIcon
      closeOnDimmerClick={false}
      onClose={() => setPublishConfirmOpen(false)}
      onOpen={() => setPublishConfirmOpen(true)}
    >
      <Modal.Header>
        {i18next.t("Are you sure you want to {{actionText}}?", {actionText: actionText})}
      </Modal.Header>
      {/* the modal text should only ever come from backend configuration */}
      <Modal.Content>
        <Message visible
         warning
         icon
        >
          <p>
            <Icon name="warning sign" />{" "}
            {i18next.t(
              "Once the deposit is published you cannot change or add attached files! (You can still update the published record's other information.)"
            )}
          </p>
        </Message>
        {publishModalExtraContent && (
          <div dangerouslySetInnerHTML={{ __html: publishModalExtraContent }} />
        )}
      </Modal.Content>
      <Modal.Actions>
        <Button onClick={handlePublishConfirmCancel} floated="left"
          negative
        >
          <Icon name='remove' /> {i18next.t("Cancel")}
        </Button>
        <Button
          onClick={handleSaveOrSubmit}
          positive
          icon="upload"
          content={buttonLabel}
        />
      </Modal.Actions>
    </Modal>

    {/* modal to confirm submitting to community */}
    {showSubmitForReviewButton && (
      <SubmitReviewModal
        isConfirmModalOpen={publishConfirmOpen && showSubmitForReviewButton}
        initialReviewComment={actionStateExtra.reviewComment}
        onSubmit={handleSaveOrSubmit}
        community={community}
        onClose={handlePublishConfirmCancel}
        publishModalExtraContent={publishModalExtraContent}
        directPublish={showDirectPublishButton}
      />
    )
    }
    </>
)
}

SubmitButtonComponent.propTypes = {
  actionState: PropTypes.string,
  actionStateExtra: PropTypes.object,
  publishWithoutCommunity: PropTypes.bool,
  numberOfFiles: PropTypes.number.isRequired,
  publishModalExtraContent: PropTypes.string,
  changeSelectedCommunityFn: PropTypes.func.isRequired,
  showChangeCommunityButton: PropTypes.bool.isRequired,
  showDirectPublishButton: PropTypes.bool.isRequired,
  showSubmitForReviewButton: PropTypes.bool.isRequired,
  disableSubmitForReviewButton: PropTypes.bool,
  isRecordSubmittedForReview: PropTypes.bool.isRequired,
};

const mapStateToProps = (state) => ({
  actionState: state.deposit.actionState,
  actionStateExtra: state.deposit.actionStateExtra,
  record: state.deposit.record,
  numberOfFiles: Object.values(state.files.entries).length,
  publishModalExtraContent: state.deposit.config.publish_modal_extra,
  community: state.deposit.editorState.selectedCommunity,
  showDirectPublishButton: state.deposit.editorState.ui.showDirectPublishButton,
  showChangeCommunityButton: state.deposit.editorState.ui.showChangeCommunityButton,
  showSubmitForReviewButton: state.deposit.editorState.ui.showSubmitForReviewButton,
  disableSubmitForReviewButton:
    state.deposit.editorState.ui.disableSubmitForReviewButton,
  isRecordSubmittedForReview: state.deposit.record.status === DepositStatus.IN_REVIEW,
});

const mapDispatchToProps = (dispatch) => ({
  changeSelectedCommunityFn: (community) =>
    dispatch(changeSelectedCommunity(community)),
});

export const SubmitButtonModal = connect(
  mapStateToProps,
  mapDispatchToProps
)(SubmitButtonComponent);