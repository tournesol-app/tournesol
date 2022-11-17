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
  ListItemButton,
} from '@mui/material';
import {
  Campaign,
  Download,
  GitHub,
  MedicalInformation,
  MenuBook,
  VerifiedUser,
  HowToVote,
} from '@mui/icons-material';

import SectionTitle from './SectionTitle';

const PublicDatabaseWidget = ({ sx }: { sx?: SxProps }) => {
  const apiUrl = process.env.REACT_APP_API_URL;
  const { t } = useTranslation();

  return (
    <Box sx={sx}>
      <Paper sx={{ mb: 2 }}>
        <Box
          p={2}
          color="#fff"
          bgcolor="#1282B2"
          sx={{
            borderTopLeftRadius: 'inherit',
            borderTopRightRadius: 'inherit',
          }}
        >
          <Typography variant="h4">
            {t('researchSection.ourDataAreOpen')}
          </Typography>
        </Box>
        <Box p={2}>
          <Typography paragraph>
            {t('researchSection.tournesolIsAnOpenlyAltruisticProject')}
          </Typography>
          <Typography paragraph>
            {t('researchSection.weHopeThatOtherProjectsCanBenefitEtc')}
          </Typography>
          <Typography paragraph>
            <Trans i18nKey="researchSection.theseDataArePublishedUnderODCBY">
              These data are published under the terms of the Open Data Commons
              Attribution License
              <Link
                color="text.primary"
                href="https://opendatacommons.org/licenses/by/summary/"
              >
                (ODC-BY 1.0).
              </Link>
            </Trans>
          </Typography>
        </Box>
      </Paper>
      <Paper sx={{ p: 2, mb: 2 }}>
        <Box display="flex" justifyContent="center">
          <Button
            variant="contained"
            component={RouterLink}
            to={`${apiUrl}/exports/all/`}
            endIcon={<Download />}
          >
            {t('researchSection.downloadTheDatabase')}
          </Button>
        </Box>
      </Paper>
      <Paper sx={{ p: 2 }}>
        <Box display="flex" justifyContent="center">
          <Button
            variant="contained"
            component={Link}
            target="_blank"
            rel="noopener"
            href="https://github.com/tournesol-app/tournesol"
            endIcon={<GitHub />}
          >
            {t('researchSection.accessTheCodeOnGitHub')}
          </Button>
        </Box>
      </Paper>
    </Box>
  );
};

const ScientificLiteratureWidget = () => {
  const { t } = useTranslation();

  const papers = [
    {
      name: 'Tournesol: Permissionless Collaborative Algorithmic Governance with Security Guarantees.',
      submitted:
        'Romain Beylerian, Bérangère Colbois, Louis Faucon, Lê Nguyên Hoang, Aidan Jungo, ' +
        "Alain Le Noac'h, Adrien Matissart (2022). ArXiV.",
      url: 'https://arxiv.org/abs/2211.01179',
      icon: VerifiedUser,
    },
    {
      name: 'Tournesol: A quest for a large, secure and trustworthy database of reliable human judgments.',
      submitted:
        'Lê-Nguyên Hoang, Louis Faucon, Aidan Jungo, Sergei Volodin, Dalia Papuc, Orfeas Liossatos, ' +
        'Ben Crulis, Mariame Tighanimine, Isabela Constantin, Anastasiia Kucherenko, Alexandre Maurer, ' +
        'Felix Grimberg, Vlad Nitu, Chris Vossen, Sébastien Rouault, El-Mahdi El-Mhamdi (2021). ArXiV.',
      url: 'https://arxiv.org/abs/2107.07334',
      icon: MenuBook,
    },
    {
      name: 'Robust Sparse Voting',
      submitted:
        'Youssef Allouah, Rachid Guerraoui, Lê-Nguyên Hoang, Oscar Villemaud (2022). ArXiV.',
      url: 'https://arxiv.org/abs/2202.08656',
      icon: HowToVote,
    },
    {
      name: 'Recommendation Algorithms, a Neglected Opportunity for Public Health.',
      submitted:
        'Lê Nguyên Hoang, Louis Faucon & El-Mahdi El-Mhamdi (2021). Revue Médecine et Philosophie.',
      url: 'https://philpapers.org/rec/HOARAA',
      icon: MedicalInformation,
    },
    {
      name: 'Science Communication Desperately Needs More Aligned Recommendation Algorithms.',
      submitted: 'Lê Nguyên Hoang (2020). Frontiers Communications.',
      url: 'https://www.frontiersin.org/articles/10.3389/fcomm.2020.598454/full',
      icon: Campaign,
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
        <Grid item lg={4} xl={4}>
          <PublicDatabaseWidget />
        </Grid>
        <Grid item lg={8} xl={5}>
          <Paper>
            <Box
              p={2}
              color="#fff"
              bgcolor="#1282B2"
              sx={{
                borderTopLeftRadius: 'inherit',
                borderTopRightRadius: 'inherit',
              }}
            >
              <Typography variant="h4">
                {t('researchSection.visualizeTheData')}
              </Typography>
            </Box>
            <Box px={2} sx={{ '& img': { maxWidth: '100%' } }}>
              <Box p={2}>
                <Typography paragraph mb={0}>
                  <Trans i18nKey="researchSection.youCanQuicklyExploreEtc">
                    You can quickly explore our public database with our
                    appplication
                    <Link
                      color="text.primary"
                      href="https://github.com/tournesol-app/tournesol/tree/main/analytics"
                    >
                      Tournesol Data Visualization
                    </Link>
                    made with Streamlit.
                  </Trans>
                </Typography>
              </Box>
              <img
                src="/images/criteria_pearson_correlation_matrix_2022_10_10.png"
                alt={t('researchSection.personCorrelationCoefficientMatrix')}
              />
            </Box>
          </Paper>
        </Grid>
        <Grid item xl={9}>
          <ScientificLiteratureWidget />
        </Grid>
      </Grid>
    </Box>
  );
};

export default ResearchSection;
