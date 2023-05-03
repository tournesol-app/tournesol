import React, { useState } from 'react';
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
}

const FAQSingleEntry = ({ entry }: FAQSingleEntryProps) => {
  const { t } = useTranslation();
  const { enqueueSnackbar } = useSnackbar();

  const [answerFolded, setAnswerFolded] = useState(
    !(location.hash.substring(1) === entry.name)
  );

  const copyUriToClipboard = (
    event: React.MouseEvent<HTMLElement>,
    anchor: string
  ) => {
    const uri = `${location.protocol}//${location.host}${location.pathname}#${anchor}`;
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
          <Grid item xs={11}>
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
          <Grid item xs={1}>
            <Box
              display="flex"
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
                  setAnswerFolded(!answerFolded);
                }}
              >
                {answerFolded ? <KeyboardArrowDown /> : <KeyboardArrowUp />}
              </IconButton>
            </Box>
          </Grid>
        </Grid>

        {answerParagraphs.length > 0 && (
          <Collapse in={!answerFolded} timeout="auto" unmountOnExit>
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
