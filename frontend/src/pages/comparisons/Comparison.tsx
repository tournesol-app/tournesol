import React from 'react';
import { useTranslation } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';

import { ContentHeader } from 'src/components';
import Comparison from 'src/features/comparisons/Comparison';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    height: '100%',
  },
  centering: {
    display: 'flex',
    alignItems: 'center',
    flexDirection: 'column',
    paddingTop: 16,
  },
}));

const ComparisonPage = () => {
  const { t } = useTranslation();
  const classes = useStyles();

  return (
    <>
      <ContentHeader title={t('comparison.submitAComparison')} />
      <div className={`${classes.root} ${classes.centering}`}>
        <Comparison />
      </div>
    </>
  );
};

export default ComparisonPage;
