import React from 'react';
import { useTranslation } from 'react-i18next';

import { Box, Button, Typography } from '@mui/material';
import { PeopleAlt } from '@mui/icons-material';

import FAQSingleEntry from 'src/pages/faq/FAQSingleEntry';
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
const FAQEntryList = ({
  entries,
  displayedEntries,
  onEntryVisibilityChange,
}: {
  entries: Array<FAQEntry>;
  displayedEntries: Array<string>;
  onEntryVisibilityChange: (name: string, visibilty: boolean) => void;
}) => {
  const { t } = useTranslation();

  return (
    <>
      {entries.map((entry) => (
        <FAQSingleEntry
          key={`q_${entry.name}`}
          entry={entry}
          displayed={displayedEntries.includes(entry.name)}
          onVisibilityChange={onEntryVisibilityChange}
        />
      ))}

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
          color="secondary"
          variant="outlined"
          startIcon={<PeopleAlt />}
        >
          {t('faqPage.joinUsOnDiscord')}
        </Button>
      </Box>
    </>
  );
};

export default FAQEntryList;
