// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

// TODO: these values are placeholder values that should be updated.
const TS_BANNER_DATE_START = new Date('2020-01-01T00:00:00Z');
const TS_BANNER_DATE_END = new Date('2022-01-01T00:00:00Z');
const TS_BANNER_ACTION_FR_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLScQzlEKBSA3MqxI0kaPazbyIUnZ4PjFcrR8EFiikG1quyAoiw/viewform?usp=pp_url&entry.939413650=';
const TS_BANNER_ACTION_EN_URL =
  'https://docs.google.com/forms/d/e/1FAIpQLSf9PXr-f8o9QqDR-Pi63xRZx4y4nOumNDdwi_jvUWc6LxZRAw/viewform?usp=pp_url&entry.1924714025=';
const TS_BANNER_PROOF_KW = 'browser_extension_study_2023';

const videosPerRow = 4;
const rowsWhenExpanded = 3;

let isExpanded = false;

const searchRecommandationNumber = 3;

let videos = [];
let additionalVideos = [];
let isPageLoaded = false;
let areRecommandationsLoading = false;
let areRecommendationsLoaded = false;
let path = location.pathname;
let search = '';
const i18n = chrome.i18n;
let recommandationsLanguages = 'en';

document.addEventListener('yt-navigate-finish', process);
if (document.body) process();
else document.addEventListener('DOMContentLoaded', process);

setInterval(() => {
  if (location.pathname != path || location.search != search) {
    path = location.pathname;
    search = location.search;
    loadRecommandations();
  }
}, 1000);

const convertDurationToClockDuration = (duration) => {
  const roundToTwoDigits = (number) => {
    return number < 10 ? `0${number}` : `${number}`;
  };
  const hours = Math.floor(duration / 3600);
  const minutes = roundToTwoDigits(Math.floor((duration % 3600) / 60));
  const seconds = roundToTwoDigits(duration % 60);
  return hours > 0 ? `${hours}:${minutes}:${seconds}` : `${minutes}:${seconds}`;
};

const getParentComponent = () => {
  try {
    // Get parent element for the boxes in youtube page
    let contents;
    if (path != '/results') {
      contents = document.querySelector('#primary > ytd-rich-grid-renderer');
    } else {
      contents = document.querySelector('#header-container');
    }
    if (!contents || !contents.children[1]) return;
    return contents;
  } catch (error) {
    return;
  }
};

/**
 * The browser API is expected to return the language indentifier following
 * the RFC 5646.
 *
 * See: https://datatracker.ietf.org/doc/html/rfc5646#section-2.1
 */
const isNavigatorLang = (lang) => {
  let expected = lang.toLowerCase();
  let found = window.navigator.language.toLocaleLowerCase();

  // `expected` can be the shortest ISO 639 code of a language.
  //  Example: 'fr'.
  if (found === expected) {
    return true;
  }

  // The shortest ISO 639 code can be followed by other "subtags" like the
  // region, or the variant. Example: 'fr-CA'.
  if (found.startsWith(expected + '-')) {
    return true;
  }

  return false;
};

const getLocalizedActionButtonText = () => {
  if (isNavigatorLang('fr')) {
    return 'Participer';
  }

  return 'Join';
};

const getLocalizedActionError = () => {
  if (isNavigatorLang('fr')) {
    return (
      'Désolé, une erreur est survenue.\n' +
      "S'il vous plaît, reportez l'erreur dans notre espace GitHub " +
      'ou sur notre serveur Discord.\n\n' +
      'GitHub: https://github.com/tournesol-app/tournesol/issues/new\n\n' +
      'Discord: https://discord.com/invite/TvsFB8RNBV'
    );
  }

  return (
    'Sorry, an error occured.\n' +
    'Please, report the issue on our GitHub space ' +
    'or on our Discord server.\n\n' +
    'GitHub: https://github.com/tournesol-app/tournesol/issues/new\n\n' +
    'Discord: https://discord.com/invite/TvsFB8RNBV'
  );
};

const displayElement = (element) => {
  element.classList.add('displayed');
};

const hideElement = (element) => {
  element.classList.remove('displayed');
};

/**
 * Create and return a banner.
 *
 * The banner invites the users to join our study about the impact of the
 * browser extension has on their YouTube usage.
 *
 * @returns HTMLDivElement
 */
const createBanner = () => {
  const banner = document.createElement('div');
  banner.id = 'tournesol_banner';
  banner.className = 'tournesol_banner';

  // Only display the banner if the user didn't explicitly close it.
  chrome.storage.local.get(
    'displayBannerStudy2023',
    ({ displayBannerStudy2023 }) => {
      if ([true, null, undefined].includes(displayBannerStudy2023)) {
        displayElement(banner);
      }
    }
  );

  // The first flex item is the campaign icon.
  const bannerIconContainer = document.createElement('div');
  const icon = document.createElement('img');
  icon.id = 'tournesol_banner_icon';
  icon.setAttribute('src', chrome.extension.getURL('images/campaign.svg'));
  icon.setAttribute('alt', 'Megaphone icon');
  bannerIconContainer.append(icon);

  // The second flex item is the text.
  const bannerTextContainer = document.createElement('div');
  const bannerText = document.createElement('p');
  bannerText.textContent = i18n.getMessage('study2023BannerText');
  bannerTextContainer.append(bannerText);

  // The third flex item is the action button.
  const actionButtonContainer = document.createElement('div');
  const actionButton = document.createElement('a');
  actionButton.textContent = getLocalizedActionButtonText();
  actionButton.className = 'tournesol_mui_like_button';
  actionButton.setAttribute(
    'href',
    isNavigatorLang('fr') ? TS_BANNER_ACTION_FR_URL : TS_BANNER_ACTION_EN_URL
  );
  actionButton.setAttribute('target', '_blank');
  actionButton.setAttribute('rel', 'noopener');

  // The last flex item is the close button.
  const closeButtonContainer = document.createElement('div');
  const closeButton = document.createElement('button');
  closeButton.className = 'tournesol_simple_button';
  const closeButtonImg = document.createElement('img');
  closeButtonImg.id = 'tournesol_banner_close_icon';
  closeButtonImg.setAttribute(
    'src',
    chrome.extension.getURL('images/close.svg')
  );
  closeButtonImg.setAttribute('alt', 'Close icon');
  closeButton.append(closeButtonImg);
  closeButtonContainer.append(closeButton);

  closeButton.onclick = () => {
    chrome.storage.local.set({ displayBannerStudy2023: false }, () => {
      hideElement(banner);
    });
  };

  // Dynamically get the user proof before opening the URL.
  actionButton.onclick = (event) => {
    event.preventDefault();
    event.stopPropagation();

    new Promise((resolve, reject) => {
      chrome.runtime.sendMessage(
        {
          message: `getProof:${TS_BANNER_PROOF_KW}`,
        },
        (response) => {
          if (response.success) {
            resolve(
              isNavigatorLang('fr')
                ? `${TS_BANNER_ACTION_FR_URL}${response.body.signature}`
                : `${TS_BANNER_ACTION_EN_URL}${response.body.signature}`
            );
          } else {
            reject(response);
          }
        }
      );
    })
      .then((url) => {
        actionButton.setAttribute('href', url);
        window.open(url, '_blank', 'noopener');
      })
      .catch((response) => {
        // Anonymous users should be redirected to the form without
        // participation proof. Other errors are logged.
        if (response.status === 401) {
          window.open(
            isNavigatorLang('fr')
              ? TS_BANNER_ACTION_FR_URL
              : TS_BANNER_ACTION_EN_URL,
            '_blank',
            'noopener'
          );
        } else {
          console.error(
            `Failed to retrieve user proof with keyword: ${TS_BANNER_PROOF_KW}`
          );
          console.error(response.body);
          alert(getLocalizedActionError());
        }
      });

    return false;
  };

  actionButtonContainer.append(actionButton);

  banner.appendChild(bannerIconContainer);
  banner.appendChild(bannerTextContainer);
  banner.appendChild(actionButtonContainer);
  banner.appendChild(closeButtonContainer);
  return banner;
};

const bannerShouldBeDisplayed = () => {
  const now = new Date();

  if (TS_BANNER_DATE_START <= now && now <= TS_BANNER_DATE_END) {
    return true;
  }

  return false;
};

const createVideosFlexContainer = () => {
  const container = document.createElement('div');
  container.id = 'tournesol_videos_flexcontainer';
  return container;
};

const getTournesolComponent = () => {
  // Create new container
  const tournesol_container = document.createElement('div');
  tournesol_container.id = 'tournesol_container';

  // Add inline-block div
  const inline_div = document.createElement('div');
  inline_div.setAttribute('class', 'inline_div');

  // Add tournesol icon
  const tournesol_icon = document.createElement('img');
  tournesol_icon.setAttribute('id', 'tournesol_icon');
  tournesol_icon.setAttribute(
    'src',
    //chrome.extension.getURL('rate_now_icon.png'),
    'https://tournesol.app/svg/tournesol.svg'
  );
  tournesol_icon.setAttribute('width', '24');
  inline_div.append(tournesol_icon);

  // Add title
  const tournesol_title = document.createElement('h1');
  tournesol_title.id = 'tournesol_title';
  tournesol_title.append(i18n.getMessage('recommendedByTournesol'));
  inline_div.append(tournesol_title);

  // Refresh button
  const refresh_button = document.createElement('button');
  refresh_button.setAttribute('id', 'tournesol_refresh_button');
  fetch(chrome.runtime.getURL('images/sync-alt.svg'))
    .then((r) => r.text())
    .then((svg) => (refresh_button.innerHTML = svg));

  refresh_button.className = 'tournesol_simple_button';
  refresh_button.onclick = () => {
    refresh_button.disabled = true;
    loadRecommandations();
  };
  inline_div.append(refresh_button);

  // Add title
  const tournesol_link = document.createElement('a');
  tournesol_link.id = 'tournesol_link';
  tournesol_link.href = 'https://tournesol.app?utm_source=extension';
  tournesol_link.target = '_blank';
  tournesol_link.rel = 'noopener';
  tournesol_link.append(i18n.getMessage('learnMore'));
  inline_div.append(tournesol_link);

  // Expand button
  const expand_button_container = document.createElement('div');
  expand_button_container.classList = 'expand_button_container';
  const expand_button = document.createElement('button');
  expand_button.setAttribute('id', 'tournesol_expand_button');
  // A new button is created on each video loading, the image must be loaded accordingly
  fetch(
    chrome.runtime.getURL(
      isExpanded ? 'images/chevron-up.svg' : 'images/chevron-down.svg'
    )
  )
    .then((r) => r.text())
    .then((svg) => (expand_button.innerHTML = svg));
  expand_button.className = 'tournesol_simple_button';
  expand_button.onclick = () => {
    expand_button.disabled = true;
    if (!areRecommandationsLoading && !isExpanded) {
      isExpanded = true;
      displayRecommendations();
    } else if (isExpanded) {
      isExpanded = false;
      displayRecommendations();
    }
  };
  expand_button_container.append(expand_button);

  // Display the campaign button only if there is a banner.
  if (bannerShouldBeDisplayed()) {
    const campaignButton = document.createElement('button');
    campaignButton.id = 'tournesol_campaign_button';
    campaignButton.className = 'tournesol_simple_button';

    const campaignButtonImg = document.createElement('img');
    campaignButtonImg.setAttribute(
      'src',
      chrome.extension.getURL('images/campaign.svg')
    );
    campaignButtonImg.setAttribute('alt', 'Megaphone icon');
    campaignButton.append(campaignButtonImg);

    campaignButton.onclick = () => {
      chrome.storage.local.set({ displayBannerStudy2023: true }, () => {
        displayElement(document.getElementById('tournesol_banner'));
      });
    };

    inline_div.append(campaignButton);
  }

  tournesol_container.append(inline_div);

  if (bannerShouldBeDisplayed()) {
    tournesol_container.append(createBanner());
  }

  const videosFlexContainer = createVideosFlexContainer();
  tournesol_container.append(videosFlexContainer);

  function make_video_box(video) {
    // Div whith everything about a video
    const video_box = document.createElement('div');
    video_box.className = 'video_box';

    // Div with thumbnail and video duration
    const thumb_div = document.createElement('div');
    thumb_div.setAttribute('class', 'thumb_div');

    const video_thumb = document.createElement('img');
    video_thumb.className = 'video_thumb';
    video_thumb.src = `https://img.youtube.com/vi/${video.metadata.video_id}/mqdefault.jpg`;
    thumb_div.append(video_thumb);

    const video_duration = document.createElement('p');
    video_duration.setAttribute('class', 'time_span');

    // Convert SECONDS to hh:mm:ss or mm:ss format depending on the duration

    var formatted_video_duration = convertDurationToClockDuration(
      video.metadata.duration
    );

    video_duration.append(document.createTextNode(formatted_video_duration));
    thumb_div.append(video_duration);

    const video_link = document.createElement('a');
    video_link.className = 'video_link';
    video_link.href = '/watch?v=' + video.metadata.video_id;
    thumb_div.append(video_link);

    video_box.append(thumb_div);

    // Div with uploader name, video title and tournesol score
    const details_div = document.createElement('div');
    details_div.setAttribute('class', 'details_div');

    const video_title = document.createElement('h2');
    video_title.className = 'video_title';

    const video_title_link = document.createElement('a');
    video_title_link.className = 'video_title_link';
    video_title_link.href = '/watch?v=' + video.metadata.video_id;
    video_title_link.append(video.metadata.name);

    video_title.append(video_title_link);
    details_div.append(video_title);

    const video_channel_details = document.createElement('div');
    video_channel_details.classList.add('video_channel_details');

    const video_uploader = document.createElement('p');
    video_uploader.className = 'video_text';

    const video_channel_link = document.createElement('a');
    video_channel_link.classList.add('video_channel_link');
    video_channel_link.textContent = video.metadata.uploader;
    video_channel_link.href = `https://youtube.com/channel/${video.metadata.channel_id}`;

    video_uploader.append(video_channel_link);
    video_channel_details.append(video_uploader);

    const video_views_publication = document.createElement('p');
    video_views_publication.className = 'video_text';
    video_views_publication.innerHTML = `${i18n.getMessage('views', [
      millifyViews(video.metadata.views),
    ])} <span class="dot">&nbsp•&nbsp</span> ${viewPublishedDate(
      video.metadata.publication_date
    )}`;
    video_channel_details.append(video_views_publication);
    details_div.append(video_channel_details);

    const video_score = document.createElement('p');
    video_score.className = 'video_text video_tournesol_rating';
    video_score.innerHTML = `<img
        class="tournesol_comparison_logo"
        src="https://tournesol.app/svg/tournesol.svg"
        alt="Tournesol logo"
      />
        <strong>
          ${video.tournesol_score.toFixed(0)}
          <span class="dot">&nbsp·&nbsp</span>
        </strong>
        <span>${i18n.getMessage('comparisonsBy', [
          video.n_comparisons,
        ])}</span>&nbsp
        <span class="contributors">
          ${i18n.getMessage('comparisonsContributors', [video.n_contributors])}
        </span>`;
    details_div.append(video_score);

    /**
     * If the content script is executed on the YT research page.
     */
    if (path == '/results') {
      const video_criteria = document.createElement('div');
      video_criteria.className = 'video_text video_criteria';

      if (video.criteria_scores.length > 1) {
        const sortedCriteria = video.criteria_scores
          .filter((criteria) => criteria.criteria != 'largely_recommended')
          .sort((a, b) => a.score - b.score);

        const lower = sortedCriteria[0];
        const higher = sortedCriteria[sortedCriteria.length - 1];

        const lowerCriteriaTitle = `${i18n.getMessage(
          lower.criteria
        )}: ${Math.round(lower.score)}`;
        const higherCriteriaTitle = `${i18n.getMessage(
          higher.criteria
        )}: ${Math.round(higher.score)}`;

        const lowerCriteriaIconUrl = `images/criteriaIcons/${lower.criteria}.svg`;
        const higherCriteriaIconUrl = `images/criteriaIcons/${higher.criteria}.svg`;
        let lowerCriteriaIcon;
        let higherCriteriaIcon;

        fetch(chrome.runtime.getURL(higherCriteriaIconUrl))
          .then((r) => r.text())
          .then((svg) => {
            higherCriteriaIcon =
              'data:image/svg+xml;base64,' + window.btoa(svg);

            if (higher.score > 0) {
              video_criteria.innerHTML += `${i18n.getMessage(
                'ratedHigh'
              )} <img src=${higherCriteriaIcon} title='${higherCriteriaTitle}' />`;
            }

            if (lower.score < 0) {
              fetch(chrome.runtime.getURL(lowerCriteriaIconUrl))
                .then((r) => r.text())
                .then(
                  (svg) =>
                    (lowerCriteriaIcon =
                      'data:image/svg+xml;base64,' + window.btoa(svg))
                )
                .then(() => {
                  video_criteria.innerHTML += ` ${i18n.getMessage(
                    'ratedLow'
                  )} <img src='${lowerCriteriaIcon}' title='${lowerCriteriaTitle}' />`;

                  details_div.append(video_criteria);
                });
            } else {
              details_div.append(video_criteria);
            }
          });
      } else {
        video_criteria.innerHTML = i18n.getMessage('noCriteriaScore');
      }
    }

    video_box.append(details_div);

    return video_box;
  }

  videos.forEach((video) => videosFlexContainer.append(make_video_box(video)));
  if (isExpanded) {
    additionalVideos.forEach((video) =>
      videosFlexContainer.append(make_video_box(video))
    );
  }
  tournesol_container.append(expand_button_container);

  if (path == '/results') {
    tournesol_container.classList.add('search');

    let viewMoreLink = document.createElement('a');
    viewMoreLink.className = 'tournesol_mui_like_button view_more_link';
    viewMoreLink.target = '_blank';
    viewMoreLink.rel = 'noopener';
    viewMoreLink.href = `https://tournesol.app/recommendations/?search=${search.substring(
      14
    )}&language=${recommandationsLanguages.replaceAll(
      ',',
      '%2C'
    )}&utm_source=extension`;
    viewMoreLink.textContent = i18n.getMessage('viewMore');

    tournesol_container.append(viewMoreLink);
  }

  return tournesol_container;
};

// This part creates video boxes from API's response JSON
function displayRecommendations() {
  if (!videos || videos.length === 0) {
    return;
  }

  // Timer will run until needed elements are generated
  var timer = window.setInterval(function () {
    /*
     ** Wait for needed elements to be generated
     ** It seems those elements are generated via javascript, so run-at document_idle in manifest is not enough to prevent errors
     **
     ** Some ids on video pages are duplicated, so I take the first non-duplicated id and search in its childs the correct div to add the recommendations
     ** Note: using .children[index] when child has no id
     */

    // Get the container on Youtube home page in which we will insert Tournesol's component
    const container = getParentComponent();
    if (!container) return;
    window.clearInterval(timer);

    // Verify that Tournesol's container has not yet been rendered
    const old_container = document.getElementById('tournesol_container');
    if (old_container) old_container.remove();

    // Generate component to display on Youtube home page

    const tournesol_component = getTournesolComponent();
    container.insertBefore(tournesol_component, container.children[1]);
  }, 300);
}

function process() {
  isPageLoaded = true;
  if (videos.length > 0) {
    displayRecommendations();
  } else if (!areRecommendationsLoaded) {
    // If the content script is loaded on a non-root URL the recommendations
    // are not loaded. So if the user then goes to the root URL and the content
    // script is not reloaded, we need to load the recommendations.
    loadRecommandations();
  }
}

function handleResponse({
  data: videosReponse,
  recommandationsLanguages: languagesString,
}) {
  areRecommandationsLoading = false;
  areRecommendationsLoaded = true;
  videos = videosReponse.slice(0, 4);
  additionalVideos = videosReponse.slice(4);
  recommandationsLanguages = languagesString;

  if (isPageLoaded) {
    displayRecommendations();
  }
}

function loadRecommandations() {
  // Only enable on youtube.com/
  if (location.pathname != '/' && location.pathname != '/results') return;

  if (areRecommandationsLoading) return;

  areRecommandationsLoading = true;

  if (location.pathname == '/results') {
    handleResponse({ data: [] });
    chrome.storage.local.get('searchEnabled', ({ searchEnabled }) => {
      if (searchEnabled) {
        let searchQuery = search
          .substring(1)
          .split('&')
          .reduce((cur, next) => {
            let param = next.split('=');
            if (param[0] === 'search_query') {
              return param[1];
            }
            return cur;
          }, null);

        chrome.runtime.sendMessage(
          {
            message: 'getTournesolSearchRecommendations',
            search: searchQuery,
            videosNumber: searchRecommandationNumber,
          },
          handleResponse
        );
      }
    });

    return;
  }

  chrome.runtime.sendMessage(
    {
      message: 'getTournesolRecommendations',
      videosNumber: videosPerRow,
      additionalVideosNumber: videosPerRow * (rowsWhenExpanded - 1),
    },
    handleResponse
  );
}

function millifyViews(videoViews) {
  // Intl.NumberFormat object is in-built and enables language-sensitive number formatting
  return Intl.NumberFormat('en', { notation: 'compact' }).format(videoViews);
}

function viewPublishedDate(publishedDate) {
  const date1 = new Date(publishedDate);
  const date2 = new Date();
  // we will find the difference in time of today's date and the published date, and will convert it into Days
  // after calculating no. of days, we classify it into days, weeks, months, years, etc.
  const diffTime = date2.getTime() - date1.getTime();

  if (diffTime < 0) {
    //in case the local machine UTC time is less than the published date
    return '';
  }
  const diffDays = Math.floor(diffTime / (1000 * 3600 * 24));

  if (diffDays == 0) {
    return i18n.getMessage('publishedToday');
  } else if (diffDays == 1) {
    return i18n.getMessage('publishedYesterday');
  } else if (diffDays < 31) {
    if (diffDays < 14) {
      return i18n.getMessage('publishedSomeDaysAgo', [diffDays]);
    } else {
      return i18n.getMessage('publishedSomeWeeksAgo', [
        Math.floor(diffDays / 7),
      ]);
    }
  } else if (diffDays < 365) {
    if (diffDays < 61) {
      return i18n.getMessage('publishedAMonthAgo');
    } else {
      return i18n.getMessage('publishedSomeMonthsAgo', [
        Math.floor(diffDays / 30),
      ]);
    }
  } else {
    if (diffDays < 730) {
      return i18n.getMessage('publishedAYearAgo');
    } else {
      return i18n.getMessage('publishedSomeYearsAgo', [
        Math.floor(diffDays / 365),
      ]);
    }
  }
}
