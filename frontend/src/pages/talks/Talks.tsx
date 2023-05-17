import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { ContentBox, ContentHeader, TitledSection } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import TalkEntryList from 'src/pages/talks/TalkEntryList';
import { TalkEntry, TalksService } from 'src/services/mocks';

const Talks = () => {
  const { t, i18n } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const [pastTalks, setPastTalks] = useState<Array<TalkEntry>>([]);
  const [upcomingTalks, setUpcomingTalks] = useState<Array<TalkEntry>>([]);

  useEffect(() => {
    async function getTalksEntries() {
      try {
        const talks = TalksService.talksList(i18n.language);
        if (talks.results) {
          const today = new Date();

          interface TalkAccumulator {
            pastTalks: TalkEntry[];
            upcomingTalks: TalkEntry[];
          }

          const filteredTalks1 = talks.results.reduce<{
            pastTalks: TalkEntry[];
            upcomingTalks: TalkEntry[];
          }>(
            (acc: TalkAccumulator, talk: TalkEntry) => {
              const talkDate = new Date(talk.date);
              if (talkDate < today) {
                acc.pastTalks.push(talk);
              } else {
                acc.upcomingTalks.push(talk);
              }
              return acc;
            },
            { pastTalks: [], upcomingTalks: [] }
          );
          const pastTalks = filteredTalks1.pastTalks;
          const upcomingTalks = filteredTalks1.upcomingTalks;
          setPastTalks(pastTalks);
          setUpcomingTalks(upcomingTalks);
        }
      } catch (error) {
        contactAdministrator('error');
      }
    }

    getTalksEntries();
  }, [contactAdministrator, setUpcomingTalks, setPastTalks, i18n.language]);

  return (
    <>
      <ContentHeader title="Talks" />
      <ContentBox maxWidth="lg">
        <TitledSection title={t('talksPage.sections.title.upcoming')}>
          <TalkEntryList talks={upcomingTalks} />
        </TitledSection>

        <TitledSection title={t('talksPage.sections.title.past')}>
          <TalkEntryList talks={pastTalks} />
        </TitledSection>
      </ContentBox>
    </>
  );
};

export default Talks;
