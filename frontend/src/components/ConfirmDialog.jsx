import { Button, Dialog, DialogActions, DialogContent, DialogContentText, DialogTitle } from '@mui/material';

export default function ConfirmDialog({
  open,
  title,
  message,
  confirmLabel = 'Confirm',
  color = 'primary',
  onConfirm,
  onClose,
  busy,
}) {
  return (
    <Dialog open={open} onClose={onClose} maxWidth="xs" fullWidth>
      <DialogTitle>{title}</DialogTitle>
      <DialogContent>
        <DialogContentText>{message}</DialogContentText>
      </DialogContent>
      <DialogActions>
        <Button onClick={onClose}>Cancel</Button>
        <Button variant="contained" color={color} onClick={onConfirm} disabled={busy} data-cy="confirm">
          {confirmLabel}
        </Button>
      </DialogActions>
    </Dialog>
  );
}
