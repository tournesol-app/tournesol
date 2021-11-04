/* eslint-disable react/no-unescaped-entities */
import React from 'react';
import ReactPlayer from 'react-player/youtube';

import { makeStyles } from '@material-ui/core/styles';
import { Typography, Grid, Box } from '@material-ui/core';

import { mainCriteriaNamesObj } from 'src/utils/constants';
import type { VideoSerializerWithCriteria } from 'src/services/openapi';
import { ActionList } from 'src/utils/types';

const useStyles = makeStyles(() => ({
  main: {
    margin: 4,
    maxWidth: 1000,
    width: 'calc(100% - 8px)',
  },
  title: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    color: '#1D1A14',
  },
  youtube_complements: {
    margin: 4,
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 'normal',
    fontSize: '13px',
    lineHeight: '19px',
    color: '#B6B1A1',
  },
  youtube_complements_p: {
    marginRight: '12px',
  },
  channel: {
    textDecorationLine: 'underline',
  },
  summary: {
    flex: 1,
    maxHeight: 85,
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: '11px',
    color: '#4A473E',
    overflow: 'auto',
  },
  nb_tournesol: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '32px',
    lineHeight: '32px',
  },
  ratings: {
    marginRight: '4px',
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 'normal',
    fontSize: '15px',
    color: '#A09B87',
  },
  contributors: {
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 500,
    fontSize: '15px',
    textDecorationLine: 'underline',
    color: '#B38B00',
  },
  rated: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: '15px',
    color: '#847F6E',
    gap: '8px',
  },
  top: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
  },
}));

function VideoCard({
  video,
  actions,
}: {
  video: VideoSerializerWithCriteria;
  actions: ActionList;
}) {
  const classes = useStyles();
  const videoId = video.video_id;
  let total_score = 0;
  let max_score = -Infinity;
  let min_score = Infinity;
  // eslint-disable-next-line @typescript-eslint/no-inferrable-types
  let max_criteria: string = '';
  // eslint-disable-next-line @typescript-eslint/no-inferrable-types
  let min_criteria: string = '';
  video.criteria_scores?.forEach((criteria) => {
    total_score += criteria.score != undefined ? 10 * criteria.score : 0;
    if (
      criteria.score != undefined &&
      criteria.score > max_score &&
      criteria.criteria != 'largely_recommended'
    ) {
      max_score = criteria.score;
      max_criteria = criteria.criteria;
    }
    if (
      criteria.score != undefined &&
      criteria.score < min_score &&
      criteria.criteria != 'largely_recommended'
    ) {
      min_score = criteria.score;
      min_criteria = criteria.criteria;
    }
  });

  return (
    <Grid container spacing={1} className={classes.main}>
      <Grid item xs={12} sm={4} style={{ aspectRatio: '16 / 9', padding: 0 }}>
        <ReactPlayer
          url={`https://youtube.com/watch?v=${videoId}`}
          light
          width="100%"
          height="100%"
        />
      </Grid>
      <Grid item xs={12} sm={7}>
        <div className={classes.top}>
          <Typography className={classes.title} variant="h5">
            {video.name}
          </Typography>
        </div>
        <div className={classes.youtube_complements}>
          {video.views && (
            <span className={classes.youtube_complements_p}>
              {video.views} views
            </span>
          )}
          {video.publication_date && (
            <span className={classes.youtube_complements_p}>
              {video.publication_date}
            </span>
          )}
          {video.uploader && (
            <span className={classes.channel}>{video.uploader}</span>
          )}
        </div>
        <Box
          display="flex"
          flexWrap="wrap"
          alignItems="center"
          style={{ gap: '12px' }}
        >
          {max_criteria.length > 0 && (
            <>
              <Box display="flex" alignItems="center">
                <img
                  className="tournesol"
                  src={'/svg/tournesol.svg'}
                  alt="logo"
                  title="Overall score"
                />
                <span className={classes.nb_tournesol}>
                  {total_score.toFixed(0)}
                </span>
              </Box>

              {!!video.rating_n_ratings && video.rating_n_ratings > 0 && (
                <Box>
                  <span className={classes.ratings}>
                    {video.rating_n_ratings} Ratings by
                  </span>
                  <span className={classes.contributors}>
                    {video.rating_n_contributors} contributors
                  </span>
                </Box>
              )}
              <Box display="flex" alignItems="center" className={classes.rated}>
                <span>Rated high:</span>
                <img
                  src={`/svg/${max_criteria}.svg`}
                  alt={max_criteria}
                  title={mainCriteriaNamesObj[max_criteria]}
                />
                <span>Rated low:</span>
                <img
                  src={`/svg/${min_criteria}.svg`}
                  alt={min_criteria}
                  title={mainCriteriaNamesObj[min_criteria]}
                />
              </Box>
            </>
          )}
        </Box>
      </Grid>
      <Grid item xs={12} sm={1}>
        {actions.map((Action, index) => (
          <Action key={index} videoId={videoId} />
        ))}
      </Grid>
    </Grid>
  );
}

export default VideoCard;
