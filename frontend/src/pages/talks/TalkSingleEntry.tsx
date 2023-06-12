import React from 'react';

import { Box, Grid, Paper, Typography, Link } from '@mui/material';

import { TalkEntry } from 'src/services/mocks';
import { extractVideoId } from 'src/utils/video';

const toPaddedString = (num: number): string => {
  return num.toString().padStart(2, '0');
};

function isPast(talk: TalkEntry) {
  return new Date(talk.date) < new Date();
}

const TalkHeading = ({ talk }: { talk: TalkEntry }) => {
  let headingLink;
  if (isPast(talk) && talk.youtube_link) {
    headingLink = talk.youtube_link;
  } else if (!isPast(talk) && talk.invitation_link) {
    headingLink = talk.invitation_link;
  }

  let displayedDate;
  const talkDate = new Date(talk.date);

  if (talk.date) {
    displayedDate = `${talkDate.getUTCFullYear()}-${toPaddedString(
      talkDate.getUTCMonth() + 1
    )}-${toPaddedString(talkDate.getUTCDate())}`;
  }

  if (!isPast(talk)) {
    displayedDate += ` ${toPaddedString(
      talkDate.getUTCHours()
    )}:${toPaddedString(talkDate.getUTCMinutes())} CET`;
  }

  return (
    <Box
      id={talk.name}
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
                {talk.title}
              </Link>
            ) : (
              talk.title
            )}
          </Typography>
        </Grid>
        <Grid item>
          <Typography variant="body1">{displayedDate}</Typography>
        </Grid>
      </Grid>
    </Box>
  );
};

const TalkImagery = ({ talk }: { talk: TalkEntry }) => {
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
      {isPast(talk) && talk.youtube_link ? (
        <img
          src={`https://i.ytimg.com/vi/${extractVideoId(
            talk.youtube_link
          )}/mqdefault.jpg`}
          style={{
            width: '320px',
            height: 'auto',
            borderRadius: '4px',
          }}
        />
      ) : (
        <img
          src="/svg/Watering.svg"
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

const TalkSingleEntry = ({ talk }: { talk: TalkEntry }) => {
  const abstractParagraphs = talk.abstract.split('\n');

  return (
    <Paper>
      <TalkHeading talk={talk} />
      <Box p={2} sx={{ overflow: 'auto' }}>
        {talk.invitation_link || talk.youtube_link ? (
          <a
            className="no-decoration"
            href={isPast(talk) ? talk.youtube_link : talk.invitation_link}
          >
            <TalkImagery talk={talk} />
          </a>
        ) : (
          <TalkImagery talk={talk} />
        )}

        {abstractParagraphs.map((abstractParagraph, index) => (
          <Typography
            key={`${talk.title}_p${index}`}
            textAlign="justify"
            paragraph
          >
            {abstractParagraph}
          </Typography>
        ))}
      </Box>
    </Paper>
  );
};

export default TalkSingleEntry;
