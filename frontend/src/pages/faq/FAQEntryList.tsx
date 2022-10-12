import React from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  Button,
  Grid,
  IconButton,
  Paper,
  Typography,
} from '@mui/material';
import { Link, PeopleAlt } from '@mui/icons-material';

import { useSnackbar } from 'notistack';
import { FAQEntry } from 'src/services/openapi';
import { SNACKBAR_DYNAMIC_FEEDBACK_MS } from 'src/utils/notifications';

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
  const { enqueueSnackbar } = useSnackbar();

  const copyUriToClipboard = (
    event: React.MouseEvent<HTMLElement>,
    anchor: string
  ) => {
    navigator.clipboard.writeText(window.location.toString() + `#${anchor}`);
    enqueueSnackbar(t('faqEntryList.urlOfTheQuestionCopied'), {
      variant: 'success',
      autoHideDuration: SNACKBAR_DYNAMIC_FEEDBACK_MS,
    });
  };

  return (
    <>
      {entries.map((entry) => {
        const answerParagraphs = entry.answer.split('\n');
        return (
          <Box key={`q_${entry.name}`} mb={4}>
            <Paper square>
              <Box p={2} pb="1px">
                <Grid container>
                  <Grid item xs={11}>
                    <Typography id={entry.name} variant="h4" gutterBottom>
                      {entry.question}
                    </Typography>
                  </Grid>
                  <Grid item xs={1}>
                    <Box
                      display="flex"
                      alignItems="center"
                      justifyContent="flex-end"
                    >
                      <IconButton
                        aria-label="Copy URI to clipboard"
                        onClick={(event) => {
                          copyUriToClipboard(event, entry.name);
                        }}
                      >
                        <Link />
                      </IconButton>
                    </Box>
                  </Grid>
                </Grid>

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
            </Paper>
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
