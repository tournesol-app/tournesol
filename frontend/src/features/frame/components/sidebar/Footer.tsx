import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link } from 'react-router-dom';
import makeStyles from '@mui/styles/makeStyles';
import { Box, Divider, Theme } from '@mui/material';

import { getWikiBaseUrl } from 'src/utils/url';

const useStyles = makeStyles((theme: Theme) => ({
  linksContainer: {
    padding: '8px',
    borderTop: '1px solid #e7e5db',
    display: 'flex',
    flexFlow: 'row wrap',
    justifyContent: 'space-between',
  },
  menuLink: {
    margin: 4,
    textDecoration: 'none',
    fontStyle: 'normal',
    fontSize: '0.875em',
    fontWeight: 'bold',
    color: theme.palette.neutral.main,
    display: 'block',
    '&:hover': {
      textDecoration: 'underline',
      color: theme.palette.neutral.dark,
    },
  },
}));

const Footer = () => {
  const { t } = useTranslation();
  const classes = useStyles();

  return (
    <Box>
      <div className={classes.linksContainer}>
        <a
          className={classes.menuLink}
          href={getWikiBaseUrl()}
          target="_blank"
          rel="noreferrer"
        >
          {t('footer.wiki')}
        </a>
        <Link className={classes.menuLink} to="/about/privacy_policy">
          {t('footer.privacyPolicy')}
        </Link>
        <Link className={classes.menuLink} to="/about/donate">
          {t('footer.donate')}
        </Link>
        <a
          className={classes.menuLink}
          href="https://arxiv.org/abs/2107.07334"
          target="_blank"
          rel="noreferrer"
        >
          {t('footer.whitePaper')}
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
      <Divider />
    </Box>
  );
};

export default Footer;
