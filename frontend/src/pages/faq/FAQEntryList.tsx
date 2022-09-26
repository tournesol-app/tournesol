import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Typography } from '@mui/material';
import { PeopleAlt } from '@mui/icons-material';

import { FAQEntry } from 'src/services/openapi';

/**
 * The Entry List section of the FAQ page.
 *
 * Questions are headings with HTML id, allowing them to be quickly reached
 * using anchors.
 */
const FAQEntryList = ({ entries }: { entries: Array<FAQEntry> }) => {
  const { t } = useTranslation();
  return (
    <>
      {entries.length > 20 ? (
        entries.map((entry) => {
          const answerParagraphs = entry.answer.split('\n');
          return (
            <Box key={entry.name} mb={4}>
              <Typography id={entry.name} variant="h4" gutterBottom>
                {entry.question}
              </Typography>

              {/* An answer can be composed of several paragraphs. */}
              {answerParagraphs.map((paragraph, index) => (
                <Typography
                  key={`${entry.name}_p${index}`}
                  paragraph
                  textAlign="justify"
                >
                  {paragraph}
                </Typography>
              ))}
            </Box>
          );
        })
      ) : (
        <>
          <Typography paragraph textAlign="justify">
            {t('faqPage.comeAndAskYourQuestionsOnDiscord')}
          </Typography>
          <Box display="flex" justifyContent="flex-end">
            <Button
              href="https://discord.gg/TvsFB8RNBV"
              target="_blank"
              color="secondary"
              variant="outlined"
              endIcon={<PeopleAlt />}
            >
              {t('faqPage.joinUsOnDiscord')}
            </Button>
          </Box>
        </>
      )}
    </>
  );
};

export default FAQEntryList;
