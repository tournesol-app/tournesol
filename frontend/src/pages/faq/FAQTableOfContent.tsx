import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';

import { FAQEntry } from 'src/services/openapi';

/**
 * The Table of Content section of the FAQ page.
 *
 * Items are anchors allowing to jump directly to the question. The anchor
 * added to the URL is the `FAQEntry.name`.
 */
const FAQTableOfContent = ({
  entries,
  onEntryClick,
}: {
  entries: Array<FAQEntry>;
  onEntryClick: (name: string, scroll?: boolean) => void;
}) => {
  const { t } = useTranslation();

  return (
    <Paper
      square
      sx={{
        color: '#fff',
        p: 2,
        pb: 2,
        mb: 2,
        backgroundColor: 'background.emphatic',
      }}
    >
      <Typography variant="h6">{t('faqPage.tableOfContent')}</Typography>
      <List dense={true}>
        {entries.map((entry) => (
          <ListItemButton
            key={`toc_${entry.name}`}
            component="a"
            onClick={() => onEntryClick(entry.name, true)}
          >
            <ListItemText>{entry.question}</ListItemText>
          </ListItemButton>
        ))}
        {/* Always display an extra entry to explain how to ask more
            questions. */}
        <ListItemButton
          component="a"
          onClick={() => onEntryClick('no_answer_found', true)}
        >
          <ListItemText>{t('faqPage.iDidFindTheAnswers')}</ListItemText>
        </ListItemButton>
      </List>
    </Paper>
  );
};

export default FAQTableOfContent;
