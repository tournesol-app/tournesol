import React from 'react';

import { Box, Paper, Typography } from '@mui/material';
import { TalkEntry } from 'src/services/mocks';
import { extractVideoId } from 'src/utils/video';
import { useTranslation } from 'react-i18next';

const TalkSingleEntry = ({ talk }: { talk: TalkEntry; compact?: boolean }) => {
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

  return (
    <>
      <a
        className="no-decoration"
        href={isPast(talk) ? talk.youtube_link : talk.invitation_link}
      >
        <Paper sx={{ mb: 2 }}>
          <Box
            id={talk.uid}
            p={2}
            color="#fff"
            bgcolor="background.emphatic"
            sx={{
              borderTopLeftRadius: 'inherit',
              borderTopRightRadius: 'inherit',
              display: 'flex',
              flexWrap: 'wrap',
              justifyContent: 'space-between',
            }}
          >
            <Typography variant="h4">{title}</Typography>
            <Box>{formatDate(talk.date)}</Box>
          </Box>
          <Box
            className="image-wrapper"
            p={2}
            display="flex"
            sx={{
              flexWrap: 'wrap',
            }}
          >
            <Box
              sx={{
                flex: '0 0 100%',
                maxWidth: '240px',
                marginRight: { sm: '10px' },
                borderRadius: '4px',
              }}
            >
              {isPast(talk) ? (
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
                key={`$p_{talk.title}_p${index}`}
                textAlign="justify"
                sx={{
                  fontSize: '0.8em',
                  marginBottom: '10px',
                }}
              >
                {abstractParagraph}
              </Typography>
            ))}
          </Box>
        </Paper>
      </a>
    </>
  );
};

export default TalkSingleEntry;
