// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

const videosPerRow = 4;
const rowsWhenExpanded = 3;

// TODO: these values are placeholder values that will be updated.
const TS_BANNER_DATE_START = new Date('2022-01-01T00:00:00Z');
const TS_BANNER_DATE_END = new Date('2024-01-01T00:00:00Z');

let isExpanded = false;

let videos = [];
let additionalVideos = [];
let isPageLoaded = false;
let areRecommandationsLoading = false;
let areRecommendationsLoaded = false;

loadRecommandations();

document.addEventListener('yt-navigate-finish', process);
if (document.body) process();
else document.addEventListener('DOMContentLoaded', process);

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
    const contents = document.querySelector(
      '#primary > ytd-rich-grid-renderer'
    );
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
  if (found.startsWith(expected + "-")) {
    return true;
  }

  return false;
}

const getLocalizedBannerText = () => {
  if (isNavigatorLang('fr')) {
    return 'Le projet Tournesol est-il vraiment efficace? Nous étudions' +
           " actuellement l'impact de notre extension navigateur sur les" +
           " habitudes d'utilisation de YouTube. Rejoingnez notre étude" +
           ' pour nous aider à améliorer Tournesol !';
  }

  // Return the 'en' version by default.
  return 'Is the Tournesol project really effective? We are currently investigating' +
  " the impact of our browser extension on the YouTube viewers' habits. Join" +
  ' our research study to help us improve Tournesol!';
}

const getLocalizedActionButtonText = () => {
  if (isNavigatorLang('fr')) {
    return 'Participer';
  }

  return 'Join';
}

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

  const bannerIconContainer = document.createElement('div');
  const icon = document.createElement('img');
  icon.id = 'tournesol_banner_icon';
  icon.setAttribute('src', chrome.extension.getURL('images/campaign.svg'));
  icon.setAttribute('alt', 'Megaphone icon');
  bannerIconContainer.append(icon);

  // The first flex item is the text.
  const bannerTextContainer = document.createElement('div');
  const bannerText = document.createElement('p');
  bannerText.textContent = getLocalizedBannerText();
  bannerTextContainer.append(bannerText);

  // The second flex item is the action button.
  const actionButtonContainer = document.createElement('div');
  const actionButton = document.createElement('a');
  actionButton.textContent = getLocalizedActionButtonText();
  actionButton.className = 'tournesol_mui_like_button';
  actionButton.setAttribute('href', 'https://tournesol.app');
  actionButton.setAttribute('target', '_blank');
  actionButton.setAttribute('rel', 'noopener');
  actionButtonContainer.append(actionButton);

  banner.appendChild(bannerIconContainer);
  banner.appendChild(bannerTextContainer);
  banner.appendChild(actionButtonContainer);
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
  tournesol_title.append('Recommended by Tournesol');
  inline_div.append(tournesol_title);

  // Add title
  const tournesol_link = document.createElement('a');
  tournesol_link.id = 'tournesol_link';
  tournesol_link.href = 'https://tournesol.app';
  tournesol_link.append('learn more');
  inline_div.append(tournesol_link);

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
  // Expand button
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
  inline_div.append(expand_button);

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

    video_box.append(thumb_div);

    // Div with uploader name, video title and tournesol score
    const details_div = document.createElement('div');
    details_div.setAttribute('class', 'details_div');

    const video_title = document.createElement('h2');
    video_title.className = 'video_title';
    video_title.append(video.metadata.name);
    details_div.append(video_title);

    const video_uploader = document.createElement('p');
    video_uploader.className = 'video_text';
    video_uploader.append(video.metadata.uploader);
    details_div.append(video_uploader);

    const video_score = document.createElement('p');
    video_score.className = 'video_text';
    video_score.innerHTML = `🌻 <strong>${video.tournesol_score.toFixed(
      0
    )} &nbsp·&nbsp</strong>
         ${video.n_comparisons} comparisons by ${video.n_contributors}
         contributors`;
    details_div.append(video_score);

    const video_link = document.createElement('a');
    video_link.className = 'video_link';
    video_link.href = '/watch?v=' + video.metadata.video_id;
    video_box.append(video_link);

    video_box.append(details_div);

    return video_box;
  }

  videos.forEach((video) => videosFlexContainer.append(make_video_box(video)));
  if (isExpanded) {
    additionalVideos.forEach((video) =>
      videosFlexContainer.append(make_video_box(video))
    );
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

function handleResponse({ data: videosReponse }) {
  areRecommandationsLoading = false;
  areRecommendationsLoaded = true;
  videos = videosReponse.slice(0, 4);
  additionalVideos = videosReponse.slice(4);

  if (isPageLoaded) {
    displayRecommendations();
  }
}

function loadRecommandations() {
  // Only enable on youtube.com/
  if (location.pathname != '/') return;

  if (areRecommandationsLoading) return;

  areRecommandationsLoading = true;

  chrome.runtime.sendMessage(
    {
      message: 'getTournesolRecommendations',
      videosNumber: videosPerRow,
      additionalVideosNumber: videosPerRow * (rowsWhenExpanded - 1),
    },
    handleResponse
  );
}
