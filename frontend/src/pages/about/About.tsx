import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import { Grid, Typography, Box, Card, Link, Paper } from '@mui/material';

import { ContentHeader, ExternalLink, InternalLink } from 'src/components';
import {
  discordTournesolInviteUrl,
  githubTournesolUrl,
  linkedInTournesolUrl,
  whitePaperUrl,
} from 'src/utils/url';
import PublicDownloadSection from './PublicDownloadSection';

const useStyles = makeStyles(() => ({
  root: {
    width: '100%',
    padding: '32px 0px 32px 0px',
    justifyContent: 'center',
  },
  noMaxWidth: {
    maxWidth: '100%',
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

const CoreTeamCard = ({
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

const ContributorCard = ({
  name,
  image,
  description,
  website,
}: {
  name: string;
  image: string;
  description: string;
  website: string;
}) => {
  const classes = useStyles();

  return (
    <Link
      href={website}
      rel="noopener"
      underline="none"
      color="inherit"
      variant="inherit"
    >
      <Card className={classes.card}>
        <Grid container spacing={2}>
          <Grid item xs={4} container alignItems="center">
            <img
              src={image}
              width="100%"
              style={{
                aspectRatio: '1',
                objectFit: 'cover',
                borderRadius: '50%',
              }}
            />
          </Grid>
          <Grid item xs={8}>
            <Typography variant="h3">{name}</Typography>
            <Typography fontSize="90%">{description}</Typography>
          </Grid>
        </Grid>
      </Card>
    </Link>
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
        sx={{ bgcolor: 'background.emphatic', color: 'white' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h1">{t('about.whatIsTournesol')}</Typography>
            <Typography paragraph>
              <Trans t={t} i18nKey="about.introductionTournesol">
                Tournesol is an open source platform which aims to
                collaboratively identify top videos of public interest by
                eliciting contributors&apos; judgements on content quality. We
                hope to contribute to making today&apos;s and tomorrow&apos;s
                large-scale algorithms robustly beneficial for all of humanity.
                Find out more with our{' '}
                <ExternalLink href={whitePaperUrl} sx={{ color: 'white' }}>
                  white paper
                </ExternalLink>
                , our{' '}
                <ExternalLink href={githubTournesolUrl} sx={{ color: 'white' }}>
                  GitHub
                </ExternalLink>
                , our{' '}
                <ExternalLink
                  href={discordTournesolInviteUrl}
                  sx={{ color: 'white' }}
                >
                  Discord
                </ExternalLink>
                , or our{' '}
                <ExternalLink
                  href={linkedInTournesolUrl}
                  sx={{ color: 'white' }}
                >
                  LinkedIn page
                </ExternalLink>
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
        sx={{ bgcolor: 'background.emphatic', color: 'white' }}
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
                <InternalLink
                  to="/about/donate"
                  color="inherit"
                  underline="always"
                >
                  with a donation
                </InternalLink>
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
            <CoreTeamCard
              name="Lê Nguyên Hoang"
              image="/people/Le.jpeg"
              institution="Calicarpa"
              role={t('about.rolePresident')}
              title="Dr. in Mathematics"
              job="AI Researcher and Communicator"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Louis Faucon"
              image="/people/Louis.jpeg"
              institution="Oracle Labs"
              role={t('about.roleTreasurer')}
              title="Dr. in Computer Science"
              job="Machine Learning Engineer"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Aidan Jungo"
              image="/people/Aidan.jpg"
              institution="CFF"
              role={t('about.roleSecretary')}
              title="Master of Science"
              job="Project Manager"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Romain"
              image="/people/Tournecat.jpeg"
              institution=""
              role="Developer"
              title=""
              job="Senior Software Engineer"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Adrien Matissart"
              image="/people/Adrien.jpeg"
              institution="Akselos"
              title="Master of Science"
              role="Technical Lead"
              job="Senior Software Engineer"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Titouan Lustin"
              image="/people/Titouan.jpg"
              institution="UTC"
              title="Master of Science"
              role="Communication & Events"
              job="Engineer"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Victor Fersing"
              image="/people/Victor.jpg"
              institution="La Fabrique Sociale"
              title=""
              role="Communication & Events"
              job="Youtuber"
            />
          </Grid>

          <Grid item xs={12} sm={4} className={classes.container}>
            <CoreTeamCard
              name="Jean-Lou"
              image="/people/JeanLou.jpg"
              institution="AprèsLaBière"
              title=""
              role="Communication & Events"
              job="Journalist & Youtuber"
            />
          </Grid>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        // sx={{ bgcolor: 'background.menu' }}
      >
        <Grid item xs={12} className={classes.container}>
          <ContentBox>
            <Typography variant="h3">
              {t('about.significantContributors')}
            </Typography>
            <Typography paragraph>
              {t('about.weThankOurContributors')}
            </Typography>
          </ContentBox>
        </Grid>

        <Grid container item xs={12} md={9} className={classes.container}>
          <Grid item xs={12} sm={6} className={classes.container}>
            <ContributorCard
              name="Sergei"
              image="/people/Sergei.jpg"
              description={t('about.sergeiDescription')}
              website="https://linkedin.com/in/sergeivolodin"
            />
          </Grid>
          <Grid item xs={12} sm={6} className={classes.container}>
            <ContributorCard
              name="Michael Witrant"
              image="/people/sigmike.png"
              description={t('about.sigmikeDescription')}
              website="https://github.com/sigmike"
            />
          </Grid>
        </Grid>
      </Grid>

      <Grid
        container
        className={classes.root}
        sx={{ bgcolor: 'background.menu' }}
      >
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
                <ExternalLink
                  href={`${githubTournesolUrl}/graphs/contributors`}
                >
                  Github Contributors
                </ExternalLink>
              </Trans>
            </Typography>
          </ContentBox>
        </Grid>
      </Grid>

      <Grid container className={classes.root}>
        <Grid
          item
          xs={12}
          sm={12}
          md={10}
          lg={8}
          xl={8}
          className={classes.container}
        >
          <ContentBox className={classes.noMaxWidth}>
            <Paper
              sx={{ bgcolor: 'background.emphatic', color: 'white', p: 2 }}
              square
            >
              <PublicDownloadSection />
            </Paper>
          </ContentBox>
        </Grid>
      </Grid>
    </>
  );
};

export default AboutPage;
