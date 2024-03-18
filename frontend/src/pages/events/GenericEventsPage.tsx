import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';
import { useHistory, useLocation } from 'react-router-dom';

import { Alert, Box, Typography } from '@mui/material';

import { ContentBox, ContentHeader, Pagination } from 'src/components';
import { useNotifications } from 'src/hooks/useNotifications';
import EventEntryList from 'src/pages/events/EventEntryList';
import { TOLERANCE_PERIOD } from 'src/pages/events/parameters';
import {
  BackofficeService,
  EventTypeEnum,
  TournesolEvent,
} from 'src/services/openapi';

import EventsMenu from './EventsMenu';

interface SortedEventAccumulator {
  past: TournesolEvent[];
  future: TournesolEvent[];
}

interface GenericEventsPageProps {
  title: string;
  selectedMenuItem: string;
  eventType?: EventTypeEnum;
  // An element that will be displayed below the page menu.
  header?: React.ReactElement;
}

const GenericEventsPage = ({
  title,
  selectedMenuItem,
  eventType,
  header,
}: GenericEventsPageProps) => {
  const { t } = useTranslation();
  const { contactAdministrator } = useNotifications();
  const history = useHistory();
  const location = useLocation();

  const [pastEvents, setPastEvents] = useState<Array<TournesolEvent>>([]);
  const [futureEvents, setFutureEvents] = useState<Array<TournesolEvent>>([]);
  const [totalEvents, setTotalEvents] = useState(0);

  const searchParams = new URLSearchParams(location.search);
  const offset = Number(searchParams.get('offset') || 0);
  const limit = 20;

  const handleOffsetChange = (newOffset: number) => {
    searchParams.set('offset', newOffset.toString());
    history.push({ search: searchParams.toString() });
  };

  const displayFutureEvents = offset === 0 || futureEvents.length > 0;

  useEffect(() => {
    async function getEventsEntries() {
      const events = await BackofficeService.backofficeEventsList({
        limit: limit,
        offset: offset,
        eventType: eventType,
      }).catch(() => {
        contactAdministrator('error');
      });

      setTotalEvents(events?.count ?? 0);

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
  }, [contactAdministrator, eventType, offset]);

  return (
    <>
      <ContentHeader title={title} />
      <ContentBox maxWidth="lg">
        <Box mb={4}>
          <EventsMenu selected={selectedMenuItem} />
        </Box>
        {header && header}
        {displayFutureEvents && (
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
        )}
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
        {totalEvents > 0 && (
          <Pagination
            offset={offset}
            count={totalEvents}
            onOffsetChange={handleOffsetChange}
            limit={limit}
          />
        )}
      </ContentBox>
    </>
  );
};

export default GenericEventsPage;
