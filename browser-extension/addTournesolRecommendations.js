// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

const defaultVideoNumber = 4;
const rowsWhenExpanded = 3;
const totalVideoNumber = defaultVideoNumber * rowsWhenExpanded;
let isExpanded = false;

let videos = [];
let additionalVideos = [];
let isPageLoaded = false;
let areRecommandationsLoading = false;

loadRecommandations();

document.addEventListener('yt-navigate-finish', process);
if (document.body) process();
else document.addEventListener('DOMContentLoaded', process);

const getParentComponent = () => {
  try {
    // Get parent element for the boxes in youtube page
    contents = document
      .getElementById('visibility-monitor')
      .parentElement.children['content'].getElementsByTagName('ytd-page-manager')[0]
      .getElementsByTagName('ytd-browse')[0]
      .getElementsByTagName('ytd-two-column-browse-results-renderer')[0]
      .children['primary'].getElementsByTagName('ytd-rich-grid-renderer')[0];
    if (!contents || !contents.children[1]) return;
    return contents
  } catch (error) {
    return;
  }
}

const getTournesolComponent = () => {
    // Create new container
    tournesol_container = document.createElement('div');
    tournesol_container.id = 'tournesol_container';

    // Add inline-block div
    inline_div = document.createElement('div');
    inline_div.setAttribute('class', 'inline_div');

    // Add tournesol icon
    tournesol_icon = document.createElement('img');
    tournesol_icon.setAttribute('id', 'tournesol_icon');
    tournesol_icon.setAttribute(
      'src',
      //chrome.extension.getURL('rate_now_icon.png'),
      'https://tournesol.app/svg/tournesol.svg'
    );
    tournesol_icon.setAttribute('width', '24');
    inline_div.append(tournesol_icon);

    // Add title
    tournesol_title = document.createElement('h1');
    tournesol_title.id = 'tournesol_title';
    tournesol_title.append('Recommended by Tournesol');
    inline_div.append(tournesol_title);

    // Language options
    const makeLanguageLink = (lang) => {
      lang_option = document.createElement('a');
      lang_option.className = 'language_option';
      lang_option.href = '#';
      lang_option.setAttribute('role', 'button');
      lang_option.append(lang);
      lang_option.onclick = (event) => {
        event.preventDefault();
        localStorage.setItem('tournesol_extension_config_language', lang);
        loadRecommandations();
      };
      return lang_option;
    };
    inline_div.append(makeLanguageLink('de'));
    inline_div.append(makeLanguageLink('en'));
    inline_div.append(makeLanguageLink('fr'));

    // Add title
    tournesol_link = document.createElement('a');
    tournesol_link.id = 'tournesol_link';
    tournesol_link.href = 'https://tournesol.app';
    tournesol_link.append('learn more');
    inline_div.append(tournesol_link);

    // Refresh button
    refresh_button = document.createElement('img');
    refresh_button.setAttribute('id', 'refresh_button');
    refresh_button.setAttribute('src', chrome.runtime.getURL('images/Refresh_icon.png'));
    refresh_button.setAttribute('width', '24');
    refresh_button.className = 'icon';
    refresh_button.onclick = () => {
      refresh_button.className = 'icon-disabled';
      loadRecommandations(loadVideos = true, loadAdditionalVideos = isExpanded);
    };
    inline_div.append(refresh_button);
    // Expand button
    expand_button = document.createElement('img');
    expand_button.setAttribute('id', 'expand_button');
    // A new button is created on each video loading, the image must be loaded accordingly
    if(isExpanded){
      expand_button.setAttribute('src', chrome.runtime.getURL('images/Arrows-Retract-Arrow-icon.png'));
    }else{
      expand_button.setAttribute('src', chrome.runtime.getURL('images/Arrows-Expand-Arrow-icon.png'));
    }
    expand_button.setAttribute('width', '24');
    expand_button.className = "icon";
    expand_button.onclick = () => {
      expand_button.className = 'icon-disabled';
      if(!areRecommandationsLoading && !isExpanded){
        isExpanded = true;
        loadRecommandations(loadVideos = false, loadAdditionalVideos = true);
      }else if(isExpanded){
        isExpanded = false;
        displayRecommendations();
      }
    };
    inline_div.append(expand_button);

    tournesol_container.append(inline_div);

    // Push videos into new container
    video_box_height = contents.children[0].clientHeight;
    video_box_width = contents.children[0].clientWidth;

    function make_video_box(video) {
      // Div whith everything about a video
      const video_box = document.createElement('div');
      video_box.className = 'video_box';

      // Div with thumbnail and video duration
      const thumb_div = document.createElement('div');
      thumb_div.setAttribute('class', 'thumb_div');

      const video_thumb = document.createElement('img');
      video_thumb.className = 'video_thumb';
      video_thumb.src = `https://img.youtube.com/vi/${video.video_id}/mqdefault.jpg`;
      thumb_div.append(video_thumb);

      // TODO: This is commented out until our backend serves again the video duration in the metadata
      // const video_duration = document.createElement('p');
      // video_duration.setAttribute('class', 'time_span');

      // Remove useless '00:' as hour value (we keep it if it is as minute value)
      // var formatted_video_duration = video.duration;
      // if (formatted_video_duration.startsWith('00:'))
      //   formatted_video_duration = formatted_video_duration.substring(
      //     3,
      //     formatted_video_duration.length,
      //   );

      // video_duration.append(document.createTextNode(formatted_video_duration));
      // thumb_div.append(video_duration);

      video_box.append(thumb_div);

      // Div with uploader name, video title and tournesol score
      const details_div = document.createElement('div');
      details_div.setAttribute('class', 'details_div');

      const video_title = document.createElement('h2');
      video_title.className = 'video_title';
      video_title.append(video.name);
      details_div.append(video_title);

      const video_uploader = document.createElement('p');
      video_uploader.className = 'video_text';
      video_uploader.append(video.uploader);
      details_div.append(video_uploader);

      // Tournesol score
      // const video_score = document.createElement('p');
      // video_score.className = 'video_text';
      // video_score.append(
      //   'Rated ' +
      //     Number(video.tournesol_score).toFixed(0) +
      //     ' points by ' +
      //     video.rating_n_experts +
      //     ' users',
      // );
      // details_div.append(video_score);

      const video_link = document.createElement('a');
      video_link.className = 'video_link';
      video_link.href = '/watch?v=' + video.video_id;
      video_box.append(video_link);

      video_box.append(details_div);

      return video_box;
    }

    videos.forEach((video) => tournesol_container.append(make_video_box(video)));
    if(isExpanded){
      additionalVideos.forEach((video) => tournesol_container.append(make_video_box(video)));
    }
    
    return tournesol_container
}

// This part creates video boxes from API's response JSON
function displayRecommendations() {
  if (!videos || videos.length === 0) {
    return
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
    old_container = document.getElementById('tournesol_container');
    if (old_container) old_container.remove();
    
    // Generate component to display on Youtube home page
    tournesol_component = getTournesolComponent();
    
    container.insertBefore(tournesol_component, container.children[1]);
  }, 300);
}


function process(){
  isPageLoaded = true;
  if(videos.length > 0){
    displayRecommendations();
  }
}

function handleResponse({ data: videosReponse, loadVideos: loadVideos, loadAdditionalVideos: loadAdditionalVideos }){
  areRecommandationsLoading = false;
  if(loadVideos && loadAdditionalVideos){
    videos = videosReponse.slice(0,4);
    additionalVideos = videosReponse.slice(4);
  }else if(loadVideos){
    videos = videosReponse;
  }else if(loadAdditionalVideos){
    additionalVideos = videosReponse;
  }
  
  if(isPageLoaded){
    displayRecommendations();
  }
}

function loadRecommandations(loadVideos = true, loadAdditionalVideos = false) {
  // Only enable on youtube.com/
  if (location.pathname != '/') return;

  if(areRecommandationsLoading) return;
  
  areRecommandationsLoading = true;
  /*
   ** Send message to background.js to get recommendations from the API of Tournesol.
   ** I put video amount here because we can get the value of --ytd-rich-grid-posts-per-row (css) to know how many videos we should retreive from api
   */
  const language =
    localStorage.getItem('tournesol_extension_config_language') || 'en';

  const videoNumber = 
    (loadVideos ? defaultVideoNumber : 0) + (loadAdditionalVideos ? defaultVideoNumber * (rowsWhenExpanded - 1) : 0);
  
  chrome.runtime.sendMessage({
    message: 'getTournesolRecommendations',
    language: language,
    number: videoNumber,
    loadVideos: loadVideos,
    loadAdditionalVideos: loadAdditionalVideos
  }, handleResponse);
}
