import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Collapse,
  Grid,
  IconButton,
  Paper,
  Typography,
} from '@mui/material';
import { KeyboardArrowDown, KeyboardArrowUp, Link } from '@mui/icons-material';

import { useSnackbar } from 'notistack';
import { FAQEntry } from 'src/services/openapi';
import { SNACKBAR_DYNAMIC_FEEDBACK_MS } from 'src/utils/notifications';

interface FAQSingleEntryProps {
  entry: FAQEntry;
  displayed: boolean;
  onVisibilityChange: (name: string, visibilty: boolean) => void;
}

const FAQSingleEntry = ({
  entry,
  displayed,
  onVisibilityChange,
}: FAQSingleEntryProps) => {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();

  const copyUriToClipboard = (
    event: React.MouseEvent<HTMLElement>,
    anchor: string
  ) => {
    const uri = `${location.protocol}//${location.host}${location.pathname}?scrollTo=${anchor}`;
    navigator.clipboard.writeText(uri);
    enqueueSnackbar(t('faqEntryList.questionURLCopied'), {
      variant: 'success',
      autoHideDuration: SNACKBAR_DYNAMIC_FEEDBACK_MS,
    });
  };

  const answerParagraphs = entry.answer.split('\n');

  return (
    <Box mb={4}>
      <Paper square sx={{ p: 2 }}>
        <Grid container>
          <Grid item xs={10}>
            <Typography
              id={entry.name}
              variant="h4"
              gutterBottom
              // Match the IconButton padding to align the two items
              // nicely, even when the title fits on several lines.
              sx={{ pt: 1 }}
            >
              {entry.question}
            </Typography>
          </Grid>
          <Grid item xs={2}>
            <Box
              display="flex"
              flexWrap="wrap"
              alignItems="center"
              justifyContent="flex-end"
              gap={0.5}
            >
              <IconButton
                aria-label="Copy URI to clipboard"
                onClick={(event) => {
                  copyUriToClipboard(event, entry.name);
                }}
              >
                <Link />
              </IconButton>
              <IconButton
                aria-label="Show question's answer"
                onClick={() => {
                  onVisibilityChange(entry.name, !displayed);
                }}
              >
                {displayed ? <KeyboardArrowUp /> : <KeyboardArrowDown />}
              </IconButton>
            </Box>
          </Grid>
        </Grid>

        {answerParagraphs.length > 0 && (
          <Collapse in={displayed} timeout="auto">
            <Box sx={{ 'p:last-child': { mb: 0 } }}>
              {
                // An answer can be composed of several paragraphs.
                answerParagraphs.map((paragraph, index) => (
                  <Typography
                    key={`$a_{entry.name}_p${index}`}
                    paragraph
                    textAlign="justify"
                  >
                    {paragraph}
                  </Typography>
                ))
              }
            </Box>
          </Collapse>
        )}
      </Paper>
    </Box>
  );
};

export default FAQSingleEntry;
