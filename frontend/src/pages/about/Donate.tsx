import React, { useEffect } from 'react';
import { useTranslation } from 'react-i18next';
import { useLocation } from 'react-router-dom';

import {
  Alert,
  Box,
  Button,
  Divider,
  Stack,
  Typography,
  Paper,
} from '@mui/material';
import Grid2 from '@mui/material/Unstable_Grid2/Grid2';
import makeStyles from '@mui/styles/makeStyles';

import {
  ContentHeader,
  ContentBox,
  TitledPaper,
  ExternalLink,
} from 'src/components';
import FundingSection from 'src/pages/home/videos/sections/FundingSection';
import {
  KKBBTournesolEnUrl,
  KKBBTournesolFrUrl,
  paypalDonateTournesolUrl,
} from 'src/utils/url';

const useStyles = makeStyles(() => ({
  bankingInfo: {
    margin: 0,
  },
}));

const QuestionRow = ({
  questionText,
  answerText,
}: {
  questionText: string;
  answerText: string;
}) => {
  return (
    <Grid2
      py={2}
      container
      spacing={4}
      justifyContent="center"
      alignItems="stretch"
    >
      <Grid2 xs={12} md={5}>
        <Paper elevation={3} sx={{ borderRadius: 1, height: '100%' }}>
          <Box
            p={3}
            height="100%"
            display="flex"
            justifyContent="center"
            alignItems="center"
            color="#fff"
            bgcolor="background.emphatic"
            borderRadius={20}
            sx={{ borderRadius: 1 }}
          >
            <Typography variant="h5" align="center">
              {questionText}
            </Typography>
          </Box>
        </Paper>
      </Grid2>
      <Grid2 xs={12} md={7}>
        <Paper elevation={1} sx={{ borderRadius: 1, p: 2, height: '100%' }}>
          <Typography fontWeight={600}>{answerText}</Typography>
        </Paper>
      </Grid2>
    </Grid2>
  );
};

const DonatePage = () => {
  const { hash } = useLocation();
  const alreadyScrolled = React.useRef(false);

  const classes = useStyles();
  const { t, i18n } = useTranslation();
  const currentLanguage = i18n.resolvedLanguage;

  const donateSectionSx = {
    width: '100%',
  };

  useEffect(() => {
    // Do not scroll when it's not required.
    if (hash) {
      // Scroll only one time.
      if (!alreadyScrolled.current) {
        const element = document.getElementById(hash.substring(1));
        if (element) {
          element.scrollIntoView({ behavior: 'smooth' });
          alreadyScrolled.current = true;
        }
      }
    }
  }, [hash]);

  return (
    <>
      <ContentHeader title={`${t('menu.about')} > ${t('menu.donate')}`} />
      <ContentBox maxWidth="lg">
        <Grid2
          container
          width="100%"
          gap={6}
          flexDirection="column"
          alignItems="center"
        >
          <Grid2 sx={donateSectionSx}>
            <FundingSection linkToDonatePage={false} fullWidth />
          </Grid2>
          <Grid2 sx={donateSectionSx}>
            <TitledPaper title={t('about.donateHowTo')}>
              <Alert severity="info" sx={{ width: '100%', mb: 2 }}>
                {t('donate.ifPossibleConsiderUsingDirectTransfers')}
              </Alert>
              <Grid2
                container
                gap={2}
                alignItems="stretch"
                justifyContent="space-evenly"
              >
                <Grid2 width="100%" xs={12} sm={12} md={5}>
                  <Stack
                    spacing={2}
                    direction="column"
                    alignItems="center"
                    justify-content="space-between"
                  >
                    <ExternalLink
                      href={
                        currentLanguage === 'fr'
                          ? KKBBTournesolFrUrl
                          : KKBBTournesolEnUrl
                      }
                    >
                      <img
                        src="/logos/KKBB_Logo.png"
                        alt="KissKissBankBank logo"
                        height="90px"
                      />
                    </ExternalLink>
                    <Button
                      variant="contained"
                      href={
                        currentLanguage === 'fr'
                          ? KKBBTournesolFrUrl
                          : KKBBTournesolEnUrl
                      }
                    >
                      {t('donate.donateWithKKBB')}
                    </Button>
                  </Stack>
                </Grid2>
                <Grid2 width="100%" xs={12} sm={12} md={5}>
                  <Stack
                    spacing={2}
                    direction="column"
                    alignItems="center"
                    justify-content="space-between"
                  >
                    <ExternalLink
                      href={paypalDonateTournesolUrl}
                      sx={{ width: '100%' }}
                    >
                      <img
                        src="/logos/PayPal_Logo.svg"
                        alt="PayPal logo"
                        height="90px"
                        width="100%"
                      />
                    </ExternalLink>
                    <Button variant="contained" href={paypalDonateTournesolUrl}>
                      {t('donate.donateWithPaypal')}
                    </Button>
                  </Stack>
                </Grid2>
              </Grid2>
            </TitledPaper>
          </Grid2>
          <Grid2 sx={donateSectionSx}>
            <TitledPaper
              title={t('donate.doYouPreferDirectTransfer')}
              titleId="direct_transfer"
            >
              <Box>
                <Typography variant="h5" sx={{ marginBottom: 1 }}>
                  {t('about.donateByDirectTransferEUR')}
                </Typography>
                <pre className={classes.bankingInfo}>Association Tournesol</pre>
                <pre className={classes.bankingInfo}>Lausanne, Switzerland</pre>
                <pre className={classes.bankingInfo}>
                  IBAN: CH75 0900 0000 1570 7623 1
                </pre>
                <pre className={classes.bankingInfo}>BIC: POFICHBEXXX</pre>
              </Box>
              <Divider sx={{ my: 2 }} />
              <Box>
                <Typography variant="h5" sx={{ marginBottom: 1 }}>
                  {t('about.donateByDirectTransferCHF')}
                </Typography>
                <pre className={classes.bankingInfo}>Association Tournesol</pre>
                <pre className={classes.bankingInfo}>Lausanne, Switzerland</pre>
                <pre className={classes.bankingInfo}>
                  IBAN: CH42 0900 0000 1569 4102 5
                </pre>
                <pre className={classes.bankingInfo}>BIC: POFICHBEXXX</pre>
              </Box>
            </TitledPaper>
          </Grid2>
        </Grid2>
        <Grid2 py={4}>
          <QuestionRow
            questionText={t('donate.whatDoWeDoQuestion')}
            answerText={t('donate.whatDoWeDoAnswer')}
          />
          <QuestionRow
            questionText={t('donate.whatWeWouldDoQuestion')}
            answerText={t('donate.whatWeWouldDoAnswer')}
          />
          <QuestionRow
            questionText={t('donate.howMuchDoWeHaveQuestion')}
            answerText={t('donate.howMuchDoWeHaveAnswer')}
          />
          <QuestionRow
            questionText={t('donate.howMuchWeCurrentlySpendQuestion')}
            answerText={t('donate.howMuchWeCurrentlySpendAnswer')}
          />
          <QuestionRow
            questionText={t('donate.haveWeConsideredQuestion')}
            answerText={t('donate.haveWeConsideredAnswer')}
          />
        </Grid2>
      </ContentBox>
    </>
  );
};

export default DonatePage;
