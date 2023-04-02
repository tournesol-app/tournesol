import React from 'react';

import { useTranslation } from 'react-i18next';
import { useParams } from 'react-router-dom';

import { ContentBox, ContentHeader } from 'src/components';
import ProofOfVote from 'src/pages/personal/feedback/ProofOfVote';

const ProofByKeywordPage = () => {
  const { t } = useTranslation();

  const { keyword } = useParams<{ keyword: string }>();

  return (
    <>
      <ContentHeader title={t('proofByKeyword.proofByKeyword')} />
      <ContentBox maxWidth="md">
        <ProofOfVote
          keyword={keyword}
          label={t('proofByKeyword.proofFor') + ` ${keyword}`}
        />
      </ContentBox>
    </>
  );
};

export default ProofByKeywordPage;
