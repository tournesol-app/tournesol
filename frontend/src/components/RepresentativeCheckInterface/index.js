import React, { useState } from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';
import { useHistory } from 'react-router-dom';

import VideoComments from '../VideoComments';
import { TournesolAPI } from '../../api';
import RepresentativeDisplay from './RepresentativeDisplay';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    justifyContent: 'center',
    overflow: 'hidden',
  },
  centered: {
    width: '750px',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    flex: '0 0 auto',
    textAlign: 'center',
  },
  comparisonContainer: {
    display: 'flex',
    flexDirection: 'row',
    margin: '8px',
    width: '750px',
    textAlign: 'center',
  },
  videoContainer: {
    position: 'relative',
    height: '140px',
    width: '250px',
    background: '#000',
    flex: 0,
  },
  sliderContainer: {
    display: 'flex',
    flexDirection: 'column',
    paddingTop: '32px',
    flex: 1,
    margin: '8px',
    justifyContent: 'center',
    alignItem: 'center',
  },
  floatLeft: {
    left: '-36px',
    position: 'absolute',
    top: '0px',
    display: 'flex',
    flexDirection: 'column',
  },
  floatRight: {
    right: '-42px',
    position: 'absolute',
    top: '0px',
    display: 'flex',
    flexDirection: 'column',
  },
  commentContainer: {
    display: 'flex',
    flexDirection: 'column',
    flex: '1 1 auto',
    border: '1px solid black',
    overflowY: 'auto',
    overflowX: 'hidden',
    padding: '4px',
    margin: '4px',
  },
}));

export default () => {
  const classes = useStyles();
  const history = useHistory();

  const [disagreements, setDisagreements] = useState(null);
  const [numDisagreements, setNumDisagreements] = useState(0);
  const [disagreementIndex, setDisagreementIndex] = useState(0);
  const [commentsLeftOpen, setCommentsLeftOpen] = useState(undefined);
  const [commentsRightOpen, setCommentsRightOpen] = useState(undefined);
  const [loading, setLoading] = useState(false);

  if (!disagreements && !loading) {
    setLoading(true);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.disagreements({}, (err, data) => {
      if (!err) {
        setDisagreements(data.results);
        setNumDisagreements(data.count);
      }
      setLoading(false);
    });
  }

  const disagreement = (disagreements !== null && disagreements.length > 0) ?
    disagreements[disagreementIndex] : null;

  return (
    <div className={classes.root} id="id_representative_interface_all">
      {!loading && <div id="id_representative_not_loading" />}
      {commentsLeftOpen && (
        <div className={classes.commentContainer}>
          <VideoComments videoId={commentsLeftOpen} />
        </div>
      )}
      <div className={classes.centered}>
        <Typography variant="h4">
          We found {numDisagreements} disagreement
          {numDisagreements < 2 ? '' : 's'} between you and the model
          constructed to represent your preferences
        </Typography>
        {(disagreements === null || disagreements.length === 0 ||
          disagreementIndex >= disagreements.length) && (
          <Button
            variant="contained"
            color="primary"
            style={{ margin: '16px' }}
            onClick={() => {
              history.push('/rate');
            }}
          >
            Rate Contents
          </Button>
        )}
        {disagreement && (
          <>
            <Typography paragraph>
              ({disagreementIndex + 1} / {disagreements.length})
            </Typography>
            <Typography paragraph>
              Disagreements comes from contradictory ratings that you gave to
              the contents. For each disagreement you can either update it or
              leave it the way it is. Update your rating only if you think the
              model is correct.
            </Typography>
            <RepresentativeDisplay
              disagreement={{ ...disagreement,
                modelScore: disagreement.model_score,
                expertScore: disagreement.rating_score,
                videoA: disagreement.video_1__video_id,
                videoB: disagreement.video_2__video_id }}
              next={() => setDisagreementIndex(disagreementIndex + 1)}
              commentsLeftOpen={commentsLeftOpen}
              setCommentsLeftOpen={setCommentsLeftOpen}
              commentsRightOpen={commentsRightOpen}
              setCommentsRightOpen={setCommentsRightOpen}
            />
            <Alert severity="warning" style={{ margin: '8px' }}>
              The models ratings are updated only on a daily basis. Come back to
              this page later to continue to make your rating more robust.
            </Alert>
          </>
        )}
      </div>
      {commentsRightOpen && (
        <div className={classes.commentContainer}>
          <VideoComments videoId={commentsRightOpen} />
        </div>
      )}
    </div>
  );
};
