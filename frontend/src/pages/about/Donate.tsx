import React from 'react';
import { useTranslation } from 'react-i18next';
import makeStyles from '@mui/styles/makeStyles';
import { Typography, Link, Stack, Button } from '@mui/material';

import { ContentHeader, ContentBox } from 'src/components';
import FundingSection from 'src/pages/home/videos/sections/FundingSection';
import { utipTournesolUrl, paypalDonateTournesolUrl } from 'src/utils/url';

const useStyles = makeStyles((theme) => ({
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
      <ContentHeader title={t('about.donate')} />
      <ContentBox maxWidth="lg">
        <Stack spacing={2}>
          <FundingSection linkToSupportPage={false} fullWidth />
          <Typography variant="h2" component="h2" textAlign="center">
            {t('about.donateHowTo')}
          </Typography>
          <Stack
            flexWrap="wrap"
            direction="row"
            spacing={2}
            py={2}
            alignItems="stretch"
            justifyContent="space-evenly"
          >
            <Stack
              direction="column"
              spacing={2}
              alignItems="center"
              justify-content="space-between"
            >
              <Link href={utipTournesolUrl} rel="noopener" target="_blank">
                <img src="/logos/800px-UTip_Logo.png" style={{ height: 110 }} />
              </Link>
              <Link
                href={utipTournesolUrl}
                rel="noopener"
                target="_blank"
                underline="none"
              >
                <Button variant="contained">Faire un don avec UTip</Button>
              </Link>
            </Stack>
            <Stack
              direction="column"
              spacing={2}
              alignItems="center"
              justify-content="space-between"
            >
              <Link
                href={paypalDonateTournesolUrl}
                rel="noopener"
                target="_blank"
              >
                <img src="/logos/Paypal_Logo.svg" style={{ height: 110 }} />
              </Link>
              <Link
                href={paypalDonateTournesolUrl}
                rel="noopener"
                target="_blank"
                underline="none"
              >
                <Button variant="contained">Faire un don avec Paypal</Button>
              </Link>
            </Stack>
          </Stack>

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
        </Stack>
      </ContentBox>
    </>
  );
};

export default DonatePage;
