/* eslint-disable react/no-unescaped-entities */
import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import { Typography, Grid } from '@material-ui/core';

import type { Video } from 'src/services/openapi';

const useStyles = makeStyles(() => ({
  main: {
    margin: 4,
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
    maxHeight: 105,
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'normal',
    fontSize: '14px',
    color: '#4A473E',
    overflow: 'auto',
  },
  application_details: {
    marginTop: '-6px',
    width: '150%',
    display: 'flex',
    flexWrap: 'wrap',
    alignContent: 'space-between',
  },
  tournesol: {
    marginTop: '-5px',
  },
  nb_tournesol: {
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '32px',
    lineHeight: '32px',
    display: 'flex',
    alignItems: 'center',
    color: '#6A6658',
    marginLeft: '8.92px',
    marginTop: 0,
    marginRight: '24px',
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
    marginLeft: '24px',
    marginTop: '12px',
  },
  logo: {
    marginLeft: '9.27px',
    marginTop: '-16px',
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

function VideoCard({ video }: { video: Video }) {
  const classes = useStyles();
  const video_id = video.video_id;
  const video_url = 'https://www.youtube.com/embed/'.concat(video_id);
  // TODO: this is commented out because it will included in a future release
  // const nb_tournesol = 80;
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
        {/* TODO: This is commented out because these features are not yet supported
        <div className={classes.application_details}>
          <div className="cropped">
            <img
              className={classes.tournesol}
              src={'/svg/tournesol.svg'}
              alt="logo"
            />
          </div>
          <p className={classes.nb_tournesol}>{nb_tournesol}</p>
          <p className={classes.ratings}>{nb_ratings} Ratings by</p>
          <p className={classes.contributors}>{nb_contributors} contributors</p>
          <p className={classes.rated}>Rated high:</p>
          <img
            className={classes.logo}
            src={'/svg/Reliable and not misleading.svg'}
            alt="logo"
          />
          <p className={classes.rated}>Rated low:</p>
          <img
            className={classes.logo}
            src="/svg/Reliable and not misleading.svg"
            alt="logo"
          />
        </div> */}
      </Grid>
    </Grid>
  );
}

export default VideoCard;
