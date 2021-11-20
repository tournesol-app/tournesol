import React from 'react';

import { makeStyles } from '@material-ui/core/styles';

import { handleWikiUrl } from 'src/utils/url';

const useStyles = makeStyles(() => ({
  root: {
    padding: 8,
    borderTop: '1px solid #806300',
    display: 'flex',
    flexFlow: 'row wrap',
    justifyContent: 'space-between',
  },
  menuLink: {
    margin: 4,
    textDecoration: 'none',
    fontFamily: 'Poppins',
    fontStyle: 'normal',
    fontWeight: 'bold',
    color: '#806300',
    display: 'block',
  },
}));

const Footer = () => {
  const classes = useStyles();

  return (
    <div className={classes.root}>
      <a
        className={classes.menuLink}
        href={handleWikiUrl(window.location.host)}
        target="_blank"
        rel="noreferrer"
      >
        about
      </a>
      <a className={classes.menuLink} href="/donate">
        donate
      </a>
      <a
        className={classes.menuLink}
        href="/pdf/privacy_policy_tournesol.pdf"
        download
      >
        privacy policy
      </a>
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
