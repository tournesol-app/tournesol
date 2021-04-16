import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { videoReportFields, videoReportFieldNames } from '../constants';
import { GET_REPORTS } from '../api';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
  },
  formControl: {
    margin: theme.spacing(3),
  },
}));

export default ({ videoId }) => {
  const [reports, setReports] = React.useState([]);
  const [loadedId, setLoadedId] = React.useState('');

  const classes = useStyles();

  const loadVideo = () => {
    if (videoId) {
      GET_REPORTS(videoId, (r) => {
        setReports(r);
        setLoadedId(videoId);
        return null;
      });
    }
    return null;
  };

  if (loadedId !== videoId) {
    loadVideo();
  }

  return (
    <div className={classes.root}>
      {reports.length && <p>Video Reports: {reports.length}</p>}
      <br />
      <ul>
        {reports.map((r) => (
          <li className="video_report_one_item">
            <span>{videoReportFields.map((f) => {
              if (r[f]) {
                return `${videoReportFieldNames[f]}. `;
              }

              return null;
            })}
            </span>
            Explanation: {r.explanation}
          </li>))}
      </ul>
    </div>
  );
};
