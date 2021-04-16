import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import TextField from '@material-ui/core/TextField';
import FormLabel from '@material-ui/core/FormLabel';
import FormControl from '@material-ui/core/FormControl';
import FormGroup from '@material-ui/core/FormGroup';
import FormControlLabel from '@material-ui/core/FormControlLabel';
import Checkbox from '@material-ui/core/Checkbox';
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';
import { videoReportFields, videoReportFieldNames } from '../constants';
import { REPORT_VIDEO, TournesolAPI, formatError } from '../api';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  formControl: {
    margin: theme.spacing(3),
  },
}));

const getDefaultState = () => {
  const p = { explanation: '' };
  videoReportFields.forEach((f) => {
    p[f] = false;
  });
  return p;
};

export default ({ videoId }) => {
  const [submitted, setSubmitted] = React.useState(false);
  const [submissionResult, setSubmissionResult] = React.useState('');
  const [submissionError, setSubmissionError] = React.useState('');
  const [state, setState] = React.useState(getDefaultState());
  const [requested, setRequested] = React.useState(false);
  const [editing, setEditing] = React.useState(false);

  const loadData = () => {
    setRequested(true);
    const api = new TournesolAPI.VideoReportsApi();
    api.videoReportsList({ onlyMine: true, videoVideoId: videoId }, (err, data) => {
      if (!err && data.results.length === 1) {
        setState(data.results[0]);
        setEditing(true);
      }
    });
  };

  if (!requested) {
    loadData();
  }

  const classes = useStyles();

  const handleChange = (event) => {
    setState({ ...state, [event.target.name]: event.target.checked });
  };

  const handleSubmit = () => {
    if (editing) {
      const api = new TournesolAPI.VideoReportsApi();
      api.videoReportsPartialUpdate(state.id,
        { patchedVideoReportsSerializerV2:
          TournesolAPI.PatchedVideoReportsSerializerV2.constructFromObject(state) },
        (err, data) => {
          if (err) {
            setSubmissionError(formatError(err));
            setSubmissionResult(null);
          } else {
            setSubmissionError(null);
            setSubmissionResult(JSON.stringify(data));
          }
        });
    } else {
      REPORT_VIDEO(videoId, state, (data) => {
        setSubmissionResult(JSON.stringify(data));
        setSubmissionError(null);
      }, (err) => {
        setSubmissionError(err);
        setSubmissionResult(null);
      });
    }
    setSubmitted(true);
  };

  return (
    <div className={classes.root}>
      <FormControl component="fieldset" className={classes.formControl}>
        <FormLabel component="legend">What is wrong?</FormLabel>
        <FormGroup>
          {videoReportFields.map((key) => (
            <FormControlLabel
              control={
                <Checkbox
                  className={`report_${key}_checkbox`}
                  checked={state[key]}
                  onChange={handleChange}
                  name={key}
                />
              }
              label={videoReportFieldNames[key]}
            />
          ))}
        </FormGroup>
        <FormGroup>
          <TextField
            className="report_explanation"
            style={{ width: '90%' }}
            id="explanation"
            label="Explanation: why do you think so?"
            multiline
            rows={4}
            value={state.explanation}
            name="explanation"
            onChange={(e) => {
              setState({ ...state, explanation: e.target.value });
            }}
          />
        </FormGroup>
        <br />
        {submitted && submissionResult && (
        <Alert variant="outlined" severity="info" id="id_report_submission_ok">
          {submissionResult}
        </Alert>)}
        {submitted && submissionError && <Alert variant="outlined" severity="error"> {submissionError} </Alert>}

        <Button variant="contained" color="primary" onClick={handleSubmit} className="report_submit">
          Submit
        </Button>
      </FormControl>
    </div>
  );
};
