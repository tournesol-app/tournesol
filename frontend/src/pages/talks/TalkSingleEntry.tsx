import React from 'react';

import { Box, Grid, Paper, Typography } from '@mui/material';
import { TalkEntry } from 'src/services/mocks';
import { extractVideoId } from 'src/utils/video';
import { useTranslation } from 'react-i18next';

const TalkSingleEntry = ({ talk }: { talk: TalkEntry }) => {
  const { i18n } = useTranslation();

  const abstractParagraphs = talk.abstract.split('\n');

  function isPast(talk: TalkEntry) {
    return new Date(talk.date) < new Date();
  }

  const title = (
    <Box display="flex" gap={2}>
      <Typography variant="h4">{talk.title}</Typography>
    </Box>
  );

  const formatDate = (dateString: string) => {
    if (i18n.language == 'fr') {
      const date = new Date(dateString);

      const day = date.getDate();
      const month = date.getMonth() + 1;
      const year = date.getFullYear();

      const formattedDate = `${day < 10 ? '0' + day : day}/${
        month < 10 ? '0' + month : month
      }/${year}`;

      return formattedDate;
    }
    return dateString;
  };

  const talkContent = (
    <>
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
        <Grid container alignItems="center" flexWrap="nowrap">
          <Grid item xs={9}>
            <Typography variant="h4" sx={{ maxWidth: '100%' }}>
              {title}
            </Typography>
          </Grid>
          <Grid item xs={3}>
            <Typography
              variant="body1"
              sx={{ textAlign: 'right', fontSize: '1em' }}
            >
              {formatDate(talk.date)}
            </Typography>
          </Grid>
        </Grid>
      </Box>
      <Box p={2} sx={{ overflow: 'auto' }}>
        <Box
          className="image-wrapper"
          display="flex"
          sx={{
            maxWidth: '240px',
            marginRight: { sm: '10px' },
            borderRadius: '4px',
            float: 'left',
          }}
        >
          {isPast(talk) && talk.youtube_link ? (
            <img
              className="full-width entity-thumbnail"
              src={`https://i.ytimg.com/vi/${extractVideoId(
                talk.youtube_link
              )}/mqdefault.jpg`}
              style={{
                width: '240px',
                height: 'auto',
                borderRadius: '4px',
              }}
            />
          ) : (
            <img
              className="full-width entity-thumbnail"
              src={`/images/coming-soon.jpg`}
              style={{
                width: '240px',
                height: 'auto',
                borderRadius: '4px',
              }}
            />
          )}
        </Box>

        {abstractParagraphs.map((abstractParagraph, index) => (
          <Typography
            key={`$p_${talk.title}_p${index}`}
            textAlign="justify"
            paragraph
          >
            {abstractParagraph}
          </Typography>
        ))}
      </Box>
    </>
  );

  return (
    <>
      {talk.invitation_link || talk.youtube_link ? (
        <a
          className="no-decoration"
          href={isPast(talk) ? talk.youtube_link : talk.invitation_link}
        >
          <Paper sx={{ mb: 2 }}>{talkContent}</Paper>
        </a>
      ) : (
        <Paper sx={{ mb: 2 }}>{talkContent}</Paper>
      )}
    </>
  );
};

export default TalkSingleEntry;
