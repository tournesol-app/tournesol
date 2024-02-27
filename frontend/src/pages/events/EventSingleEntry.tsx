import React from 'react';
import { Trans, useTranslation } from 'react-i18next';

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
} from '@mui/icons-material';

import { TOLERANCE_PERIOD } from 'src/pages/talks/parameters';
import { TalkEntry } from 'src/services/openapi';
import { localDate, localTime } from 'src/utils/datetime';
import { extractVideoId } from 'src/utils/video';

function isPast(event: TalkEntry) {
  if (!event.date) {
    return false;
  }

  const now = new Date();
  return new Date(event.date) < new Date(now.getTime() - TOLERANCE_PERIOD);
}

function isLive(event: TalkEntry) {
  if (!event.date) {
    return false;
  }

  const eventDate = new Date(event.date);
  const now = new Date();
  return (
    eventDate < now && now < new Date(eventDate.getTime() + TOLERANCE_PERIOD)
  );
}

const EventHeading = ({ event }: { event: TalkEntry }) => {
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
      p={2}
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
          <Typography variant="h4">
            {headingLink ? (
              <Link
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
              </Link>
            ) : (
              event.title
            )}
          </Typography>
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

const EventImagery = ({ event }: { event: TalkEntry }) => {
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
        <a className="no-decoration" href={imageLink}>
          <img
            src={imgSrc}
            style={{
              width: '320px',
              height: '180px',
              borderRadius: '4px',
            }}
          />
        </a>
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

const EventSingleEntry = ({ event }: { event: TalkEntry }) => {
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
        <Typography variant="h6" color="secondary" gutterBottom>
          {event.speakers && (
            <Trans t={t} i18nKey="eventsPage.by">
              By {{ speaker: event.speakers }}
            </Trans>
          )}
        </Typography>
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
            rel="noopener"
            target="_blank"
          >
            {eventIsPast ? t('eventsPage.replay') : t('eventsPage.join')}
          </Button>
        </Box>
      )}
    </Paper>
  );
};

export default EventSingleEntry;
