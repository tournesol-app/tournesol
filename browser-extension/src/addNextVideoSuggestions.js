/**
 * Create the Rate Later and the Rate Now buttons.
 *
 * This content script is meant to be run on each YouTube video page.
 */

const TS_NEXT_VIDEO_SUGGESTIONS_CONTAINER_ID = 'ts-next-video-suggestions';
const TS_NEXT_VIDEO_SUGGESTIONS_CONTAINER_BEFORE_REF = 'related';

/**
 * Youtube doesnt completely load a video page, so content script doesn't
 * launch correctly without these events.
 *
 * This part is called on connection for the first time on youtube.com/*
 */
document.addEventListener('yt-navigate-finish', addSuggestions);

if (document.body) {
  addSuggestions();
} else {
  document.addEventListener('DOMContentLoaded', addSuggestions);
}

/**
 * The Tournesol video actions row contains the video actions related to the
 * Tournesol project.
 *
 * This container is meant to be displayed after the YouTube actions and
 * before the video descrition container.
 */
const createNextVideoSuggestionContainer = () => {
  const existing = document.getElementById(TS_NEXT_VIDEO_SUGGESTIONS_CONTAINER_ID);
  if (existing) {
    existing.remove();
  }

  const videoActions = document.createElement('div');
  videoActions.id = TS_NEXT_VIDEO_SUGGESTIONS_CONTAINER_ID;

  const container = document.getElementById(TS_NEXT_VIDEO_SUGGESTIONS_CONTAINER_BEFORE_REF);

  container.prepend(videoActions);
  return videoActions;
};

const getChannelName = () => {
  const channelNameEl = document.querySelector("#meta-contents #channel-name a")
  if (channelNameEl) {
    return channelNameEl.text;
  }
  return;
}

function getNextVideoSuggestionContainerParent() {
  const beforeRef = document.getElementById(TS_NEXT_VIDEO_SUGGESTIONS_CONTAINER_BEFORE_REF);
  if (!beforeRef) {
    return;
  }

  return document.getElementById(beforeRef.parentElement.id);
}

function addSuggestions() {
  const videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timers will run until needed elements are generated
  const timer = window.setInterval(createButtonIsReady, 300);

  /**
   * Create the Rate Later and the Rate Now buttons.
   */
  function createButtonIsReady() {
    const buttonsContainer = getNextVideoSuggestionContainerParent();
    if (!buttonsContainer) {
      return;
    }

    window.clearInterval(timer);
    const videoActions = createNextVideoSuggestionContainer();

    const addRateButton = ({ id, label, iconSrc, iconClass, onClick }) => {
      // Create Button
      const button = document.createElement('button');
      button.setAttribute('id', id);
      button.setAttribute('class', 'tournesol-rate-button');

      // Icon
      const image = document.createElement('img');
      image.classList.add('tournesol-button-image');
      if (iconClass) image.classList.add(iconClass);
      image.setAttribute('src', iconSrc);
      image.setAttribute('width', '24');
      button.append(image);

      // Label
      const text = document.createTextNode(label);
      button.append(text);

      const setLabel = (label) => {
        text.textContent = label;
      };

      const setIcon = (iconSrc) => {
        image.setAttribute('src', iconSrc);
      };

      button.onclick = onClick;
      videoActions.appendChild(button);

      return { button, setLabel, setIcon };
    };
    const channelName = getChannelName()
    addRateButton({
      id: 'tournesol-rate-now-button',
      label: channelName,
      iconSrc: chrome.runtime.getURL('images/compare.svg'),
      onClick: () => {alert(channelName)},
    });

  }
}
