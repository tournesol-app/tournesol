// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

const videosPerRow = 4;
const rowsWhenExpanded = 3;
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

    const video_views_publication = document.createElement('p');
    video_views_publication.className = 'video_text';
    video_views_publication.innerHTML = `<strong>${video.metadata.views} &nbsp·&nbsp ${video.metadata.publication_date}</strong>`;
    details_div.append(video_views_publication);

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

  videos.forEach((video) => tournesol_container.append(make_video_box(video)));
  if (isExpanded) {
    additionalVideos.forEach((video) =>
      tournesol_container.append(make_video_box(video))
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
