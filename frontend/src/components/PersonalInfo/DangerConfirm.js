import Button from '@material-ui/core/Button';
import Dialog from '@material-ui/core/Dialog';
import DialogActions from '@material-ui/core/DialogActions';
import DialogContent from '@material-ui/core/DialogContent';
import DialogContentText from '@material-ui/core/DialogContentText';
import DialogTitle from '@material-ui/core/DialogTitle';
import React from 'react';
import Snackbar from '@material-ui/core/Snackbar';
import Alert from '@material-ui/lab/Alert';

function defaultCallback(f) {
  if (Math.random() > 0.5) {
    window.setTimeout(() => f(null, 'Everything was blown up'), 500);
  } else {
    window.setTimeout(() => f('SEGMENTATION FAULT :(', null), 500);
  }
}

export default ({
  buttonText = 'Dangerous action',
  explanation = 'This blows up everything, are you sure?',
  yesText = 'Yes',
  noText = 'Cancel',
  callback = defaultCallback,
}) => {
  const [open, setOpen] = React.useState(false);

  const [snackOpen, setSnackOpen] = React.useState(false);
  const [snackFailOpen, setSnackFailOpen] = React.useState(false);
  const [successMessage, setSuccessMessage] = React.useState('');
  const [errorMessage, setErrorMessage] = React.useState('');

  const handleClickOpen = () => {
    setOpen(true);
  };

  const handleClose = () => {
    setOpen(false);
  };

  const handleYes = () => {
    callback((errorStatus, successStatus) => {
      if (errorStatus) {
        setErrorMessage(errorStatus);
        setSnackFailOpen(true);
      }
      if (successStatus) {
        setSuccessMessage(successStatus);
        setSnackOpen(true);
      }
    });
    handleClose();
  };

  return (
    <div>
      <Button variant="outlined" color="primary" onClick={handleClickOpen}>
        {buttonText}
      </Button>
      <Dialog
        open={open}
        onClose={handleClose}
        aria-labelledby="alert-dialog-title"
        aria-describedby="alert-dialog-description"
      >
        <DialogTitle id="alert-dialog-title">{buttonText}</DialogTitle>
        <DialogContent>
          <DialogContentText id="alert-dialog-description">
            {explanation}
          </DialogContentText>
        </DialogContent>
        <DialogActions>
          <Button onClick={handleClose} color="secondary" autoFocus>
            {noText}
          </Button>
          <Button onClick={handleYes} color="primary">
            {yesText}
          </Button>
        </DialogActions>
      </Dialog>
      <Snackbar
        open={snackOpen}
        autoHideDuration={1000}
        onClose={() => setSnackOpen(false)}
      >
        <Alert severity="success">
          {successMessage}
        </Alert>
      </Snackbar>
      <Snackbar
        open={snackFailOpen}
        autoHideDuration={1000}
        onClose={() => setSnackFailOpen(false)}
      >
        <Alert severity="error">
          {errorMessage}
        </Alert>
      </Snackbar>
    </div>
  );
};
