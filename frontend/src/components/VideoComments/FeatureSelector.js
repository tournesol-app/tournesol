import React from 'react';

import Tooltip from '@material-ui/core/Tooltip';
import { makeStyles } from '@material-ui/core/styles';
import Button from '@material-ui/core/Button';
import CheckIcon from '@material-ui/icons/Check';
import { featureNames, featureList, featureColors } from '../../constants';

const useStyles = makeStyles(() => ({
  buttonFieldShow: {
    boxShadow: '0 3px 5px 2px rgba(0, 0, 0, .3)',
  },
  featureSelector: {
    padding: '6px',
    width: '100%',
    overflow: 'auto',
  },
  minimalistContainer: {
    display: 'flex',
    flexDirection: 'row',
    width: '100%',
    marginRight: '8px',
    justifyContent: 'flex-end',
  },
  minimalistDisplay: {
    borderRadius: '50%',
    width: '16px',
    height: '16px',
    margin: '4px',
    flex: '0 0 auto',
  },
}));

export default ({
  show = null,
  readOnly = false,
  onUpdate = null,
  onUpdateSingle = null,
  single = false,
  minimalist,
}) => {
  const classes = useStyles();

  const getDefaultShowFeatures = (s) => {
    const showF = {};
    featureList.map((f) => {
      showF[f] = s ? s[f] : true;
      return null;
    });
    return showF;
  };

  const [showFeatures, setShowFeatures] = React.useState(
    getDefaultShowFeatures(show),
  );

  const toggleManyFeature = (f) => {
    const fnew = { ...showFeatures, [f]: !showFeatures[f] };
    return fnew;
  };

  const toggleSingleFeature = (f) => {
    const fnew = {};
    featureList.forEach((f1) => {
      fnew[f1] = false;
    });
    fnew[f] = true;

    if (onUpdateSingle) {
      onUpdateSingle(f);
    }

    return fnew;
  };

  const toggleFeature = (f) => () => {
    let fnew = null;
    if (single) {
      fnew = toggleSingleFeature(f);
    } else {
      fnew = toggleManyFeature();
    }

    setShowFeatures(fnew);
    if (onUpdate) {
      onUpdate(fnew);
    }
  };

  if (minimalist) {
    return (
      <div className={classes.minimalistContainer}>
        {featureList
          .filter((f) => showFeatures[f])
          .map((f) => (
            <div
              key={f}
              style={{
                backgroundColor: featureColors[f],
              }}
              className={classes.minimalistDisplay}
            />
          ))}
      </div>
    );
  }

  return (
    <div className={classes.featureSelector}>
      <div
        style={{
          width: '600px',
          display: 'flex',
          flexDirection: 'row',
          justifyContent: 'space-around',
          position: 'relative',
        }}
      >
        {featureList.map((f) => {
          const c = featureColors[f];
          if (!readOnly || showFeatures[f]) {
            return (
              <Tooltip title={featureNames[f]} aria-label="report">
                <Button
                  size="small"
                  variant="outlined"
                  key={f}
                  style={{ background: c }}
                  className={classes.buttonFieldShow}
                  disabled={readOnly}
                  onClick={toggleFeature(f)}
                >
                  {showFeatures[f] ? <CheckIcon /> : <span>&nbsp;</span>}
                </Button>
              </Tooltip>
            );
          }
          return '';
        })}
      </div>
    </div>
  );
};
