import React from 'react';
import { Trans } from 'react-i18next';

const ReliabilityDesc = () => (
  <Trans i18nKey="criteriaDescriptions.reliability">
    <em>
      Is the presented information trustworthy, robustly backed and properly
      nuanced?
    </em>
    <p>
      This criterion aims to measure the trustworthiness of the information
      presented in a content, but also the extent to which the information may
      be misleading. In particular, a factual content that cherry-picks data to
      present to corroborate a world view and lacks completeness should be
      considered partially misleading. Similarly, contents that lack epistemic
      prudence and suffer overconfidence may be considered less reliable than
      contents that adequately measure the extent of their ignorance.
    </p>
    <p>
      Contents that score high on &quot;reliable and not misleading&quot; should
      make nearly all viewers improve their global world view, despite
      viewers&apos; biases and motivated reasoning.
    </p>
    <h3>Reliability</h3>
    <p>
      The multiplicity and diversity of sources and evidence plays an important
      role in the reliability of a content. It should ideally be also backed by{' '}
      <a href="https://tournesol.app/entities/yt:DWzKI4WhSPQ">
        peer-reviewed scientific publications
      </a>
      . However, as explained in{' '}
      <a href="https://tournesol.app/entities/yt:42QuXLucH3Q">
        this video by Veritasium
      </a>
      , even published research usually has major shortcomings. More reliable
      information can be obtained by meta-analyses of multiple scientific
      publications, or by drawing on scientific consensus.
    </p>
    <p>
      Even then, even meta-analysis
      <a href="https://www.sciencemag.org/news/2018/09/meta-analyses-were-supposed-end-scientific-debates-often-they-only-cause-more">
        may not be conclusive
      </a>
      , especially when data are not compelling enough. A reliable analysis of
      the data should acknowledge uncertainty
      <sup>
        (
        <a href="https://www.tandfonline.com/doi/full/10.1080/00031305.2019.1583913">
          WassersteinSL-19
        </a>
        )
      </sup>{' '}
      by showing epistemic prudence, thereby combatting overconfidence. Ideally,
      the level of certainty should be well calibrated.
    </p>
    <h3>Misleading</h3>
    <p>
      Unfortunately, factual news can be deeply misleading. As an example, on
      October 21st, 2020, NBC News published a news entitled{' '}
      <a href="https://www.nbcnews.com/health/health-news/volunteer-astrazeneca-covid-19-vaccine-trial-dies-brazil-n1244166">
        &quot;Volunteer in AstraZeneca Covid-19 vaccine trial dies in
        Brazil&quot;
      </a>
      . However, subsequent news reported that the volunteer did not receive the
      vaccine, as he was in the control group. Weirdly, this was reported by
      Healthcare Finance in a news entitled{' '}
      <a href="https://www.healthcarefinancenews.com/news/28-year-old-volunteer-astrazeneca-covid-19-vaccine-trial-dies">
        &quot;28-year-old volunteer in AstraZeneca COVID-19 vaccine trial
        dies&quot;
      </a>
      . Only the subtitle clarifies the story, as it asserts &quot;The trial has
      not been paused as the volunteer did not receive the COVID-19 vaccine but
      was part of the control group.&quot;. Still, more generally, even a death
      of a single vaccinated individual should not radically affect our
      estimation of the dangerousness of the vaccine, as the cause of the death
      may be unrelated to the individual&apos;s vaccination. In fact, if tens of
      thousands of individuals get vaccinated, then a death of at least one
      individual should be expected in the months to come since; according at{' '}
      <a href="https://www.statista.com/statistics/241572/death-rate-by-age-and-sex-in-the-us/">
        Statista
      </a>
      , adults have a probability of dying within a year of at least 1 in 1,000.
    </p>
    <p>
      <a href="https://twitter.com/Chevre_Pensante/status/1352646815909351424">
        ChevrePensante-21<sup>FR</sup>
      </a>{' '}
      reports the way vaccine news have been reported in a disproportionally
      negative manner.
    </p>
    <p>
      More generally, to avoid being misleading, information should arguably
      present on scientific background knowledge, set information within
      context, analyze the best available statistical data, discuss conflicting
      interpretations and use careful wordings.
    </p>
  </Trans>
);

export default ReliabilityDesc;
