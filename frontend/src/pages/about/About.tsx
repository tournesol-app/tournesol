import React from 'react';
import { useTranslation, Trans } from 'react-i18next';
import { Link as RouterLink } from 'react-router-dom';
import makeStyles from '@mui/styles/makeStyles';
import { Grid, Typography, Box, Card, Link } from '@mui/material';

import { ContentHeader } from 'src/components';
import {
  discordTournesolInviteUrl,
  getWikiBaseUrl,
  githubTournesolUrl,
  utipTournesolUrl,
  whitePaperUrl,
} from 'src/utils/url';
import PublicDownloadSection from './PublicDownloadSection';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    padding: '32px 0px 32px 0px',
    justifyContent: 'center',
  },
  container: {
    display: 'flex',
    justifyContent: 'center',
    padding: 8,
  },
  card: {
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: 4,
    padding: 8,
    width: '100%',
    background: '#FFFFFF',
  },
  important: {
    fontWeight: 'bold',
  },
}));

const PeopleCard = ({
  name,
  image,
  institution,
  role,
  title,
  job,
}: {
  name: string;
  image: string;
  institution: string;
  role: string;
  title: string;
  job: string;
}) => {
  const classes = useStyles();

  return (
    <Card className={classes.card} sx={{ maxWidth: 320 }}>
      <img
        src={image}
        width="100%"
        style={{ aspectRatio: '1', objectFit: 'cover', borderRadius: '50%' }}
      />
      <Typography variant="h3">{name}</Typography>
      <Typography>{role}</Typography>
      <Typography>{title}</Typography>
      <Typography>{job}</Typography>
      <Typography>{institution}</Typography>
    </Card>
  );
};

const ContentBox = ({
  children,
  className,
}: {
  children?: React.ReactNode;
  className?: string;
}) => {
  return (
    <Box
      className={className}
      display="flex"
      flexDirection="column"
      maxWidth="640px"
      alignItems="flex-start"
    >
      {children}
    </Box>
  );
};

const AboutPage = () => {
  const { t } = useTranslation();
  const classes = useStyles();

  return (
    <>
      <ContentHeader title={t('menu.about')} />
      <Grid
        container
        className={classes.root}
        sx={{ background: '#1282B2', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">{t('about.whatIsTournesol')}</Typography>
            <Typography paragraph>
              <Trans t={t} i18nKey="about.introductionTournesol">
                Tournesol is an open source platform which aims to
                collaboratively identify top videos of public utility by
                eliciting contributors&apos; judgements on content quality. We
                hope to contribute to making today&apos;s and tomorrow&apos;s
                large-scale algorithms robustly beneficial for all of humanity.
                Find out more with our{' '}
                <a
                  href={whitePaperUrl}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: 'white' }}
                >
                  white paper
                </a>
                , our{' '}
                <a
                  href={getWikiBaseUrl()}
                  target="_blank"
                  rel="noreferrer"
                  style={{ color: 'white' }}
                >
                  wiki
                </a>
                , our{' '}
                <a
                  href={githubTournesolUrl}
                  target="_blank"
                  style={{ color: 'white' }}
                  rel="noreferrer"
                >
                  GitHub
                </a>
                , our{' '}
                <a
                  href={discordTournesolInviteUrl}
                  target="_blank"
                  style={{ color: 'white' }}
                  rel="noreferrer"
                >
                  Discord
                </a>
                , or our{' '}
                <a
                  href="https://www.linkedin.com/company/tournesol-app/"
                  target="_blank"
                  style={{ color: 'white' }}
                  rel="noreferrer"
                >
                  LinkedIn page
                </a>
                .
              </Trans>
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid container className={classes.root}>
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h4">{t('about.tournesolVision')}</Typography>
            <ul>
              <li>
                <Typography paragraph className={classes.important}>
                  {t('about.tournesolVisionRaisingAwareness')}
                </Typography>
              </li>
              <li>
                <Typography paragraph className={classes.important}>
                  {t('about.tournesolVisionCollaborativePlatform')}
                </Typography>
              </li>
              <li>
                <Typography paragraph className={classes.important}>
                  {t('about.tournesolVisionResearchOnEthicsOfAlgorithms')}
                </Typography>
              </li>
            </ul>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        sx={{ background: '#1282B2', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">
              {t('about.whoBuildsTournesol')}
            </Typography>
            <Typography paragraph>
              {t('about.tournesolTransparency')}
            </Typography>
            <Typography paragraph>
              <Trans t={t} i18nKey="about.considerHelpingWithDonation">
                If you can, please consider helping us{' '}
                <Link component={RouterLink} to="/about/donate" color="inherit">
                  with a donation
                </Link>
                .
              </Trans>
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        sx={{ bgcolor: 'background.menu' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <img height="64px" src="/logos/Tournesol_Logo.png" />
            <Typography variant="h4">
              {t('about.tournesolAssociation')}
            </Typography>
            <Typography paragraph>
              {t('about.tournesolAssociationDetail')}
            </Typography>
          </ContentBox>
        </Grid>

        <Grid container item xs={12} md={9} className={classes.container}>
          <Grid item xs={12} sm={4} className={classes.container}>
            <PeopleCard
              name="Lê Nguyên Hoang"
              image="/people/Le.jpeg"
              institution=""
              role={t('about.rolePresident')}
              title="Dr. in Mathematics"
              job="AI Researcher and Communicator"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <PeopleCard
              name="Louis Faucon"
              image="/people/Louis.jpeg"
              institution="Oracle Labs"
              role={t('about.roleTreasurer')}
              title="Dr. in Computer Science"
              job="Software engineer"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <PeopleCard
              name="Aidan Jungo"
              image="/people/Aidan.jpg"
              institution="CFS Engineering SA"
              role={t('about.roleSecretary')}
              title="Master of Science"
              job="Research Scientist"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <PeopleCard
              name="Romain"
              image="/people/Tournecat.jpeg"
              institution=""
              role="Association employee"
              title="Cat lover"
              job="Senior Software Engineer"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <PeopleCard
              name="Adrien Matissart"
              image="/people/Adrien.jpeg"
              institution="Association Tournesol"
              title=""
              role=""
              job="Senior Software Engineer"
            />
          </Grid>
        </Grid>
      </Grid>

      <Grid container className={classes.root}>
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">
              {t('about.weThankOurPartners')}
            </Typography>
          </ContentBox>
        </Grid>

        <Grid item xs={12} className={classes.container}>
          <ContentBox className={classes.card}>
            <img height="84px" src="/logos/EPFL_Logo.png" />
            <Typography variant="h4">
              {t('about.partnershipWithEpfl')}
            </Typography>
            <Typography paragraph>
              {t('about.partenershipWithEpflDetail')}
            </Typography>
          </ContentBox>
        </Grid>

        <Grid item xs={12} md={4} className={classes.container}>
          <Link
            href="https://www.polyconseil.fr/"
            rel="noopener"
            target="_blank"
            underline="none"
            color="inherit"
            variant="inherit"
          >
            <ContentBox className={classes.card}>
              <img
                height="64px"
                src="/logos/Polyconseil_Logo.png"
                style={{ maxWidth: '100%' }}
              />
              <Typography variant="h4">
                {t('about.partnershipWithPolyconseil')}
              </Typography>
              <Typography paragraph>
                {t('about.partnershipWithPolyconseilDetail')}
              </Typography>
            </ContentBox>
          </Link>
        </Grid>

        <Grid item xs={12} md={4} className={classes.container}>
          <Link
            href="https://kleis.ch/"
            rel="noopener"
            target="_blank"
            underline="none"
            color="inherit"
            variant="inherit"
          >
            <ContentBox className={classes.card}>
              <img height="64px" src="/logos/Kleis_Logo.svg" />
              <Typography variant="h4">
                {t('about.partnershipWithKleis')}
              </Typography>
              <Typography paragraph>
                {t('about.partnershipWithKleisDetail')}
              </Typography>
            </ContentBox>
          </Link>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        sx={{ bgcolor: 'background.menu' }}
      >
        <Grid item xs={12} md={6} className={classes.container}>
          <ContentBox>
            <img height="64px" src="/logos/Foss_Logo.png" />
            <Typography variant="h4">
              {t('about.openSourceContributions')}
            </Typography>
            <Typography paragraph>
              <Trans t={t} i18nKey="about.openSourceContributors">
                As Tournesol is an open source project, we have been lucky to
                benefit from contributions by multiple volunteers. Find our
                wonderful contributors on{' '}
                <a
                  href={`${utipTournesolUrl}/graphs/contributors`}
                  target="_blank"
                  rel="noreferrer"
                >
                  Github Contributors
                </a>
              </Trans>
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        sx={{ background: '#1282B2', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <PublicDownloadSection />
          </ContentBox>
        </Grid>
      </Grid>
    </>
  );
};

export default AboutPage;
