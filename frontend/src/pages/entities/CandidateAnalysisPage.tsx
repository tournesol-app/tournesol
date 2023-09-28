import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import { Box, Button, Container, Grid, Paper, Typography } from '@mui/material';

import EntityImagery from 'src/components/entity/EntityImagery';
import EntityCardTitle from 'src/components/entity/EntityCardTitle';
import EntityCardScores from 'src/components/entity/EntityCardScores';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { Recommendation, TypeEnum } from 'src/services/openapi';
import CriteriaBarChart from 'src/components/CriteriaBarChart';

interface Props {
  entity: Recommendation;
}

const CandidateAnalysisPage = ({ entity: reco }: Props) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();
  const entity = reco.entity;

  return (
    <Container sx={{ maxWidth: '1000px !important' }}>
      <Box py={2}>
        {/* Top level section, containing links and maybe more in the future. */}
        <Box mb={2} display="flex" justifyContent="flex-end">
          <Button
            color="secondary"
            variant="outlined"
            component={RouterLink}
            to={`${baseUrl}/recommendations`}
          >
            {t('entityAnalysisPage.candidate.goToGlobalRanking')}
          </Button>
        </Box>

        {/* Entity section, with its picture, title and scores. */}
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <EntityImagery entity={entity} compact={true} />
          </Grid>
          <Grid item xs={12}>
            <Paper>
              <Box p={1}>
                <EntityCardTitle
                  uid={entity.uid}
                  title={entity.metadata.name}
                  compact={false}
                />
                <EntityCardScores
                  result={reco}
                  showTournesolScore={
                    entity.type !== TypeEnum.CANDIDATE_FR_2022
                  }
                  showTotalScore={entity.type === TypeEnum.CANDIDATE_FR_2022}
                />
              </Box>
            </Paper>
          </Grid>

          {/* Data visualization. */}
          <Grid item xs={12} sm={12} md={6}>
            <Paper>
              <Box
                p={1}
                bgcolor="rgb(238, 238, 238)"
                display="flex"
                justifyContent="center"
              >
                <Typography variant="h5">
                  {t('entityAnalysisPage.chart.criteriaScores.title')}
                </Typography>
              </Box>
              <Box p={1}>
                <CriteriaBarChart reco={reco} />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default CandidateAnalysisPage;
