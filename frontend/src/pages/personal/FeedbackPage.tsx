import React from 'react';
import { useTranslation } from 'react-i18next';
import { Container } from '@mui/material';
import { ContentHeader } from 'src/components';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { PRESIDENTIELLE_2022_POLL_NAME } from 'src/utils/constants';
import Pres2022FeedbackPage from './Pres2022FeedBackPage';

const FeedbackPage = () => {
  const { t } = useTranslation();
  const { name: pollName } = useCurrentPoll();

  return (
    <>
      <ContentHeader title={t('myFeedbackPage.title')} />
      <Container sx={{ py: 2 }}>
        {pollName === PRESIDENTIELLE_2022_POLL_NAME && <Pres2022FeedbackPage />}
      </Container>
    </>
  );
};

export default FeedbackPage;
