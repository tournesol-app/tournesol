import React from 'react';

import { makeStyles } from '@material-ui/core/styles';

import GridList from '@material-ui/core/GridList';
import GridListTile from '@material-ui/core/GridListTile';

import Plot from 'react-plotly.js';
import { featureNames, featureColors, featureList } from '../constants';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexWrap: 'wrap',
    justifyContent: 'space-around',
    overflow: 'hidden',
    backgroundColor: theme.palette.background.paper,
  },
  plot: {
    width: '320px',
    height: '240px',
  },
  gridList: {
    flexWrap: 'nowrap',
    // Promote the list into his own layer on Chrome. This cost memory but helps keeping high FPS.
    transform: 'translateZ(0)',
  },
  title: {
    color: theme.palette.primary.light,
  },
  titleBar: {
    background:
      'linear-gradient(to top, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.3) 70%, rgba(0,0,0,0) 100%)',
  },
}));

export default ({ videos = null, datasetExternal = null }) => {
  const classes = useStyles();
  const [dataset, setDataset] = React.useState(null);
  const [videosInternal, setVideosInternal] = React.useState(null);

  if (datasetExternal !== null && dataset !== datasetExternal) {
    setDataset(datasetExternal);
  }

  if (videosInternal !== videos) {
    setVideosInternal(videos);
    if (videos.length) {
      let m = videos.map((video) => ({
        score_search_term: video.score_search_term,
        score_preferences_term: video.score_preferences_term,
        total_score: video.score,
        ...Object.fromEntries(featureList.map((k) => [k, video[k]])),
      }));
      m = Object.keys(m[0]).map((key) => [key, m.map((item) => item[key])]);
      setDataset(Object.fromEntries(m));
    }
  }

  return (
    <div className={classes.root}>
      {dataset && (
        <GridList className={classes.gridList} cols={5}>
          {Object.keys(dataset).map((key) => {
            const arr = dataset[key];

            let name = key;
            if (key in featureNames) {
              name = featureNames[key];
            }

            let color = 'black';
            if (key in featureColors) {
              color = featureColors[key];
            }

            return (
              <GridListTile>
                <Plot
                  data={[
                    {
                      x: arr,
                      y: arr,
                      type: 'histogram',
                      mode: 'lines+markers',
                      marker: { color },
                    },
                  ]}
                  layout={{ width: 320, height: 240, title: name }}
                />
              </GridListTile>
            );
          })}
        </GridList>
      )}
    </div>
  );
};
