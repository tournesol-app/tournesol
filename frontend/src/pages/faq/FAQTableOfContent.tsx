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
const FAQTableOfContent = ({ entries }: { entries: Array<FAQEntry> }) => {
  const { t } = useTranslation();

  return (
    <Paper
      square
      sx={{ color: '#fff', p: 2, pb: 2, mb: 2, backgroundColor: '#1282B2' }}
    >
      <Typography variant="h6">{t('faq.tableOfContent')}</Typography>

      {entries.length > 0 ? (
        <List dense={true}>
          {entries.map((entry) => (
            <ListItemButton
              key={entry.name}
              component="a"
              href={`#${entry.name}`}
            >
              <ListItemText>{entry.question}</ListItemText>
            </ListItemButton>
          ))}
        </List>
      ) : (
        <Typography sx={{ mt: 2 }}>
          {t('faq.itSeemsThereIsNoQuestionInFaq')}
        </Typography>
      )}
    </Paper>
  );
};

export default FAQTableOfContent;
