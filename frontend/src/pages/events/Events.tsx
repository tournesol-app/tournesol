import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import { Alert, Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import EventEntryList from 'src/pages/events/EventEntryList';
import { TOLERANCE_PERIOD } from 'src/pages/talks/parameters';
import { BackofficeService, TournesolEvent } from 'src/services/openapi';

import EventsMenu from './EventsMenu';

interface SortedEventAccumulator {
  past: TournesolEvent[];
  future: TournesolEvent[];
}

const Events = () => {
  const { t } = useTranslation();
  const { contactAdministrator } = useNotifications();

  const [pastEvents, setPastEvents] = useState<Array<TournesolEvent>>([]);
  const [futureEvents, setFutureEvents] = useState<Array<TournesolEvent>>([]);

  useEffect(() => {
    async function getEventsEntries() {
      const events = await BackofficeService.backofficeEventsList({
        limit: 100,
      }).catch(() => {
        contactAdministrator('error');
      });

      if (events && events.results) {
        const now = new Date();

        const sortedEvents = events.results.reduce<{
          past: TournesolEvent[];
          future: TournesolEvent[];
        }>(
          (acc: SortedEventAccumulator, event: TournesolEvent) => {
            // Do not display not scheduled Talk.
            if (!event.date) {
              return acc;
            }

            const eventDate = new Date(event.date);

            if (eventDate < new Date(now.getTime() - TOLERANCE_PERIOD)) {
              acc.past.push(event);
            } else {
              acc.future.push(event);
            }
            return acc;
          },
          { past: [], future: [] }
        );

        setPastEvents(sortedEvents.past);
        setFutureEvents(sortedEvents.future);
      }
    }

    getEventsEntries();
  }, [contactAdministrator]);

  return (
    <>
      <ContentHeader title={t('eventsPage.title')} />
      <ContentBox maxWidth="lg">
        <Box mb={4}>
          <EventsMenu selected="all" />
        </Box>
        <Box mb={4}>
          <Typography
            variant="h6"
            component="h3"
            mb={2}
            borderBottom="1px solid #E7E5DB"
          >
            {t('eventsPage.upcomingEvents')}
          </Typography>

          {futureEvents && futureEvents.length > 0 ? (
            <EventEntryList events={futureEvents} />
          ) : (
            <Alert severity="info">
              {t('eventsPage.noEventsPlannedForTheMoment')}
            </Alert>
          )}
        </Box>
        {pastEvents && pastEvents.length > 0 && (
          <Box mb={4}>
            <Typography
              variant="h6"
              component="h3"
              mb={2}
              borderBottom="1px solid #E7E5DB"
            >
              {t('eventsPage.pastEvents')}
            </Typography>
            <EventEntryList events={pastEvents} />
          </Box>
        )}
      </ContentBox>
    </>
  );
};

export default Events;
