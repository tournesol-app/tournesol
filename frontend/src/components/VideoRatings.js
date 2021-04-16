import React from 'react';

import { useParams, useHistory } from 'react-router-dom';

import { makeStyles } from '@material-ui/core/styles';

import Grid from '@material-ui/core/Grid';
import YouTube from 'react-youtube';
import FunctionsIcon from '@material-ui/icons/Functions';
import FilterListIcon from '@material-ui/icons/FilterList';
import IconButton from '@material-ui/core/IconButton';
import VideoCard from './VideoCard';
import {
  GET_SINGLE_VIDEO_RATINGS,
  GET_COMPARISON_RATINGS,
  DOUBLE_DOWN,
  GET_CYCLIC_INCONSISTENCIES,
} from '../api';
import { featureList, featureNames } from '../constants';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    width: '100%',
  },
  formControl: {
    margin: theme.spacing(3),
  },
}));

export default () => {
  const classes = useStyles();
  const params = useParams();
  const { videoId } = params;

  // console.log(videoId);

  const [savedParams, setSavedParams] = React.useState({});
  const [comparisonRatings, setComparisonRatings] = React.useState([]);
  const [videos, setVideos] = React.useState([]);
  const [loading, setLoading] = React.useState(true);
  const [mismatched, setMismatched] = React.useState([]);
  const [cyclic, setCyclic] = React.useState([]);

  const history = useHistory();

  const ytOpts = {
    height: '192px',
    width: '300px',
    playerVars: {
      // https://developers.google.com/youtube/player_parameters
      autoplay: 0,
    },
  };

  const updateRatings = () => {
    setLoading(true);
    const options = { username: window.username };
    if (videoId !== undefined) {
      options.videoVideoId = videoId;
    }

    const countComparisons = (v, comparisonRatings_) => {
      const compBool = comparisonRatings_.map(
        (c) => c.video_1 === v || c.video_2 === v,
      );
      const sum = compBool.reduce((res, item) => res + item, 0);
      return sum;
    };

    GET_CYCLIC_INCONSISTENCIES(window.username, (x) => setCyclic(x));

    GET_COMPARISON_RATINGS((comparisonRatingsNew) => {
      setComparisonRatings(comparisonRatingsNew);

      GET_SINGLE_VIDEO_RATINGS((r) => {
        const videosNew = Object.fromEntries(
          r.map((rating) => {
            const scoreInfo = featureList.map((f) => [f, rating[f]]);
            return [
              rating.video,
              {
                ...Object.fromEntries(scoreInfo),
                ...rating.video_dict,
                video_id: rating.video,
                score: rating.score,
                score_info: Object.fromEntries(scoreInfo),
                rating_n_ratings: countComparisons(
                  rating.video,
                  comparisonRatingsNew,
                ),
                rating_n_experts: 1,
              },
            ];
          }),
        );
        setVideos(videosNew);

        // console.log(videosNew);

        const mismatchedNew = [];

        comparisonRatingsNew.forEach((c) => {
          if (!videosNew[c.video_1] || !videosNew[c.video_2]) {
            return;
          }
          featureList.forEach((f) => {
            const y = c[f] - 50;
            const modelScore =
              1 +
              2.0 /
                (1 +
                  Math.exp(
                    videosNew[c.video_2][f] -
                      videosNew[c.video_1][f],
                  ));
            const delta = y * modelScore;
            if (delta < 0) {
              mismatchedNew.push({
                feature: f,
                video_1: c.video_1,
                video_2: c.video_2,
                y,
                model_score: modelScore,
                delta,
              });
            }
          });
        });
        mismatchedNew.sort((a, b) => a.delta - b.delta);
        setMismatched(mismatchedNew);

        // const datasetNew = featureList.map((f) => [
        //   f,
        //   r.map((video) => video[f]),
        // ]);
        // setDataset(Object.fromEntries(datasetNew));
        setLoading(false);

        return null;
      }, options);
      return null;
    }, options);
    setSavedParams(params);
    return null;
  };

  if (params !== savedParams) {
    updateRatings();
  }

  return (
    <div className={classes.root} id="id_my_ratings">
      <Grid container spacing={3} style={{ width: '100%' }}>
        {!loading && (
          <Grid item xs={12}>
            My ratings: {videos.length} videos, {comparisonRatings.length}{' '}
            comparisons
          </Grid>
        )}

        {loading && 'Loading...'}

        {!loading && cyclic.length > 0 && (
          <span>
            <h3>Rating cyclic inconsistency</h3>
            <p>Note, ratings are not updated in real time.</p>

            {cyclic.map((m) => (
              <Grid item xs={12}>
                Cycle of length {m.videos.length - 1}:
                {[...Array(m.videos.length - 1).keys()].map((i) => (
                  <span>
                    <IconButton
                      aria-label="v1"
                      onClick={() => history.push(`/details/${m.videos[i]}`)}
                    >
                      {m.videos[i]}
                    </IconButton>
                    <IconButton
                      aria-label="rerate"
                      onClick={() => history.push(
                        `/rate/${m.ratings[i][0]}/${m.ratings[i][1]}`,
                      )}
                    >
                      <FunctionsIcon />
                    </IconButton>
                  </span>
                ))}
                <IconButton
                  aria-label="v1"
                  onClick={() => history.push(`/details/${m.videos[m.videos.length - 1]}`)}
                >
                  {m.videos[m.videos.length - 1]}
                </IconButton>
              </Grid>
            ))}
          </span>
        )}

        {!loading && (
          <span>
            <h3>Algorithmic representative inconsistency</h3>
            <p>Note, ratings are not updated in real time.</p>
            {mismatched.slice(0, 10).map((m) => (
              <Grid item xs={12}>
                <IconButton
                  aria-label="v1"
                  onClick={() => history.push(`/details/${m.video_1}`)}
                >
                  {m.video_1}
                </IconButton>
                /
                <IconButton
                  aria-label="v2"
                  onClick={() => history.push(`/details/${m.video_2}`)}
                >
                  {m.video_2}
                </IconButton>
                badness {Math.round(m.delta, 1)} on {featureNames[m.feature]}
                <IconButton
                  aria-label="rerate"
                  onClick={() => history.push(`/rate/${m.video_1}/${m.video_2}`)}
                >
                  Re-rate <FunctionsIcon />
                </IconButton>
                <IconButton
                  aria-label="double_down"
                  onClick={() => DOUBLE_DOWN(
                    window.username,
                    m.video_1,
                    m.video_2,
                    m.feature,
                    () => null,
                    () => null,
                  )}
                >
                  Double down
                </IconButton>
              </Grid>
            ))}
          </span>
        )}

        {!loading &&
          Object.values(videos).map((v) => (
            <VideoCard
              video={v}
              showPlayer_={videoId !== undefined}
              showChart_={videoId !== undefined}
            />
          ))}

        {!loading &&
          videoId !== undefined &&
          comparisonRatings.map((r) => {
            const otherVideo = r.video_1 === videoId ? r.video_2 : r.video_1;
            return (
              <Grid item xs={3} className="video_rating_video">
                {window.ENABLE_YOUTUBE_VIDEO_EMBED === 1 ? (
                  <YouTube key={otherVideo} videoId={otherVideo} opts={ytOpts} />
                ) : <span>Youtube {otherVideo}</span>}

                <IconButton
                  className="video_rating_rerate"
                  aria-label="rerate"
                  onClick={() => history.push(`/rate/${r.video_1}/${r.video_2}`)}
                >
                  Re-rate
                  <FunctionsIcon />
                </IconButton>
                <IconButton
                  aria-label="ratings"
                  onClick={() => history.push(`/ratings/${otherVideo}`)}
                >
                  Ratings
                  <FilterListIcon />
                </IconButton>
              </Grid>
            );
          })}
      </Grid>
    </div>
  );
};
