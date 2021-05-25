import React from 'react';

import Grid from '@material-ui/core/Grid';
import IconButton from '@material-ui/core/IconButton';
import Typography from '@material-ui/core/Typography';
import SkipPreviousIcon from '@material-ui/icons/SkipPrevious';
import SkipNextIcon from '@material-ui/icons/SkipNext';

import ExpertInterface from '../ExpertInterface/index';
import { TournesolAPI } from '../../api';

// iterate over the comparisons in random order
const ComparisonSelector = ({
  videoId,
  onComparisonChanged = () => {},
}) => {
  // number of comparisons (ratings)
  const [count, setCount] = React.useState(null);
  // internal offset state
  const [offset, setOffset] = React.useState(0);
  // resulting current rating
  const [rating, setRating] = React.useState(null);

  if (!videoId) {
    return null;
  }

  // requesting the count if not requested before
  if (count === null) {
    setCount(undefined);
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsList({ limit: 1, offset, videoVideoId: videoId }, (err, data) => {
      if (!err && data.count >= 1) {
        setCount(data.count);
        setRating(data.results[0]);
        if (onComparisonChanged) {
          onComparisonChanged(null, null);
        }
      }
    });
    return null;
  }

  if (count === undefined || !rating) {
    return <Typography paragraph>Loading your ratings . . .</Typography>;
  }

  if (count === 0) {
    return <Typography paragraph>You have not yet compared this video with others</Typography>;
  }

  const onlineUpdateFeed = (videoId1, videoId2, feature, value) => {
    const api = new TournesolAPI.ExpertRatingsApi();
    api.expertRatingsOnlineByVideoIdsRetrieve(
      feature,
      value,
      videoId1,
      videoId2,
      { addDebugInfo: false },
      (err, data) => {
        if (!err) {
          const newScore = videoId1 === videoId ? data.new_score_left : data.new_score_right;
          onComparisonChanged(feature, newScore);
        }
      },
    );
  };

  return (
    <Grid container justify="center">
      <Typography paragraph>
        You compared the video {count} {count > 1 ? 'times' : 'time'}.
        Showing rating {offset + 1}/{count}.
      </Typography>

      <Grid
        container
        direction="row"
        justify="center"
        alignItems="center"
      >
        <Grid item>
          {/* left button */}
          <IconButton
            aria-label="left"
            color="primary"
            variant="outlined"
            onClick={() => setOffset(offset - 1) || setCount(null)}
            disabled={offset <= 0}
          >
            <SkipPreviousIcon />
          </IconButton>

        </Grid>

        <Grid item>
          <ExpertInterface
            videoIdAOverride={rating.video_1}
            videoIdBOverride={rating.video_2}
            showControls={false}
            onSliderFeatureChanged={(feature, value) => onlineUpdateFeed(
              rating.video_1,
              rating.video_2,
              feature,
              value,
            )}
            key={`rating-${rating.id}`}
          />
        </Grid>

        {/* right button */}
        <Grid item>
          <IconButton
            aria-label="left"
            color="primary"
            variant="outlined"
            onClick={() => setOffset(offset + 1) || setCount(null)}
            disabled={offset + 1 >= count}
          >
            <SkipNextIcon />
          </IconButton>
        </Grid>
      </Grid>
    </Grid>
  );
};

export default ComparisonSelector;
