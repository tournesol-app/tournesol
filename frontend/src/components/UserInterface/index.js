import React from 'react';

import { makeStyles } from '@material-ui/core/styles';
import Typography from '@material-ui/core/Typography';
import Button from '@material-ui/core/Button';
import Alert from '@material-ui/lab/Alert';
import CircularProgress from '@material-ui/core/CircularProgress';
import TextField from '@material-ui/core/TextField';
import ExpansionPanel from '@material-ui/core/ExpansionPanel';
import ExpansionPanelSummary from '@material-ui/core/ExpansionPanelSummary';
import ExpansionPanelDetails from '@material-ui/core/ExpansionPanelDetails';
import ExpandMoreIcon from '@material-ui/icons/ExpandMore';
import YoutubeSearchedForIcon from '@material-ui/icons/YoutubeSearchedFor';
import VideoLibraryIcon from '@material-ui/icons/VideoLibrary';
import { useParams } from 'react-router-dom';
import { GET_TOP_RECOMMENDATION, TournesolAPI } from '../../api';
import { featureList, SEARCH_DIVIDER_COEFF, SEARCH_FEATURE_CONST_ADD } from '../../constants';
import SearchOptions from './SearchOption';
import SearchPreferences from './SearchPreference';
import VideoCard from '../VideoCard';

const getDefaultPreference = () => {
  const p = {};
  featureList.forEach((f) => {
    p[f] = 25;
  });
  return p;
};

const useStyles = makeStyles(() => ({
  root: {
    display: 'flex',
    width: '100%',
    height: '100%',
    overflow: 'hidden',
    flexDirection: 'column',
  },
  main: {
    display: 'flex',
    flexDirection: 'row',
    flex: 1,
    overflow: 'hidden',
  },
  searchPanel: {
    display: 'flex',
    flexDirection: 'column',
    marginRight: '8px',
    overflow: 'auto',
    flex: '0 0 320px',
    paddingBottom: '32px',
  },
  container: {
    display: 'flex',
    flexDirection: 'column',
  },
  videoPanel: {
    flex: 1,
    display: 'flex',
    flexDirection: 'row',
    flexWrap: 'wrap',
    alignContent: 'flex-start',
    overflow: 'auto',
    height: '100%',
    minWidth: '400px',
    paddingBottom: '32px',
  },
  loadButton: { marginTop: '16px', marginBottom: '16px', padding: '16px' },
}));

export default ({ searchModelOverride = null, showAllMyVideosInitial = 'false' }) => {
  const batchShowResults = 5;
  const classes = useStyles();
  const { defaultSearchModel = searchModelOverride } = useParams();
  const [videos, setVideos] = React.useState([]);

  // request recommendations on page load
  const [initialRequested, setInitialRequested] = React.useState(false);

  const [preferences, setPreferencesRaw] = React.useState(getDefaultPreference());
  const [options, setOptionsRaw] = React.useState({
    search: '',
    durationGte: 0,
    durationLte: '--null',
    viewsGte: 0,
    viewsLte: '--null',
    daysAgoLte: '--null',
    language: '--null',
    searchYTRaw: 'false',
    searchModel: defaultSearchModel || '--null',
    showAllMyVideos: showAllMyVideosInitial,
  });
  const [loading, setLoading] = React.useState(false);
  const [busy, setBusy] = React.useState(false);
  const [needResult, setNeedResult] = React.useState(false);

  const [lastRefresh, setLastRefresh] = React.useState(null);
  const [refreshPending, setRefreshPending] = React.useState(null);
  const refreshIntervalMs = 1000;

  const [storedPreferencesLoading, setStoredPreferencesLoading] = React.useState(false);
  const [storedPreferencesLoaded, setStoredPreferencesLoaded] = React.useState(false);

  // set minValue and maxValue to each video to show
  const computeMinMaxChart = (v) => {
    let minValue = null;
    let maxValue = null;

    function updateVal(val) {
      if (minValue === null || val < minValue) minValue = val;
      if (maxValue === null || val > maxValue) maxValue = val;
    }

    v.forEach((video) => {
      featureList.forEach((f) => {
        updateVal(video[f] + SEARCH_FEATURE_CONST_ADD);
      });
      if (video.score_search_term) {
        updateVal(video.score_search_term / SEARCH_DIVIDER_COEFF);
      }
    });

    v.forEach((video) => {
      video.minValue = Math.min(0, minValue); // eslint-disable-line no-param-reassign
      video.maxValue = maxValue; // eslint-disable-line no-param-reassign
    });
  };

  const loadRecommendations = (args, forceRefresh = false, append = false) => {
    const currentTimeMs = Date.now();
    let canRun = !loading && (lastRefresh === null ||
        (currentTimeMs - lastRefresh > refreshIntervalMs));
    canRun = canRun || forceRefresh;
    if (!canRun) {
      setRefreshPending(args);
      return false;
    }
    setBusy(true);
    setLastRefresh(currentTimeMs);

    const prefs = (args && args.prefsOverride) ? args.prefsOverride : preferences;
    const opts = (args && args.optsOverride) ? args.optsOverride : options;

    // mapping 0..100 preferences (always positive)
    // into 50..100
    // See (and change) also storedPreferencesLoading
    const preferencesMappedArray = Array.from(
      Object.entries(prefs),
      ([key, value]) => [key, value / 2 + 50],
    );
    const preferencesMapped = Object.fromEntries(preferencesMappedArray);

    // mapping value --null to null
    const optionsMapped = Object.fromEntries(Array.from(Object.entries(opts),
      ([key, value]) => [key, (value === '--null') ? null : value]));

    optionsMapped.offset = append ? videos.length : 0;
    optionsMapped.limit = batchShowResults;

    if (!append) {
      setVideos([]);
    }
    GET_TOP_RECOMMENDATION(preferencesMapped, optionsMapped, (v) => {
      const newVideos = append ? [...videos, ...v] : v;
      computeMinMaxChart(newVideos);
      setVideos(newVideos);
      setLoading(false);
      setBusy(false);
    });
    setLoading(true);
    setNeedResult(true);
    return true;
  };

  // load more videos
  function loadMore() {
    if (loading) {
      return;
    }
    loadRecommendations({}, false, true);
  }

  // run pending updates
  React.useEffect(() => {
    const intervalId = setInterval(() => {
      if (refreshPending !== null) {
        const result = loadRecommendations(refreshPending, true);
        if (result) {
          setRefreshPending(null);
        }
      }
    }, refreshIntervalMs);

    return () => clearInterval(intervalId); // This is important
  }, [preferences, options, lastRefresh, videos, refreshPending, React.useState, loading]);

  /// set preferences and refresh
  const setPreferences = (prefs) => {
    setPreferencesRaw(prefs);
    loadRecommendations({ prefsOverride: prefs });
  };

  // set options and refresh
  const setOptions = (opts) => {
    setOptionsRaw(opts);
    loadRecommendations({ optsOverride: opts });
  };

  if (!storedPreferencesLoading) {
    setStoredPreferencesLoading(true);
    const api = new TournesolAPI.UserPreferencesApi();
    api.userPreferencesMyRetrieve((error, data) => {
      if (!error) {
        // restored preferences from the database
        const p = {};

        // is the setting valid?
        let pValid = true;

        // converting the feature values to the positive range
        featureList.forEach((f) => {
          // See (and change) also preferencesMappedArray
          const val = (data[f] - 50) * 2.0;
          const val1 = Math.min(Math.max(val, 0), 100);

          // load defaults on any out-of-bounds value
          if (val1 !== val) {
            pValid = false;
          }

          p[f] = val1;
        });

        if (pValid) {
          setPreferencesRaw(p);
        }
      }

      // now loading the search results...
      setStoredPreferencesLoaded(true);
    });
  }

  // call resolve later
  function sleep(ms) {
    return new Promise((resolve) => setTimeout(resolve, ms));
  }

  if (!initialRequested && storedPreferencesLoaded) {
    setInitialRequested(true);

    // wait for the animation to go and the page to load
    sleep(1200).then(() => { loadRecommendations(); });
  }

  return (
    <div className={classes.root}>
      <div style={{ flex: '0 0 auto' }}>
        <Alert severity="warning" style={{ margin: '8px' }}>
          We are still in the process of collecting enough data and setting up
          our models to provide expert-driven recommendations. The current
          results do not yet reflect the result of experts' judgments.
        </Alert>
      </div>

      {(busy || refreshPending) && <div id="id_search_loading" />}
      {!(busy || refreshPending) && <div id="id_search_not_loading" />}

      <div className={classes.main}>
        <div className={classes.searchPanel}>
          <TextField
            label="Search phrase"
            id="search_phrase"
            variant="outlined"
            color="secondary"
            value={options.search}
            onChange={(e) => {
              setOptions({ ...options, search: e.target.value });
            }}
            style={{ background: '#0b03', borderRadius: 5, marginTop: '8px' }}
          />

          <SearchPreferences
            preferences={preferences}
            setPreferences={setPreferences}
          />

          <Button
            variant="contained"
            color="primary"
            id="load_recommendations"
            onClick={() => {
              setRefreshPending(null);
              loadRecommendations({}, true, false);
            }}
            className={classes.loadButton}
          >
            Load Recommendations
          </Button>

          <ExpansionPanel defaultExpanded={false}>
            <ExpansionPanelSummary
              expandIcon={<ExpandMoreIcon />}
              className="search_options"
              aria-controls="panel1a-content"
            >
              <Typography>Search Options</Typography>
            </ExpansionPanelSummary>
            <ExpansionPanelDetails>
              <SearchOptions options={options} setOptions={setOptions} />
            </ExpansionPanelDetails>
          </ExpansionPanel>

        </div>

        <div
          className={classes.videoPanel}
          onScroll={(e) => {
            const element = e.target;
            if (element.scrollHeight - element.scrollTop === element.clientHeight) {
              loadMore();
            }
          }}
        >
          {videos.length > 0 && (
            videos
              .map((video) => (
                <div className="video_search_result">
                  <VideoCard
                    key={video.video_id}
                    video={video}
                    needShowMyScoreToggle
                    forceShowAddRateLater={false}
                  />
                </div>))
          )}
          {loading && (
            <CircularProgress color="secondary" />
          )}
          {!loading && !videos.length && needResult && (
            <Alert icon={<YoutubeSearchedForIcon />} severity="warning">
              {options.searchModel === '--null' ? (
                'Empty search result') : (
                'This user did not rate any video publicly'
              )}
            </Alert>
          )}
          {!loading && !needResult && (
            <Alert icon={<VideoLibraryIcon />} severity="success">
              Search results will appear here.
            </Alert>
          )}
        </div>
      </div>
    </div>
  );
};
