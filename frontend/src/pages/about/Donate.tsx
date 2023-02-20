import React from 'react';
import { useTranslation } from 'react-i18next';

import { Button, Link, Stack, Typography } from '@mui/material';
import Grid2 from '@mui/material/Unstable_Grid2/Grid2';
import makeStyles from '@mui/styles/makeStyles';

import { ContentHeader, ContentBox } from 'src/components';
import TitledPaper from 'src/components/TitledPaper';
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
  const classes = useStyles();
  const { t } = useTranslation();

  const donateSectionSx = {
    width: '100%',
  };

  return (
    <>
      <ContentHeader title={t('about.donate')} />
      <ContentBox maxWidth="lg">
        <Grid2
          container
          width="100%"
          gap={6}
          flexDirection="column"
          alignItems="center"
        >
          <Grid2 sx={donateSectionSx}>
            <FundingSection linkToSupportPage={false} fullWidth />
          </Grid2>
          <Grid2 sx={donateSectionSx}>
            <TitledPaper title={t('about.donateHowTo')}>
              <Stack
                spacing={4}
                flexWrap="wrap"
                direction="row"
                alignItems="stretch"
                justifyContent="space-evenly"
              >
                <Stack
                  spacing={2}
                  direction="column"
                  alignItems="center"
                  justify-content="space-between"
                >
                  <Link href={utipTournesolUrl} rel="noopener" target="_blank">
                    <img src="/logos/800px-UTip_Logo.png" height="110px" />
                  </Link>
                  <Link
                    href={utipTournesolUrl}
                    rel="noopener"
                    target="_blank"
                    underline="none"
                  >
                    <Button variant="contained">
                      {t('donate.donateWithUtip')}
                    </Button>
                  </Link>
                </Stack>
                <Stack
                  spacing={2}
                  direction="column"
                  alignItems="center"
                  justify-content="space-between"
                >
                  <Link
                    href={paypalDonateTournesolUrl}
                    rel="noopener"
                    target="_blank"
                  >
                    <img src="/logos/Paypal_Logo.svg" height="110px" />
                  </Link>
                  <Link
                    href={paypalDonateTournesolUrl}
                    rel="noopener"
                    target="_blank"
                    underline="none"
                  >
                    <Button variant="contained">
                      {t('donate.donateWithPaypal')}
                    </Button>
                  </Link>
                </Stack>
              </Stack>
            </TitledPaper>
          </Grid2>
          <Grid2 sx={donateSectionSx}>
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
          </Grid2>
        </Grid2>
      </ContentBox>
    </>
  );
};

export default DonatePage;
