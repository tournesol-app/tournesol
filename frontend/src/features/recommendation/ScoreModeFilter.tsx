import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import { Tooltip } from '@mui/material';
import { HelpOutline } from '@mui/icons-material';

import { ChoicesFilterSection, InternalLink } from 'src/components';
import { ScoreModeEnum } from 'src/utils/api/recommendations';

interface Props {
  value: string;
  onChange: (value: string) => void;
}

const helpIcon = <HelpOutline fontSize="inherit" sx={{}} />;

function ScoreModeFilter(props: Props) {
  const { t } = useTranslation();

  const scoreModeChoices = {
    [ScoreModeEnum.DEFAULT]: (
      <Tooltip title={t('filter.scoreMode.default.description')}>
        <span>
          {t('filter.scoreMode.default.label')} {helpIcon}
        </span>
      </Tooltip>
    ),
    [ScoreModeEnum.ALL_EQUAL]: (
      <Tooltip title={t('filter.scoreMode.allEqual.description')}>
        <span>
          {t('filter.scoreMode.allEqual.label')} {helpIcon}
        </span>
      </Tooltip>
    ),
    [ScoreModeEnum.TRUSTED_ONLY]: (
      <Tooltip
        title={
          <Trans t={t} i18nKey="filter.scoreMode.trustedOnly.description">
            Only accounts associated with{' '}
            <InternalLink
              color="primary"
              target="_blank"
              to="/about/trusted_domains"
            >
              a trusted email address
            </InternalLink>
            are considered
          </Trans>
        }
      >
        <span>
          {t('filter.scoreMode.trustedOnly.label')} {helpIcon}
        </span>
      </Tooltip>
    ),
  };

  return (
    <ChoicesFilterSection
      title={t('filter.scoreModeSection')}
      choices={scoreModeChoices}
      radio
      {...props}
    />
  );
}

export default ScoreModeFilter;
