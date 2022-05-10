import React from 'react';
import { useTranslation } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';

import { Box, Button, Container, Grid, Paper } from '@mui/material';

import EntityImagery from 'src/components/entity/EntityImagery';
import EntityCardTitle from 'src/components/entity/EntityCardTitle';
import EntityCardScores from 'src/components/entity/EntityCardScores';
import { useCurrentPoll } from 'src/hooks/useCurrentPoll';
import { Recommendation } from 'src/services/openapi';

interface Props {
  entity: Recommendation;
}

const CandidateAnalysisPage = ({ entity }: Props) => {
  const { t } = useTranslation();
  const { baseUrl } = useCurrentPoll();

  return (
    <Container>
      <Box py={2}>
        <Box display="flex" justifyContent="flex-end">
          <Button
            color="secondary"
            variant="outlined"
            component={RouterLink}
            to={`${baseUrl}/recommendations`}
          >
            {t('entityAnalysisPage.candidate.goToGlobalRanking')}
          </Button>
        </Box>
        <Grid container spacing={2}>
          <Grid item xs={12}>
            <EntityImagery entity={entity} compact={true} />
          </Grid>
          <Grid item xs={12}>
            <Paper>
              <Box p={1}>
                <EntityCardTitle title={entity.metadata.name} compact={false} />
                <EntityCardScores
                  entity={entity}
                  showTournesolScore={false}
                  showTotalScore={true}
                />
              </Box>
            </Paper>
          </Grid>
        </Grid>
      </Box>
    </Container>
  );
};

export default CandidateAnalysisPage;
