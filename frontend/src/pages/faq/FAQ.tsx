import React, { useEffect, useState } from 'react';

import {
  List,
  ListItemButton,
  ListItemText,
  Paper,
  Typography,
} from '@mui/material';

import { ContentBox, ContentHeader } from 'src/components';
import { FAQEntry, FaqService } from 'src/services/openapi';

const FAQ = () => {
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
  }, []);

  console.log(entries);
  return (
    <>
      <ContentHeader title="Frequently Asked Questions" />
      <ContentBox maxWidth="md">
        <Paper
          square
          sx={{ color: '#fff', p: 2, pb: 2, mb: 2, backgroundColor: '#1282B2' }}
        >
          <Typography variant="h6">Table of Content</Typography>
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
        </Paper>
        {entries.map((entry) => {
          const answerParagraphs = entry.answer.split('\n');
          return (
            <React.Fragment key={entry.name}>
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
            </React.Fragment>
          );
        })}
      </ContentBox>
    </>
  );
};

export default FAQ;
