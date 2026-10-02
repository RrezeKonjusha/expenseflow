import ConfirmDialog from './ConfirmDialog';

export default {
  title: 'Components/ConfirmDialog',
  component: ConfirmDialog,
  parameters: { layout: 'fullscreen' },
  args: { open: true, onConfirm: () => {}, onClose: () => {} },
};

export const Default = {
  args: {
    title: 'Submit expense?',
    message: 'Your manager will be asked to approve it.',
    confirmLabel: 'Submit',
  },
};

/** Destructive action: the confirm button is red. */
export const Destructive = {
  args: {
    title: 'Delete draft?',
    message: 'The draft and its details are removed. This cannot be undone.',
    confirmLabel: 'Delete',
    color: 'error',
  },
};

/** While the request runs, the confirm button is disabled so it cannot be sent twice. */
export const Loading = {
  args: {
    title: 'Deactivate user?',
    message: 'They can no longer sign in.',
    confirmLabel: 'Deactivate',
    color: 'error',
    busy: true,
  },
};
