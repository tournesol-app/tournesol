import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Grid,
  Paper,
  Typography,
  Link,
  Button,
  Chip,
} from '@mui/material';
import {
  FiberManualRecord,
  PersonAddAlt1,
  PlayArrow,
  Science,
  YouTube,
} from '@mui/icons-material';

import { ExternalLink } from 'src/components';
import { TOLERANCE_PERIOD } from 'src/pages/events/parameters';
import { EventTypeEnum, TournesolEvent } from 'src/services/openapi';
import { localDate, localTime } from 'src/utils/datetime';
import { extractVideoId } from 'src/utils/video';

function isPast(event: TournesolEvent) {
  if (!event.date) {
    return false;
  }

  const now = new Date();
  return new Date(event.date) < new Date(now.getTime() - TOLERANCE_PERIOD);
}

function isLive(event: TournesolEvent) {
  if (!event.date) {
    return false;
  }

  const eventDate = new Date(event.date);
  const now = new Date();
  return (
    eventDate < now && now < new Date(eventDate.getTime() + TOLERANCE_PERIOD)
  );
}

const EventTypeLabel = ({ event }: { event: TournesolEvent }) => {
  return (
    <>
      {event.event_type === EventTypeEnum.LIVE && (
        <Box display="flex" gap={1} alignItems="center">
          <YouTube fontSize="small" />
          <Typography variant="body2">Tournesol Live</Typography>
        </Box>
      )}
      {event.event_type === EventTypeEnum.TALK && (
        <Box display="flex" gap={1} alignItems="center">
          <Science fontSize="small" />
          <Typography variant="body2">Tournesol Talk</Typography>
        </Box>
      )}
    </>
  );
};

const EventHeading = ({ event }: { event: TournesolEvent }) => {
  const { t } = useTranslation();

  let headingLink;
  if (isPast(event) && event.youtube_link) {
    headingLink = event.youtube_link;
  } else if (!isPast(event) && event.invitation_link) {
    headingLink = event.invitation_link;
  }

  let displayedDatetime;

  // We display the local date according to the Europe/Paris timezone.
  if (event.date_as_tz_europe_paris) {
    const date = localDate(event.date_as_tz_europe_paris);
    const time = localTime(event.date_as_tz_europe_paris);

    if (date) {
      displayedDatetime = date;

      if (!isPast(event) && time) {
        displayedDatetime += ` ${time} Europe/Paris`;
      }
    }
  }

  return (
    <Box
      id={event.name}
      px={2}
      py="12px"
      color="#fff"
      bgcolor="background.emphatic"
      sx={{
        borderTopLeftRadius: 'inherit',
        borderTopRightRadius: 'inherit',
      }}
    >
      <Grid
        container
        justifyContent="space-between"
        alignItems="center"
        spacing={1}
      >
        <Grid item>
          <Box display="flex" flexDirection="column">
            <Typography variant="h4">
              {headingLink ? (
                <ExternalLink
                  href={headingLink}
                  sx={{
                    color: '#fff',
                    textDecoration: 'none',
                    '&:hover': {
                      textDecoration: 'underline',
                    },
                  }}
                >
                  {event.title}
                </ExternalLink>
              ) : (
                event.title
              )}
            </Typography>
            <EventTypeLabel event={event} />
          </Box>
        </Grid>
        {displayedDatetime && (
          <Grid item>
            <Box display="flex" alignItems="center" gap={1}>
              {isLive(event) && (
                <Chip
                  label={t('eventsPage.live')}
                  color="primary"
                  icon={<FiberManualRecord fontSize="small" color="error" />}
                />
              )}
              <Typography variant="body1">{displayedDatetime}</Typography>
            </Box>
          </Grid>
        )}
      </Grid>
    </Box>
  );
};

const EventImagery = ({ event }: { event: TournesolEvent }) => {
  const eventIsPast = isPast(event);

  const imgSrc =
    eventIsPast && event.youtube_link
      ? `https://i.ytimg.com/vi/${extractVideoId(
          event.youtube_link
        )}/mqdefault.jpg`
      : '/svg/Watering.svg';

  let imageLink;
  if (eventIsPast && event.youtube_link) {
    imageLink = event.youtube_link;
  }

  if (!eventIsPast && event.invitation_link) {
    imageLink = event.invitation_link;
  }

  return (
    <Box
      display="flex"
      sx={{
        maxWidth: '320px',
        marginRight: { xs: 0, sm: 2 },
        marginBottom: { xs: 2, sm: 0 },
        borderRadius: '4px',
        float: { xs: 'none', sm: 'left' },
      }}
    >
      {imageLink ? (
        <ExternalLink href={imageLink}>
          <img
            src={imgSrc}
            style={{
              width: '320px',
              height: '180px',
              borderRadius: '4px',
            }}
          />
        </ExternalLink>
      ) : (
        <img
          src={imgSrc}
          style={{
            width: '320px',
            height: '180px',
            borderRadius: '4px',
          }}
        />
      )}
    </Box>
  );
};

const EventSingleEntry = ({ event }: { event: TournesolEvent }) => {
  const { t } = useTranslation();

  const eventIsPast = isPast(event);
  const abstractParagraphs = event.abstract ? event.abstract.split('\n') : [];

  let actionLink;
  if (eventIsPast && event.youtube_link) {
    actionLink = event.youtube_link;
  }

  if (!eventIsPast && event.invitation_link) {
    actionLink = event.invitation_link;
  }

  return (
    <Paper>
      <EventHeading event={event} />
      <Box p={2} sx={{ overflow: 'auto' }}>
        <EventImagery event={event} />
        {event.speakers && (
          <Typography variant="h6" color="secondary" gutterBottom>
            {event.speakers}
          </Typography>
        )}
        {abstractParagraphs.map((abstractParagraph, index) => (
          <Typography
            key={`${event.title}_p${index}`}
            textAlign="justify"
            paragraph
          >
            {abstractParagraph}
          </Typography>
        ))}
      </Box>
      {actionLink && (
        <Box p={2} pt={0} display="flex" justifyContent="flex-end">
          <Button
            size="small"
            color="secondary"
            variant="outlined"
            startIcon={eventIsPast ? <PlayArrow /> : <PersonAddAlt1 />}
            component={Link}
            href={actionLink}
          >
            {eventIsPast ? t('eventsPage.replay') : t('eventsPage.join')}
          </Button>
        </Box>
      )}
    </Paper>
  );
};

export default EventSingleEntry;
