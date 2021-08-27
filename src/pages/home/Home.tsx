import React from 'react';
import { Link } from 'react-router-dom';

import { makeStyles } from '@material-ui/core/styles';

import { topBarHeight } from '../../features/frame/components/topbar/TopBar';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
    minWidth: '420px',
    marginTop: 120,
  },
  rectangle67: {
    display: 'flex',
    justifyContent: 'flex-end',
    position: 'absolute',
    width: '100%',
    height: '534px',
    left: '0px',
    top: topBarHeight,
    background: '#1282B2',
  },
  wateringSunflower: {
    position: 'absolute',
    width: '374px',
    height: '392.01px',
    right: '211px',
    top: '118px',
  },
  menuLink: {
    /* Auto Layout */

    display: 'flex',
    flexDirection: 'row',
    alignItems: 'center',
    padding: '11px 16px',

    position: 'static',

    border: 'none',
    boxSizing: 'border-box',
    background: 'none',

    /* Inside Auto Layout */

    order: 1,
    flexGrow: 0,
    marginRight: '0px',

    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    fontSize: '16px',
    lineHeight: '18px',
    color: '#FFFFFF',
  },

  menu: {
    display: 'flex',
    flexFlow: 'row wrap',
    background: 'none',
    maxHeight: '80px',
  },
}));

const Home = () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <div className={classes.rectangle67}>
        <img src="/svg/Watering.svg" className={classes.wateringSunflower} />
        <div className={classes.menu}>
          <Link to="/comparisons" className={classes.menuLink}>
            CONTRIBUTE
          </Link>
          <a
            className={classes.menuLink}
            href="https://wiki.staging.tournesol.app"
            target="_blank"
            rel="noreferrer"
          >
            ABOUT
          </a>
          <Link className={classes.menuLink} to="/donate">
            DONATE
          </Link>
        </div>
      </div>
    </div>
  );
};

function HomePage() {
  return (
    <div>
      <Home />
    </div>
  );
}

export default HomePage;
