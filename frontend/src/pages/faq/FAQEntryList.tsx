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
 *
 * An extra entry is displayed after the provided `entries`, inviting the
 * users to join Discord if they didn't find the answer to their questions.
 */
const FAQEntryList = ({ entries }: { entries: Array<FAQEntry> }) => {
  const { t } = useTranslation();
  return (
    <>
      {entries.map((entry) => {
        const answerParagraphs = entry.answer.split('\n');
        return (
          <Box key={`q_${entry.name}`} mb={4}>
            <Typography id={entry.name} variant="h4" gutterBottom>
              {entry.question}
            </Typography>

            {/* An answer can be composed of several paragraphs. */}
            {answerParagraphs.map((paragraph, index) => (
              <Typography
                key={`$a_{entry.name}_p${index}`}
                paragraph
                textAlign="justify"
              >
                {paragraph}
              </Typography>
            ))}
          </Box>
        );
      })}

      {/* Always display an extra entry to explain how to ask more questions. */}
      <Box mb={4}>
        <Typography id="no_answer_found" variant="h4" gutterBottom>
          {t('faqPage.iDidFindTheAnswers')}
        </Typography>

        <Typography paragraph textAlign="justify">
          {t('faqPage.comeAndAskYourQuestionsOnDiscord')}
        </Typography>
      </Box>
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
  );
};

export default FAQEntryList;
