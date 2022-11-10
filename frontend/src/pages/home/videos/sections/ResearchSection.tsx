import React from 'react';
import { Link as RouterLink } from 'react-router-dom';
import { Trans, useTranslation } from 'react-i18next';

import {
  Box,
  Divider,
  Grid,
  Link,
  List,
  ListItem,
  ListItemAvatar,
  ListItemText,
  Avatar,
  Paper,
  Typography,
  Button,
  SxProps,
  useTheme,
  ListItemButton,
} from '@mui/material';
import {
  Download,
  MenuBook,
  VerifiedUser,
  PieChart,
  HowToVote,
} from '@mui/icons-material';

import SectionTitle from './SectionTitle';

const PublicDatabaseWidget = ({ sx }: { sx?: SxProps }) => {
  const apiUrl = process.env.REACT_APP_API_URL;

  const theme = useTheme();
  const { t } = useTranslation();

  return (
    <Paper sx={sx}>
      <Box
        p={2}
        color="#fff"
        bgcolor="#1282B2"
        sx={{ borderTopLeftRadius: 'inherit', borderTopRightRadius: 'inherit' }}
      >
        <Typography variant="h4">
          {t('researchSection.ourDataAreOpen')}
        </Typography>
      </Box>
      <Box p={2}>
        <Typography paragraph>
          <Trans i18nKey="researchSection.theTournesolPublicDatabaseIsPublished">
            The Tournesol public database is published under the terms of the
            Open Data Commons Attribution License
            <Link
              color={theme.palette.text.primary}
              href="https://opendatacommons.org/licenses/by/summary/"
            >
              (ODC-BY 1.0)
            </Link>
          </Trans>
        </Typography>
        <Box display="flex" justifyContent="center">
          <Button
            variant="contained"
            component={RouterLink}
            to={`${apiUrl}/exports/all/`}
            endIcon={<Download />}
          >
            {t('researchSection.download')}
          </Button>
        </Box>
      </Box>
    </Paper>
  );
};

const ScientificLiteratureWidget = () => {
  const { t } = useTranslation();

  const papers = [
    {
      name: 'Tournesol: A quest for a large, secure and trustworthy database of reliable human judgments',
      submitted: t('researchSection.may2021'),
      url: 'https://arxiv.org/abs/2107.07334',
      icon: MenuBook,
    },
    {
      name: 'Strategyproof Learning: Building Trustworthy User-Generated Datasets',
      submitted: t('researchSection.june2021'),
      url: 'https://arxiv.org/abs/2106.02398',
      icon: PieChart,
    },
    {
      name: 'Robust Sparse Voting',
      submitted: t('researchSection.february2022'),
      url: 'https://arxiv.org/abs/2202.08656',
      icon: HowToVote,
    },
    {
      name: 'Tournesol: Permissionless Collaborative Algorithmic Governance with Security Guarantees',
      submitted: t('researchSection.october2022'),
      url: 'https://arxiv.org/abs/2211.01179',
      icon: VerifiedUser,
    },
  ];

  return (
    <Paper>
      <Box
        p={2}
        color="#fff"
        bgcolor="#1282B2"
        sx={{ borderTopLeftRadius: 'inherit', borderTopRightRadius: 'inherit' }}
      >
        <Typography variant="h4">
          {t('researchSection.scientificLiterature')}
        </Typography>
      </Box>
      {/* Here px=1 is used instead of the regular p=2 as the list as already
          enough built-in padding */}
      <Box px={1}>
        <List>
          {papers.map((paper, idx) => (
            <React.Fragment key={paper.name.replace(' ', '_')}>
              <ListItem>
                <ListItemAvatar>
                  <Avatar>
                    <paper.icon />
                  </Avatar>
                </ListItemAvatar>
                <ListItemButton
                  href={paper.url}
                  target="_blank"
                  rel="noopener"
                  disableGutters
                >
                  <ListItemText
                    primary={paper.name}
                    secondary={paper.submitted}
                  />
                </ListItemButton>
              </ListItem>
              {idx !== papers.length - 1 && <Divider />}
            </React.Fragment>
          ))}
        </List>
      </Box>
    </Paper>
  );
};

const ResearchSection = () => {
  const { t } = useTranslation();

  return (
    <Box>
      <SectionTitle title={t('researchSection.research')} />
      <Box display="flex" justifyContent="center" mb={6}>
        <Box sx={{ width: { lg: '44%', xl: '44%' } }}>
          <Typography variant="h3" textAlign="center" letterSpacing="0.8px">
            {t('researchSection.weHopeToContribute')}
          </Typography>
        </Box>
      </Box>
      <Grid container spacing={4} justifyContent="center">
        {/* left section */}
        <Grid item lg={5} xl={5}>
          <Paper>
            <Box px={2} sx={{ '& img': { maxWidth: '100%' } }}>
              <img
                src="/images/criteria_pearson_correlation_matrix_2022_10_10.png"
                alt={t('researchSection.personCorrelationCoefficientMatrix')}
              />
            </Box>
          </Paper>
        </Grid>
        {/* right section */}
        <Grid item lg={4} xl={4}>
          <PublicDatabaseWidget sx={{ mb: 4 }} />
          <ScientificLiteratureWidget />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchSection;
