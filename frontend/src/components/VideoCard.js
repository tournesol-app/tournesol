import React from 'react';

import { withStyles, makeStyles } from '@material-ui/core/styles';

import Popover from '@material-ui/core/Popover';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Tooltip from '@material-ui/core/Tooltip';
import Card from '@material-ui/core/Card';
import Chart from 'react-google-charts';
import CommentIcon from '@material-ui/icons/Comment';
import FunctionsIcon from '@material-ui/icons/Functions';
import SearchIcon from '@material-ui/icons/Search';
import IconButton from '@material-ui/core/IconButton';
import PersonIcon from '@material-ui/icons/Person';
import FilterListIcon from '@material-ui/icons/FilterList';
import { useHistory } from 'react-router-dom';
import ThumbUpIcon from '@material-ui/icons/ThumbUp';
import ThumbDownIcon from '@material-ui/icons/ThumbDown';
import QueuePlayNextIcon from '@material-ui/icons/QueuePlayNext';
import RemoveFromQueueIcon from '@material-ui/icons/RemoveFromQueue';
import Grid from '@material-ui/core/Grid';
import { TournesolAPI } from '../api';
import { YoutubePlayer } from '../utils';
import {
  featureNames,
  featureColors,
  featureList,
  SEARCH_DIVIDER_COEFF,
  SEARCH_FEATURE_CONST_ADD,
} from '../constants';

const useStyles = makeStyles((theme) => ({
  root: {
    margin: 6,
    width: '900px',
    minWidth: '900px',
    padding: '4px',
    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
  },
  videoContainer: {
    height: '142px',
    width: '250px',
    background: '#000',
    flex: 0,
  },
  infoContainer: {
    display: 'flex',
    flexFlow: 'row wrap',
    width: '520px',
  },
  controlsContainer: {
    display: 'flex',
    flexFlow: 'row wrap',
    width: '50px',
  },
  infoScore: {
    display: 'flex',
    flexDirection: 'row',
    width: '300px',
    height: '120px',
    flex: '1 1 auto',
  },
  chartContainer: {
    width: '220px',
    height: '120px',
    flex: '0 0 auto',
  },
  titleBar: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'row',
    marginLeft: '4px',
    flex: '0 0 100%',
    borderBottom: '1px solid #9999',
  },
  subtitle: {
    fontStyle: 'italic',
    color: '#666',
  },
  title: {
    fontSize: '120%',
    fontWeight: 'bold',
    flex: '0 0 100%',
  },
  infoIcon: {
    color: '#999999',
    marginRight: '8px',
  },
  sunflower: {
    fontSize: '600%',
  },
  score: {
    paddingTop: '12px',
    fontSize: '280%',
    fontWeight: 'bold',
  },
  contributorsTooltip: {
    backgroundColor: '#f5f5f9',
    color: 'rgba(0, 0, 0, 0.87)',
    maxWidth: 220,
    border: '1px solid #dadde9',
  },
  paretoPopover: {
    pointerEvents: 'none',
  },
  paretoPaper: {
    padding: theme.spacing(1),
  },
}));

const numberFormat = (x) => {
  if (x === null) return 'null';
  if (x < 1000) return x.toFixed(0);
  if (x < 1000000) return `${(x / 1000).toFixed()}k`;
  if (x < 1000000000) return `${(x / 1000000).toFixed()}M`;
  return `${(x / 1000000000).toFixed()}B`;
};

const VideoEmbed = ({ video, showPlayer, setShowPlayer, light = true }) => {
  const classes = useStyles();

  return (
    <div className={classes.videoContainer}>
      {showPlayer && (
        <YoutubePlayer
          videoId={video.video_id}
          light={light}
          width={250}
          height={142}
        />
      )}
      {!showPlayer && (
        <Button
          variant="contained"
          color="primary"
          onClick={() => {
            setShowPlayer(true);
          }}
        >
          Show video
        </Button>
      )}
    </div>
  );
};

const InfoChart = ({ showChart, setShowChart, video, showMyScore, myInfo }) => {
  const classes = useStyles();
  const [statsRequested, setStatsRequested] = React.useState(false);
  const [globalMaxValue, setGlobalMaxValue] = React.useState(0);
  const [localMinValue, setLocalMinValue] = React.useState(false);
  const [chartReady, setChartReady] = React.useState(false);

  const chartData = [
    [
      'Property',
      'Rating',
      { role: 'style' },
      {
        sourceColumn: 0,
        role: 'annotation',
        type: 'string',
        calc: 'stringify',
      },
    ],
  ];
  featureList.map((k) => {
    let v = video[k];
    if (showMyScore && myInfo !== null) {
      v = myInfo[k];
    }
    chartData.push([
      featureNames[k],
      SEARCH_FEATURE_CONST_ADD + v,
      featureColors[k],
      null,
    ]);
    return null;
  });

  // add search score
  if (video.score_search_term) {
    chartData.push([
      'Search match score',
      video.score_search_term / SEARCH_DIVIDER_COEFF,
      'black',
      null,
    ]);
  }

  if (video.minValue === undefined && localMinValue === false) {
    setLocalMinValue(
      Math.min([
        0,
        Math.min(featureList.map((f) => video[f] + SEARCH_FEATURE_CONST_ADD)),
      ]),
    );
  }

  if (video.maxValue === undefined && !statsRequested) {
    setStatsRequested(true);
    const api = new TournesolAPI.StatisticsApi();
    api.view((_err, stats) => {
      setGlobalMaxValue(stats.max_score + SEARCH_FEATURE_CONST_ADD);
      setChartReady(true);
    });
  } else if (!chartReady) {
    setChartReady(true);
  }

  return (
    <div className={classes.chartContainer}>
      {showChart ? (
        chartReady && (
          <Chart
            width="100%"
            height="100%"
            chartType="BarChart"
            loader={<div>Loading Chart</div>}
            data={chartData}
            options={{
              bar: { groupWidth: '80%' },
              vAxis: { textPosition: 'none' },
              chartArea: { width: '95%', height: '95%' },
              hAxis: {
                minValue:
                  video.minValue !== undefined ? video.minValue : localMinValue,
                maxValue:
                  video.maxValue !== undefined
                    ? video.maxValue
                    : globalMaxValue,
                viewWindow: {
                  min:
                    video.minValue !== undefined
                      ? video.minValue
                      : localMinValue,
                  max:
                    video.maxValue !== undefined
                      ? video.maxValue
                      : globalMaxValue,
                },
              },
            }}
          />
        )
      ) : (
        <Button
          variant="contained"
          color="primary"
          onClick={() => {
            setShowChart(true);
          }}
        >
          Show chart
        </Button>
      )}
    </div>
  );
};

const HtmlTooltip = withStyles((theme) => ({
  tooltip: {
    backgroundColor: '#f5f5f9',
    color: 'rgba(0, 0, 0, 0.87)',
    maxWidth: 220,
    fontSize: theme.typography.pxToRem(12),
    border: '1px solid #dadde9',
  },
}))(Tooltip);

const InfoScore = ({ video, myInfo, showMyInfo }) => {
  const classes = useStyles();

  const [paretoAnchorEl, setParetoAnchorEl] = React.useState(null);

  const handleParetoPopoverOpen = (event) => {
    setParetoAnchorEl(event.currentTarget);
  };

  const handleParetoPopoverClose = () => {
    setParetoAnchorEl(null);
  };

  const paretoOpen = Boolean(paretoAnchorEl);

  return (
    <div className={classes.infoScore}>
      <span
        className={classes.sunflower}
        role="img"
        aria-label="sunflower-logo"
      >
        {video.pareto_optimal ? (
          <div>
            <img
              aria-owns={paretoOpen ? 'pareto-mouse-over-popover' : undefined}
              onMouseEnter={handleParetoPopoverOpen}
              onMouseLeave={handleParetoPopoverClose}
              style={{ width: '1em' }}
              src="/static/video_pareto_logo.png"
              alt="pareto_optimal"
            />
            <Popover
              id="pareto-mouse-over-popover"
              className={classes.paretoPopover}
              classes={{
                paper: classes.paretoPaper,
              }}
              open={paretoOpen}
              anchorEl={paretoAnchorEl}
              anchorOrigin={{
                vertical: 'bottom',
                horizontal: 'left',
              }}
              transformOrigin={{
                vertical: 'top',
                horizontal: 'left',
              }}
              onClose={handleParetoPopoverClose}
              disableRestoreFocus
            >
              <Typography>
                This video is Pareto-optimal! This means that no other video
                uniformly outperforms it according to Tournesol contributors.
              </Typography>
            </Popover>
          </div>
        ) : (
          <img
            style={{ width: '1em' }}
            src="/static/video_logo.png"
            alt="tournesol"
          />
        )}
      </span>
      <div style={{ display: 'flex', flexDirection: 'column' }}>
        <span className={classes.score}>
          Score {Math.round(video.tournesol_score)}
        </span>
        {video.rating_n_ratings !== undefined && (
          <span style={{ color: '#666', fontSize: '90%' }}>
            {showMyInfo && myInfo !== null && (
              <span>Based on {myInfo.rating_n_ratings} ratings by me</span>
            )}
            {!showMyInfo && (
              <span>
                Based on {video.rating_n_ratings} ratings by{' '}
                <HtmlTooltip
                  className={classes.contributorsTooltip}
                  title={
                    <div>
                      {video.public_experts !== undefined &&
                        video.public_experts.map((e) => (
                          <span>
                            <a href={`/user/${e.username}`}>@{e.username}</a>
                            <br />
                          </span>
                        ))}
                      {video.n_public_experts !== undefined &&
                        video.public_experts !== undefined &&
                        video.n_public_experts >
                          video.public_experts.length && (
                          <span>
                            ...
                            <br />
                          </span>
                      )}
                      {video.n_private_experts !== undefined &&
                        video.n_private_experts > 0 && (
                          <span>
                            {video.n_public_experts !== undefined &&
                            video.n_public_experts > 0
                              ? 'and '
                              : ''}
                            {video.n_private_experts} anonymous contributors
                          </span>
                      )}
                    </div>
                  }
                  interactive
                >
                  <span>{video.rating_n_experts} contributors</span>
                </HtmlTooltip>
              </span>
            )}
          </span>
        )}
      </div>
    </div>
  );
};

const TitleBar = ({ video }) => {
  const classes = useStyles();

  return (
    <div className={classes.titleBar}>
      <div style={{ display: 'flex', flexDirection: 'column', flex: 1 }}>
        <span className={classes.title}>{video.name}</span>
        <span className={classes.subtitle}>
          {video.uploader} · {numberFormat(video.views)} views ·{' '}
          {video.publication_date
            ? `${video.publication_date.getFullYear()}.${video.publication_date.getMonth()}.${video.publication_date.getDate()}`
            : 'No date'}
        </span>
      </div>
    </div>
  );
};

const Controls = ({
  video,
  setShowMyScore,
  showMyScore,
  needShowMyScoreToggle,
  myInfo,
  showRatingsLink,
  forceShowAddRateLater = true,
  onRateLaterClick = null,
  showRateLater = true,
  setInRateLater = null,
}) => {
  const history = useHistory();
  const [thankStatus, setThankStatus] = React.useState(null);
  const [rateLaterStatus, setRateLaterStatus] = React.useState(null);
  const [rateLaterId, setRateLaterId] = React.useState(null);
  const [lastVideoId, setLastVideoId] = React.useState(null);

  const innerOnRateLaterClick = () => {
    if (onRateLaterClick !== null) {
      onRateLaterClick();
    }
  };

  // get number of thanks
  const reloadThanks = () => {
    const api = new TournesolAPI.VideosApi();
    api.nThanks(video.video_id, (err, data) => {
      if (!err) {
        setThankStatus(data.n_thanks > 0);
      }
    });
  };

  // is the video in list of ones to rate later?
  const reloadRateLater = () => {
    const api = new TournesolAPI.RateLaterApi();
    api.rateLaterList({ videoVideoId: video.video_id }, (err, data) => {
      if (!err) {
        setRateLaterStatus(data.count > 0);
        if (setInRateLater !== null) {
          setInRateLater(data.count > 0);
        }
        if (data.count === 1) {
          setRateLaterId(data.results[0].id);
        } else {
          setRateLaterId(null);
        }
      }
    });
  };

  // load thanks at the beginning
  if (thankStatus === null) {
    setThankStatus(undefined);
    reloadThanks();
  }

  // load thanks at the beginning
  if (rateLaterStatus === null) {
    setRateLaterStatus(undefined);
    reloadRateLater();
  }

  // updating on id change
  if (video.video_id !== lastVideoId) {
    setLastVideoId(video.video_id);
    setThankStatus(null);
    setRateLaterStatus(null);
  }

  // thank/unthank helper fcn
  const thank = (action) => {
    const api = new TournesolAPI.VideosApi();
    api.thankContributors(action, video.video_id, () => {
      setThankStatus(null);
    });
  };

  // rate later/remove helper fcn
  const rateLater = (add) => {
    const api = new TournesolAPI.RateLaterApi();

    if (add) {
      api.rateLaterCreate({ video: video.video_id }, () => {
        setRateLaterStatus(null);
        innerOnRateLaterClick();
      });
    } else if (rateLaterId !== null) {
      api.rateLaterDestroy(rateLaterId, () => {
        setRateLaterStatus(null);
        innerOnRateLaterClick();
      });
    } else {
      // something is wrong, better reload the data...
      setRateLaterStatus(null);
      innerOnRateLaterClick();
    }
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column' }}>
      <Grid container>
        <Grid item xs={6} spacing={0}>
          <Grid container>
            <Grid item xs={12}>
              {needShowMyScoreToggle && myInfo !== null && (
                <Tooltip
                  title={
                    showMyScore ? 'Show search results scores' : 'Show my score'
                  }
                  aria-label="add"
                >
                  <IconButton
                    aria-label="load"
                    onClick={() => setShowMyScore(!showMyScore)}
                  >
                    {showMyScore ? <SearchIcon /> : <PersonIcon />}
                  </IconButton>
                </Tooltip>
              )}
            </Grid>
            <Grid item xs={12}>
              {thankStatus === true && (
                <Tooltip title="Remove thank you" aria-label="add">
                  <IconButton
                    id={`id_${video.video_id}_unthank`}
                    aria-label="load"
                    onClick={() => thank('unthank')}
                  >
                    <ThumbDownIcon />
                  </IconButton>
                </Tooltip>
              )}
              {thankStatus === false && (
                <Tooltip title="Thank contributors" aria-label="add">
                  <IconButton
                    id={`id_${video.video_id}_thank`}
                    aria-label="load"
                    onClick={() => thank('thank')}
                  >
                    <ThumbUpIcon />
                  </IconButton>
                </Tooltip>
              )}
            </Grid>
          </Grid>
        </Grid>
        <Grid item xs={6}>
          <Grid container>
            <Grid item xs={12}>
              <Tooltip title="Comments" aria-label="add">
                <IconButton
                  aria-label="load"
                  onClick={() => history.push(`/details/${video.video_id}`)}
                >
                  <CommentIcon />
                </IconButton>
              </Tooltip>
            </Grid>

            <Grid item xs={12}>
              <Tooltip title="Rate Video" aria-label="add">
                <IconButton
                  aria-label="load"
                  onClick={() => history.push(`/rate/${video.video_id}/...`)}
                >
                  <FunctionsIcon />
                </IconButton>
              </Tooltip>
            </Grid>

            {showRatingsLink === true && (
              <Grid item xs={12}>
                <Tooltip title="Ratings" aria-label="add">
                  <IconButton
                    className="button_video_ratings"
                    aria-label="load"
                    onClick={() => history.push(`/ratings/${video.video_id}`)}
                  >
                    <FilterListIcon />
                  </IconButton>
                </Tooltip>
              </Grid>
            )}

            <Grid item xs={12}>
              {rateLaterStatus === true && showRateLater === true && (
                <Tooltip title="Remove from Rate Later" aria-label="add">
                  <IconButton
                    id={`id_${video.video_id}_remove_rate_later`}
                    aria-label="load"
                    onClick={() => rateLater(false)}
                  >
                    <RemoveFromQueueIcon />
                  </IconButton>
                </Tooltip>
              )}
              {rateLaterStatus === false &&
                showRateLater === true &&
                (myInfo === null || forceShowAddRateLater) && (
                  <Tooltip title="Add to Rate later" aria-label="add">
                    <IconButton
                      id={`id_${video.video_id}_rate_later`}
                      aria-label="load"
                      onClick={() => rateLater(true)}
                    >
                      <QueuePlayNextIcon />
                    </IconButton>
                  </Tooltip>
              )}
            </Grid>
          </Grid>
        </Grid>
      </Grid>
    </div>
  );
};

export default ({
  video,
  showPlayer_ = true,
  showChart_ = true,
  onlyInfo,
  needShowMyScoreToggle = false,
  showRatingsLink = false,
  forceShowAddRateLater = true,
  showRateLater = true,
  onRateLaterClick = null,
  setInRateLater = null,
}) => {
  const classes = useStyles();

  const [showPlayer, setShowPlayer] = React.useState(showPlayer_);
  const [showChart, setShowChart] = React.useState(showChart_);
  const [showMyScore, setShowMyScore] = React.useState(false);
  const [myInfo, setMyInfo] = React.useState(null);
  const [myInfoRequested, setMyInfoRequested] = React.useState(false);

  if (myInfo === null && !myInfoRequested) {
    setMyInfoRequested(true);
    const api = new TournesolAPI.VideoRatingsApi();
    api.videoRatingsList(
      { limit: 1, videoVideoId: video.video_id },
      (_err, data) => {
        if (!_err && data.count > 0) {
          setMyInfo(data.results[0]);
        }
      },
    );
  }

  return (
    <Card
      className={`${classes.root} video_card_id_${video.video_id}`}
      // style={{
      //   width: onlyInfo ? '550px' : '1000px',
      //   minWidth: onlyInfo ? '550px' : '1000px',
      // }}
    >
      <Grid
        container
        direction="row"
        justify="center"
        alignItems="center"
        style={{ flexGrow: 1 }}
      >
        <Grid item>
          {!onlyInfo && (
            <VideoEmbed
              video={video}
              showPlayer={showPlayer}
              setShowPlayer={setShowPlayer}
            />
          )}
        </Grid>
        <Grid item>
          <div className={classes.infoContainer}>
            <TitleBar video={video} />
            <InfoScore video={video} myInfo={myInfo} showMyInfo={showMyScore} />
            <InfoChart
              video={video}
              showChart={showChart}
              setShowChart={setShowChart}
              showMyScore={showMyScore}
              myInfo={myInfo}
            />
          </div>
        </Grid>

        <Grid item>
          <div className={classes.controlsContainer}>
            {!onlyInfo && window.is_authenticated === 1 && (
              <Controls
                video={video}
                needShowMyScoreToggle={needShowMyScoreToggle}
                setShowMyScore={setShowMyScore}
                showMyScore={showMyScore}
                myInfo={myInfo}
                forceShowAddRateLater={forceShowAddRateLater}
                showRatingsLink={showRatingsLink}
                onRateLaterClick={onRateLaterClick}
                setInRateLater={setInRateLater}
                showRateLater={showRateLater}
              />
            )}
          </div>
        </Grid>
      </Grid>
    </Card>
  );
};
