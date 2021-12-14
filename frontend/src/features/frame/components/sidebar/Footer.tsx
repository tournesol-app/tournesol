import React from 'react';

import { makeStyles } from '@material-ui/core/styles';

import { Link } from 'react-router-dom';

const useStyles = makeStyles(() => ({
  root: {
    padding: 8,
    borderTop: '1px solid #e7e5db',
    display: 'flex',
    flexFlow: 'row wrap',
    justifyContent: 'space-between',
  },
  menuLink: {
    margin: 4,
    textDecoration: 'none',
    fontStyle: 'normal',
    fontWeight: 'bold',
    color: '#A09B87',
    display: 'block',
    '&:hover': {
      textDecoration: 'underline',
      color: '#806300',
    },
  },
}));

const Footer = () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <Link className={classes.menuLink} to="/about">
        about
      </Link>
      <Link className={classes.menuLink} to="/about/privacy_policy">
        privacy policy
      </Link>
      <Link className={classes.menuLink} to="/donate">
        donate
      </Link>
      <a
        className={classes.menuLink}
        href="https://arxiv.org/abs/2107.07334"
        target="_blank"
        rel="noreferrer"
      >
        white paper
      </a>
      <a
        className={classes.menuLink}
        href="https://github.com/tournesol-app/tournesol"
        target="_blank"
        rel="noreferrer"
      >
        github
      </a>
      <a
        className={classes.menuLink}
        href="https://discord.gg/TvsFB8RNBV"
        target="_blank"
        rel="noreferrer"
      >
        discord
      </a>
    </div>
  );
};

export default Footer;
