import React, { useEffect, useState } from 'react';
import { useTranslation } from 'react-i18next';

import {
  Box,
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { FAQEntry, FaqService } from 'src/services/openapi';

const FAQ = () => {
  const { t } = useTranslation();
  const [entries, setEntries] = useState<Array<FAQEntry>>([]);

  useEffect(() => {
    async function getFaqEntries() {
      try {
        const faq = await FaqService.faqList({});
        if (faq.results) {
          setEntries(faq.results);
        }
      } catch (error) {
        // do something
      }
    }

    getFaqEntries();
  }, [setEntries]);

  console.log(entries);
  return (
    <>
      <ContentHeader title="Frequently Asked Questions" />
      <ContentBox maxWidth="md">
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

        {entries.length > 0 ? (
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
          <Typography paragraph textAlign="justify">
            {t('faq.comeAndAskYourQuestionsOnDiscord')}
          </Typography>
        )}
      </ContentBox>
    </>
  );
};

export default FAQ;
