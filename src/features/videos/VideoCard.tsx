/* eslint-disable react/no-unescaped-entities */
import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { Typography, Grid } from '@material-ui/core';

import type { Video, ComparisonCriteriaScore } from 'src/services/openapi';

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
  application_details: {
    width: '100%',
    display: 'flex',
    flexWrap: 'wrap',
    alignItems: 'center',
    padding: 4,
  },
  nb_tournesol: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '32px',
    lineHeight: '32px',
    // display: 'flex',
    // alignItems: 'center',
    // color: '#6A6658',
    // marginLeft: '8.92px',
    // marginTop: '5px',
    // marginRight: '24px',
  },
  ratings: {
    marginRight: '4px',
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 'normal',
    fontSize: '15px',
    lineHeight: '22px',
    color: '#A09B87',
    marginTop: '12px',
  },
  contributors: {
    fontFamily: 'Poppins',
    fontStyle: 'italic',
    fontWeight: 500,
    fontSize: '15px',
    lineHeight: '22px',
    textDecorationLine: 'underline',
    color: '#B38B00',
    marginTop: '12px',
  },
  rated: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: '15px',
    lineHeight: '22px',
    color: '#847F6E',
    marginLeft: 16,
    display: 'flex',
    alignItems: 'center',
  },
  logo: {
    marginLeft: 8,
  },
  top: {
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
  },
  later: {
    marginLeft: '159.75px',
  },
  moreInfo: {
    marginLeft: '21.75px',
  },
  detailsImage: {
    marginLeft: '116px',
    paddingBottom: 0,
  },
}));

type VideoWithCriteriaScore = Video & {
  criteria_scores?: Array<ComparisonCriteriaScore>;
};

function VideoCard({ video }: { video: VideoWithCriteriaScore }) {
  const classes = useStyles();
  const video_id = video.video_id;
  const video_url = 'https://www.youtube.com/embed/'.concat(video_id);
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
      criteria.criteria != 'largely_recommanded'
    ) {
      max_score = criteria.score;
      max_criteria = criteria.criteria;
    } else if (
      criteria.score != undefined &&
      criteria.score < min_score &&
      criteria.criteria != 'largely_recommanded'
    ) {
      min_score = criteria.score;
      min_criteria = criteria.criteria;
    }
  });
  // TODO: this is commented out because it will included in a future release
  // const nb_ratings = 51;
  // const nb_contributors = 18;

  return (
    <Grid container spacing={1} className={classes.main}>
      <Grid item xs={12} sm={4} style={{ aspectRatio: '16 / 9', padding: 0 }}>
        <iframe width="100%" height="100%" src={video_url}></iframe>
      </Grid>
      <Grid item xs={12} sm={8}>
        <div className={classes.top}>
          <Typography className={classes.title} variant="h5">
            {video.name}
          </Typography>
          {/* <img className={classes.later} src={'/svg/later.svg'} alt="logo" />
            <img
              className={classes.moreInfo}
              src={'/svg/more_info.svg'}
              alt="logo"
            /> */}
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
        <div className={classes.summary}>
          <span>{video.description}</span>
          {/* <img
              className={classes.detailsImage}
              src={'/svg/details.svg'}
              alt="logo"
            /> */}
        </div>
        <div className={classes.application_details}>
          {max_criteria.length > 0 && (
            <>
              <div className={classes.logo}>
                <img
                  className="tournesol"
                  src={'/svg/tournesol.svg'}
                  alt="logo"
                />
              </div>
              <span className={classes.nb_tournesol}>
                {total_score.toFixed(0)}
              </span>
              {/*<p className={classes.ratings}>{nb_ratings} Ratings by</p>
          <p className={classes.contributors}>{nb_contributors} contributors</p> */}
              <div className={classes.rated}>
                <span>Rated high:</span>
                <img
                  className={classes.logo}
                  src={`/svg/${max_criteria}.svg`}
                  alt={max_criteria}
                  title={max_criteria}
                />
              </div>
              <div className={classes.rated}>
                <span>Rated low:</span>
                <img
                  className={classes.logo}
                  src={`/svg/${min_criteria}.svg`}
                  alt={min_criteria}
                  title={min_criteria}
                />
              </div>
            </>
          )}
        </div>
      </Grid>
    </Grid>
  );
}

export default VideoCard;
