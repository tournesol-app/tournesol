import React from 'react';

import Typography from '@material-ui/core/Typography';
import TextField from '@material-ui/core/TextField';
import Button from '@material-ui/core/Button';

import { SUBMIT_VIDEO } from '../api';

export default () => {
  const [url, setUrl] = React.useState('');
  const [submitted, setSubmitted] = React.useState(false);
  const [submissionResult, setSubmissionResult] = React.useState('');

  const handleSubmit = () => {
    setSubmitted(true);
    setSubmissionResult('Result: ');
    SUBMIT_VIDEO(url,
      (data) => { setSubmissionResult(`${submissionResult}\n${JSON.stringify(data)}`); },
      (error) => { setSubmissionResult(`${submissionResult}\n${JSON.stringify(error)}`); });
    setUrl('');
  };

  return (
    <>
      <Typography variant="h3" noWrap>
        Submit Content
      </Typography>
      <Typography paragraph>
        Contribute content to be compared by experts. Submit URL of youtube
        videos below
      </Typography>
      <TextField
        id="outlined-basic"
        label="Youtube Video URL"
        variant="outlined"
        value={url}
        onChange={(e) => setUrl(e.target.value)}
      />
      <br />
      <Button variant="contained" color="primary" onClick={handleSubmit}>
        Submit
      </Button>
      {submitted && (
        <Typography paragraph>Thank you for your submission !</Typography>
      )}

      {
        submitted
        && (
        <pre>
          {' '}
          {submissionResult}
          {' '}
        </pre>
        )
    }
    </>
  );
};
