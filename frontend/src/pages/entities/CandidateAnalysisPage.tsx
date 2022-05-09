import React from 'react';
import { Box, Container, Typography } from '@mui/material';
import { Recommendation } from 'src/services/openapi';

interface Props {
  entity: Recommendation;
}

const CandidateAnalysisPage = ({ entity }: Props) => {
  return (
    <Container>
      <Box py={2}>
        <Typography variant="h3">{entity.metadata.name}</Typography>
      </Box>
    </Container>
  );
};

export default CandidateAnalysisPage;
