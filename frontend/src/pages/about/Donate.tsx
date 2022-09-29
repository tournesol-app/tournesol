import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import makeStyles from '@mui/styles/makeStyles';
import { Typography, Link } from '@mui/material';

import { ContentHeader } from 'src/components';
import {
  discordTournesolInviteUrl,
  githubTournesolUrl,
  utipTournesolUrl,
} from 'src/utils/url';

const useStyles = makeStyles((theme) => ({
  root: {
    display: 'flex',
    flexDirection: 'column',
    alignItems: 'center',
  },
  content: {
    maxWidth: '100%',
    width: 640,
    padding: 24,
  },
  box: {
    padding: 8,
    marginTop: 8,
    background: '#FFFFFF',
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: '4px',
    position: 'relative',
  },
  bankingInfo: {
    margin: 0,
  },
  link: {
    color: theme.palette.text.primary,
  },
}));

const DonatePage = () => {
  const { t } = useTranslation();
  const classes = useStyles();
  return (
    <>
      <ContentHeader title="About > Donate" />
      <div className={classes.root}>
        <div className={classes.content}>
          <Typography paragraph>
            <Trans t={t} i18nKey="about.donateWeAreASmallTeam">
              Because we are a small team of mostly volunteers, the development
              of Tournesol is slower than we would like it to be. If you can,
              please consider helping us, through coding or through donations.
              Check-out our{' '}
              <a
                href={githubTournesolUrl}
                target="_blank"
                rel="noreferrer"
                className={classes.link}
              >
                open source code
              </a>
              , or join our{' '}
              <a
                href={discordTournesolInviteUrl}
                target="_blank"
                rel="noreferrer"
                className={classes.link}
              >
                Discord
              </a>
              .
            </Trans>
          </Typography>

          <Typography variant="h4" sx={{ fontStyle: 'italic' }}>
            {t('about.donateHowTo')}
          </Typography>
          <Link
            href={utipTournesolUrl}
            rel="noopener"
            target="_blank"
            underline="none"
            color="inherit"
            variant="inherit"
          >
            <div className={classes.box}>
              <img
                src="/logos/UTip_Logo.png"
                style={{ height: 42, position: 'absolute', top: 0, right: 6 }}
              />
              <Typography variant="h5" sx={{ marginBottom: 1 }}>
                {t('about.donateWithUtipTitle')}
              </Typography>
              <Typography>
                <Trans t={t} i18nKey="about.donateWithUtipDescription">
                  uTip is an online crowdfunding platform. Visit our{' '}
                  <a
                    href={utipTournesolUrl}
                    target="_blank"
                    rel="noreferrer"
                    className={classes.link}
                  >
                    Utip page
                  </a>{' '}
                  to make a one-time or recurring donation
                </Trans>
              </Typography>
            </div>
          </Link>
          <div className={classes.box}>
            <Typography variant="h5" sx={{ marginBottom: 1 }}>
              {t('about.donateByDirectTransferEUR')}
            </Typography>
            <pre className={classes.bankingInfo}>Association Tournesol</pre>
            <pre className={classes.bankingInfo}>Lausanne, Switzerland</pre>
            <pre className={classes.bankingInfo}>
              IBAN: CH75 0900 0000 1570 7623 1
            </pre>
            <pre className={classes.bankingInfo}>BIC: POFICHBEXXX</pre>
          </div>

          <div className={classes.box}>
            <Typography variant="h5" sx={{ marginBottom: 1 }}>
              {t('about.donateByDirectTransferCHF')}
            </Typography>
            <pre className={classes.bankingInfo}>Association Tournesol</pre>
            <pre className={classes.bankingInfo}>Lausanne, Switzerland</pre>
            <pre className={classes.bankingInfo}>
              IBAN: CH42 0900 0000 1569 4102 5
            </pre>
            <pre className={classes.bankingInfo}>BIC: POFICHBEXXX</pre>
          </div>

          <div className={classes.box}>
            <Typography variant="h5" sx={{ marginBottom: 1 }}>
              {t('about.donateByPaypal')}
            </Typography>
            <form
              action="https://www.paypal.com/donate"
              method="post"
              target="_top"
              style={{ marginTop: 8 }}
            >
              <input
                type="hidden"
                name="hosted_button_id"
                value="22T84YR7TZ762"
              />
              <input
                type="image"
                src="https://www.paypalobjects.com/en_US/CH/i/btn/btn_donateCC_LG.gif"
                name="submit"
                title="PayPal - The safer, easier way to pay online!"
                alt="Donate with PayPal button"
              />
              <img
                alt=""
                src="https://www.paypal.com/en_CH/i/scr/pixel.gif"
                width="1"
                height="1"
              />
            </form>
          </div>
        </div>
      </div>
    </>
  );
};

export default DonatePage;
