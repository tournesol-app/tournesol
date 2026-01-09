import React from 'react';
import { useTranslation, Trans } from 'react-i18next';

import makeStyles from '@mui/styles/makeStyles';
import {
  Grid2,
  Typography,
  Box,
  Card,
  Link,
  Paper,
  SxProps,
} from '@mui/material';

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
    padding: '16px 0',
    margin: '16px 0',
    justifyContent: 'center',
    flexDirection: 'column',
  },
  container: {
    maxWidth: '900px',
    margin: '0 auto',
    display: 'flex',
    justifyContent: 'left',
    padding: 8,
  },
  card: {
    border: '1px solid #DCD8CB',
    boxShadow:
      '0px 0px 8px rgba(0, 0, 0, 0.02), 0px 2px 4px rgba(0, 0, 0, 0.05)',
    borderRadius: 4,
    padding: '16px',
    width: '100%',
    background: '#FFFFFF',
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
      sx={{
        display: 'flex',
      }}
    >
      <Card className={classes.card}>
        <Grid2 container spacing={2}>
          <Grid2
            container
            sx={{
              alignItems: 'center',
            }}
            size={4}
          >
            <img
              src={image}
              width="100%"
              style={{
                aspectRatio: '1',
                objectFit: 'cover',
                borderRadius: '50%',
              }}
            />
          </Grid2>
          <Grid2 size={8}>
            <Typography variant="h3">{name}</Typography>
            <Typography
              sx={{
                fontSize: '90%',
              }}
            >
              {description}
            </Typography>
          </Grid2>
        </Grid2>
      </Card>
    </Link>
  );
};

const ContentBox = ({
  children,
  className,
  maxWidth = '900px',
  sx,
}: {
  children?: React.ReactNode;
  className?: string;
  maxWidth?: string;
  sx?: SxProps;
}) => {
  return (
    <Box
      className={className}
      sx={[
        {
          display: 'flex',
          flexDirection: 'column',
          maxWidth: maxWidth,
          alignItems: 'flex-start',
        },
        ...(Array.isArray(sx) ? sx : [sx]),
      ]}
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
      <Grid2
        container
        className={classes.root}
        sx={{ bgcolor: 'background.emphatic', color: 'white' }}
      >
        <Grid2 className={classes.container} size={12}>
          <ContentBox>
            <Typography
              variant="h1"
              sx={{
                mb: 1,
              }}
            >
              {t('about.whatIsTournesol')}
            </Typography>
            <Typography
              sx={{
                marginBottom: 2,
              }}
            >
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
        </Grid2>
      </Grid2>
      <Grid2 container className={classes.root}>
        <Grid2 className={classes.container} size={12}>
          <ContentBox sx={{ '& li': { fontWeight: 'bold', marginBottom: 2 } }}>
            <Typography variant="h4">{t('about.tournesolVision')}</Typography>
            <ul>
              <li>{t('about.tournesolVisionRaisingAwareness')}</li>
              <li>{t('about.tournesolVisionCollaborativePlatform')}</li>
              <li>{t('about.tournesolVisionResearchOnEthicsOfAlgorithms')}</li>
            </ul>
          </ContentBox>
        </Grid2>
      </Grid2>
      <Grid2
        container
        className={classes.root}
        sx={{ bgcolor: 'background.emphatic', color: 'white' }}
      >
        <Grid2 className={classes.container} size={12}>
          <ContentBox>
            <Typography
              variant="h1"
              sx={{
                mb: 1,
              }}
            >
              {t('about.whoBuildsTournesol')}
            </Typography>
            <Typography
              sx={{
                marginBottom: 2,
              }}
            >
              {t('about.tournesolTransparency')}
            </Typography>
            <Typography
              sx={{
                marginBottom: 2,
              }}
            >
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
        </Grid2>
      </Grid2>
      <Grid2
        container
        className={classes.root}
        sx={{ bgcolor: 'background.menu' }}
      >
        <Grid2 className={classes.container} size={12}>
          <ContentBox>
            <img height="64px" src="/logos/Tournesol_Logo.png" />
            <Typography variant="h4">
              {t('about.tournesolAssociation')}
            </Typography>
            <Typography
              sx={{
                marginBottom: 2,
              }}
            >
              {t('about.tournesolAssociationDetail')}
            </Typography>
          </ContentBox>
        </Grid2>

        <Grid2
          container
          className={classes.container}
          size={{
            xs: 12,
            lg: 8,
          }}
        >
          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Lê Nguyên Hoang"
              image="/people/Le.jpeg"
              institution="Calicarpa"
              role={t('about.rolePresident')}
              title="Dr. in Mathematics"
              job="AI Researcher and Communicator"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Louis Faucon"
              image="/people/Louis.jpeg"
              institution="Oracle Labs"
              role={t('about.roleTreasurer')}
              title="Dr. in Computer Science"
              job="Machine Learning Engineer"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Aidan Jungo"
              image="/people/Aidan.jpg"
              institution="CFF"
              role={t('about.roleSecretary')}
              title="Master of Science"
              job="Project Manager"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Romain"
              image="/people/Tournecat.jpeg"
              institution=""
              role="Developer"
              title=""
              job="Senior Software Engineer"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Adrien Matissart"
              image="/people/Adrien.jpeg"
              institution="Akselos"
              title="Master of Science"
              role="Technical Lead"
              job="Senior Software Engineer"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Titouan Lustin"
              image="/people/Titouan.jpg"
              institution="UTC"
              title="Master of Science"
              role="Communication & Events"
              job="Engineer"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Victor Fersing"
              image="/people/Victor.jpg"
              institution="La Fabrique Sociale"
              title=""
              role="Communication & Events"
              job="Youtuber"
            />
          </Grid2>

          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 4,
            }}
          >
            <CoreTeamCard
              name="Jean-Lou"
              image="/people/JeanLou.jpg"
              institution="AprèsLaBière"
              title=""
              role="Communication & Events"
              job="Journalist & Youtuber"
            />
          </Grid2>
        </Grid2>
      </Grid2>
      <Grid2 container className={classes.root}>
        <Grid2 className={classes.container} size={12}>
          <ContentBox>
            <Typography variant="h3">
              {t('about.significantContributors')}
            </Typography>
            <Typography
              sx={{
                marginBottom: 2,
              }}
            >
              {t('about.weThankOurContributors')}
            </Typography>
          </ContentBox>
        </Grid2>

        <Grid2
          container
          className={classes.container}
          size={{
            xs: 12,
            md: 9,
          }}
        >
          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 6,
            }}
          >
            <ContributorCard
              name="Sergei"
              image="/people/Sergei.jpg"
              description={t('about.sergeiDescription')}
              website="https://linkedin.com/in/sergeivolodin"
            />
          </Grid2>
          <Grid2
            className={classes.container}
            size={{
              xs: 12,
              sm: 6,
            }}
          >
            <ContributorCard
              name="Michael Witrant"
              image="/people/sigmike.png"
              description={t('about.sigmikeDescription')}
              website="https://github.com/sigmike"
            />
          </Grid2>
        </Grid2>
      </Grid2>
      <Grid2
        container
        className={classes.container}
        sx={{
          maxWidth: { md: '75%' },
          margin: 'auto',
        }}
      >
        <Grid2 className={classes.container}>
          <ContentBox>
            <Typography variant="h1">
              {t('about.weThankOurPartners')}
            </Typography>
          </ContentBox>
        </Grid2>

        <Grid2 className={classes.container} size={12}>
          <Link
            href="https://www.calicarpa.com/"
            rel="noopener"
            underline="none"
            color="inherit"
            variant="inherit"
            sx={{
              display: 'flex',
            }}
          >
            <ContentBox className={classes.card} maxWidth="100%">
              <img height="84px" src="/logos/Calicarpa_Logo.svg" />
              <Typography variant="h4">
                {t('about.partnershipWithCalicarpa')}
              </Typography>
              <Typography paragraph>
                {t('about.partnershipWithCalicarpaDetail')}
              </Typography>
            </ContentBox>
          </Link>
        </Grid2>

        <Grid2 size={12} className={classes.container}>
          <ContentBox className={classes.card} maxWidth="100%">
            <img height="84px" src="/logos/EPFL_Logo.png" />
            <Typography variant="h4">
              {t('about.partnershipWithEpfl')}
            </Typography>
            <Typography
              sx={{
                marginBottom: 2,
              }}
            >
              {t('about.partenershipWithEpflDetail')}
            </Typography>
          </ContentBox>
        </Grid2>

        <Grid2
          className={classes.container}
          size={{
            xs: 12,
            md: 6,
          }}
        >
          <Link
            href="https://www.polyconseil.fr/"
            rel="noopener"
            underline="none"
            color="inherit"
            variant="inherit"
            sx={{
              display: 'flex',
            }}
          >
            <ContentBox className={classes.card} maxWidth="100%">
              <img
                height="64px"
                src="/logos/Polyconseil_Logo.png"
                style={{ maxWidth: '100%' }}
              />
              <Typography variant="h4">
                {t('about.partnershipWithPolyconseil')}
              </Typography>
              <Typography
                sx={{
                  marginBottom: 2,
                }}
              >
                {t('about.partnershipWithPolyconseilDetail')}
              </Typography>
            </ContentBox>
          </Link>
        </Grid2>

        <Grid2
          className={classes.container}
          size={{
            xs: 12,
            md: 6,
          }}
        >
          <Link
            href="https://kleis.ch/"
            rel="noopener"
            underline="none"
            color="inherit"
            variant="inherit"
            sx={{
              display: 'flex',
            }}
          >
            <ContentBox className={classes.card} maxWidth="100%">
              <img height="64px" src="/logos/Kleis_Logo.svg" />
              <Typography variant="h4">
                {t('about.partnershipWithKleis')}
              </Typography>
              <Typography
                sx={{
                  marginBottom: 2,
                }}
              >
                {t('about.partnershipWithKleisDetail')}
              </Typography>
            </ContentBox>
          </Link>
        </Grid2>

        <Grid2 className={classes.container} size={12}>
          <Link
            href="https://www.devoxx.fr/"
            rel="noopener"
            underline="none"
            color="inherit"
            variant="inherit"
          >
            <ContentBox className={classes.card} maxWidth="100%">
              <img height="64px" src="/logos/devoxx_france_logo.png" />
              <Typography
                sx={{
                  marginBottom: 2,
                }}
              >
                {t('about.collaborationWithDevoxx')}
              </Typography>
            </ContentBox>
          </Link>
        </Grid2>
      </Grid2>
      <Grid2 container className={classes.root}>
        <Grid2 className={classes.container}>
          <ContentBox maxWidth="100%" sx={{ p: 2 }}>
            <img height="64px" src="/logos/Foss_Logo.png" />
            <Typography variant="h4">
              {t('about.openSourceContributions')}
            </Typography>
            <Typography>
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
        </Grid2>
      </Grid2>
      <Grid2 container className={classes.root}>
        <Grid2 className={classes.container}>
          <Paper
            sx={{ bgcolor: 'background.emphatic', color: 'white', p: 2, m: 1 }}
          >
            <PublicDownloadSection />
          </Paper>
        </Grid2>
      </Grid2>
    </>
  );
};

export default AboutPage;
