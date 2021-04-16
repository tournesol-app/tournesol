import React from 'react';

import { withStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Tooltip from '@material-ui/core/Tooltip';

export const tooltips = [
  <Typography>
    (1/8) Copy-paste the URL of a video you want to rate. You can find such
    videos for example in your{' '}
    <a
      href="https://www.youtube.com/feed/history"
      target="_blank"
      rel="noreferrer"
    >
      watch history
    </a>{' '}
    or list of{' '}
    <a
      href="https://www.youtube.com/playlist?list=LL"
      target="_blank"
      rel="noreferrer"
    >
      liked videos
    </a>
  </Typography>,
  <Typography>
    (2/8) Copy-paste the URL of a video you want to use as comparison
    (preferrably one that you have already watched)
  </Typography>,
  <Typography>
    (3/8) Position the slider to let us know which of the two videos is best
    according to the particular features. (For this feature, moving the silder
    left means that the video on the left is more reliable)
  </Typography>,
  <Typography>
    (4/8) Please provide ratings for most of the quality features
  </Typography>,
  <Typography>
    (5/8) Finally, submit your ratings to help improve Tournesol's
    recommendations!
  </Typography>,
  <Typography>
    (6/8) You can check the score and add comments to the video that you rated
  </Typography>,
  <Typography>(7/10) If the video is unsuitable, please report it.</Typography>,
  <Typography>
    (8/8) Once you will have rated multiple video you will be able to
    automatically load previous video to provide new ratings without watching
    more videos!
  </Typography>,
];

export const TutorialTooltip = withStyles((theme) => ({
  tooltip: {
    backgroundColor: theme.palette.primary.main,
    border: 'solid 1px black',
    color: 'black',
  },
}))((props) => (
  <Tooltip
    open={props.tourIndex === props.i}
    {...props} // eslint-disable-line
    title={tooltips[props.tourIndex]}
    interactive
    arrow
  />
));
