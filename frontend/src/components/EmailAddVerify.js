// variables starting with underscore can be unused
/* eslint no-unused-vars: ["error", { "argsIgnorePattern": "^_" }] */

import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import FormControl from '@material-ui/core/FormControl';
import FormGroup from '@material-ui/core/FormGroup';
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';
import Grid from '@material-ui/core/Grid';
import { TournesolAPI, formatError } from '../api';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    textAlign: 'center',
    justifyContent: 'center',
  },
  formControl: {
    margin: theme.spacing(3),
  },
}));

const getDefaultState = () => ({ email: '' });

export default () => {
  const [submitted, setSubmitted] = React.useState(false);
  const [submissionResult, setSubmissionResult] = React.useState('');
  const [submissionError, setSubmissionError] = React.useState('');
  const [state, setState] = React.useState(getDefaultState());

  const classes = useStyles();

  const handleSubmit = () => {
    const api = new TournesolAPI.UserInformationApi();
    api.userInformationAddVerifyEmailPartialUpdate(state.email, window.user_information_id,
      (err, _res) => {
        if (err) {
          setSubmissionError(formatError(err));
          setSubmissionResult(null);
        } else {
          setSubmissionError(null);
          setSubmissionResult('Your e-mail was added, please check your inbox! Note that the certification email might have ended up in your spam mailbox');
        }
      });
    setSubmitted(true);
  };

  return (
    <div className={classes.root}>
      <FormControl component="fieldset" className={classes.formControl}>
        <Grid
          container
          direction="row"
          justify="center"
          alignItems="center"
        >
          <Grid item>

            <FormGroup>
              <TextField
                className="alert_email_class"
                style={{ width: '90%' }}
                id="email"
                label="Add e-mail address"
                value={state.email}
                name="email"
                onChange={(e) => {
                  setState({ ...state, email: e.target.value });
                }}
              />
            </FormGroup>
          </Grid>

          <Grid item>

            <Button variant="contained" color="primary" onClick={handleSubmit} className="alert_email_add_submit">
              Submit
            </Button>

          </Grid>
        </Grid>

        {submitted && (
          <div>
            <br />
            {submitted && submissionResult && (
            <Alert variant="outlined" severity="info" id="id_add_email_success">
              {submissionResult}
            </Alert>)}
            {submitted && submissionError && <Alert variant="outlined" severity="error"> {submissionError} </Alert>}
          </div>
        )}
      </FormControl>

    </div>
  );
};
