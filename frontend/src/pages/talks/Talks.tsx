import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Typography } from '@mui/material';

import { ContentBox, ContentHeader, TitledSection } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import TalkEntryList from 'src/pages/talks/TalkEntryList';
import { TalkEntry, TalksService } from 'src/services/mocks';

interface SortedTalkAccumulator {
  past: TalkEntry[];
  future: TalkEntry[];
}

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
        <TitledSection
          title={t('talksPage.upcomingEvents')}
          titleComponent="h3"
        >
          {upcomingTalks && upcomingTalks.length > 0 ? (
            <TalkEntryList talks={upcomingTalks} />
          ) : (
            <Typography>{t('talksPage.sections.empty')}</Typography>
          )}
        </TitledSection>

        {pastTalks && pastTalks.length > 0 && (
          <TitledSection title={t('talksPage.pastEvents')} titleComponent="h3">
            <TalkEntryList talks={pastTalks} />
          </TitledSection>
        )}
      </ContentBox>
    </>
  );
};

export default Talks;
