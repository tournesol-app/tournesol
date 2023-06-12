import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Button, Link, Paper, Typography } from '@mui/material';
import { Email } from '@mui/icons-material';

import { ContentBox, ContentHeader } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import TalkEntryList from 'src/pages/talks/TalkEntryList';
import { TalkEntry, TalksService } from 'src/services/mocks';
import { tournesolTalksMailingListUrl } from 'src/utils/url';

interface SortedTalkAccumulator {
  past: TalkEntry[];
  future: TalkEntry[];
}

const IntroductionPaper = () => {
  const { t } = useTranslation();

  return (
    <Paper sx={{ p: 2, mb: 4 }}>
      <Typography component="h2" variant="h4" gutterBottom>
        {t('talksPage.whatAreTournesolTalks')}
      </Typography>
      <Typography paragraph>
        {t('talksPage.tournesolTalksIntroduction')}
      </Typography>
      <Box display="flex" justifyContent="flex-end">
        <Button
          size="small"
          variant="contained"
          component={Link}
          href={tournesolTalksMailingListUrl}
          startIcon={<Email />}
        >
          {t('talksPage.beInformedOfUpcomingEvents')}
        </Button>
      </Box>
    </Paper>
  );
};

const Talks = () => {
  const { t, i18n } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const [pastTalks, setPastTalks] = useState<Array<TalkEntry>>([]);
  const [upcomingTalks, setUpcomingTalks] = useState<Array<TalkEntry>>([]);

  useEffect(() => {
    async function getTalksEntries() {
      try {
        const talks = TalksService.talksList(i18n.language);

        if (!talks.results || talks.results?.length === 0) {
          return;
        }

        const now = new Date();

        const sortedTalks = talks.results.reduce<{
          past: TalkEntry[];
          future: TalkEntry[];
        }>(
          (acc: SortedTalkAccumulator, talk: TalkEntry) => {
            const talkDate = new Date(talk.date);
            if (talkDate < now) {
              acc.past.push(talk);
            } else {
              acc.future.push(talk);
            }
            return acc;
          },
          { past: [], future: [] }
        );

        setPastTalks(sortedTalks.past);
        setUpcomingTalks(sortedTalks.future);

        // TODO: when the talks API will be available, make this try/catch
        // wrap only the API call, instead of the whole function.
      } catch (error) {
        contactAdministrator('error');
      }
    }

    getTalksEntries();
  }, [contactAdministrator, i18n.language]);

  return (
    <>
      <ContentHeader title={t('talksPage.title')} />
      <ContentBox maxWidth="lg">
        <IntroductionPaper />
        <Box mb={4}>
          <Typography
            variant="h6"
            component="h3"
            mb={2}
            borderBottom="1px solid #E7E5DB"
          >
            {t('talksPage.upcomingEvents')}
          </Typography>

          {upcomingTalks && upcomingTalks.length > 0 ? (
            <TalkEntryList talks={upcomingTalks} />
          ) : (
            <Alert severity="info">
              {t('talksPage.noTalksInTheNearFuture')}
            </Alert>
          )}
        </Box>
        {pastTalks && pastTalks.length > 0 && (
          <Box mb={4}>
            <Typography
              variant="h6"
              component="h3"
              mb={2}
              borderBottom="1px solid #E7E5DB"
            >
              {t('talksPage.pastEvents')}
            </Typography>

            <TalkEntryList talks={pastTalks} />
          </Box>
        )}
      </ContentBox>
    </>
  );
};

export default Talks;
