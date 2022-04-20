import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container } from '@mui/material';
import { ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { PRESIDENTIELLE_2022_POLL_NAME } from 'src/utils/constants';
import FeedbackPagePresidentielle2022 from './FeedbackPagePresidentielle2022';

const FeedbackPage = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  return (
    <>
      <ContentHeader title={t('myFeedbackPage.title')} />
      <Container sx={{ py: 2 }}>
        {pollName === PRESIDENTIELLE_2022_POLL_NAME && (
          <FeedbackPagePresidentielle2022 />
        )}
      </Container>
    </>
  );
};

export default FeedbackPage;
