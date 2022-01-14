// Youtube doesnt completely load a video page, so content script doesn't lauch correctly without these events

// This part is called on connection for the first time on youtube.com/*
/* ********************************************************************* */

document.addEventListener('yt-navigate-finish', process);

if (document.body) process();
else document.addEventListener('DOMContentLoaded', process);

let videosToCompare = [];
let popupActive = false;
let comparedVideoId = null;

/* ********************************************************************* */

function process() {
  // Get video id via URL
  let videoId = new URL(location.href).searchParams.get('v');

  // Only enable on youtube.com/watch?v=* pages
  if (!location.pathname.startsWith('/watch') || !videoId) return;

  // Timer will run until needed elements are generated
  let timer = window.setInterval(createButtonIsReady, 300);

  function createButtonIsReady() {
    /*
     ** Wait for needed elements to be generated
     ** It seems those elements are generated via javascript, so run-at document_idle in manifest is not enough to prevent errors
     **
     ** Some ids on video pages are duplicated, so I take the first non-duplicated id and search in its childs the correct div to add the button
     ** Note: using .children[index] when child has no id
     */
    if (
      !document.getElementById('menu-container') ||
      !document.getElementById('menu-container').children['menu'] ||
      !document.getElementById('menu-container').children['menu'].children[0] ||
      !document.getElementById('menu-container').children['menu'].children[0].children['top-level-buttons-computed']
    ) return;

    window.clearInterval(timer);

    // If the button already exists, don't create a new one
    if (document.getElementById('tournesol-rate-later-button')) {
      return;
    }

    // Create Buttons
    function getRateButton(buttonText){
      let rateButton = document.createElement('button');
      rateButton.className = 'tournesol-rate-button';

      // Image td for better vertical alignment
      let img_td = document.createElement('td');
      img_td.setAttribute('valign', 'middle');
      let image = document.createElement('img');
      image.setAttribute('id', 'tournesol-button-image');
      image.setAttribute('src', chrome.runtime.getURL('Logo128.png'));
      image.setAttribute('width', '20');
      img_td.append(image);
      rateButton.append(img_td);

      // Text td for better vertical alignment
      let text_td = document.createElement('td');
      text_td.setAttribute('valign', 'middle');
      text_td_text = document.createTextNode(buttonText)
      text_td.append(text_td_text);
      rateButton.append(text_td);

      return rateButton;
    }

    // Rate later button
    let rateLaterButton = getRateButton('Rate Later');
    rateLaterButton.setAttribute('id', 'tournesol-rate-later-button');
    rateLaterButton.onclick = () => {
      rateLaterButton.disabled = true;
      chrome.runtime.sendMessage(
        {
          message: 'addRateLater',
          video_id: videoId
        },
        (data) => {
          if (data.success) {
            rateLaterButton.getElementsByTagName('td')[1].firstChild.replaceWith(document.createTextNode('Done!'))
          }
          else {
            rateLaterButton.disabled = false;
          }
        }
      );
    }

    // Rate now button
    

    let rateNowButton = getRateButton('Rate Now');
    rateNowButton.setAttribute('id', 'tournesol-rate-now-button');
    rateNowButton.onclick = async () => {
      if(popupActive){
        popupActive = false;
        // Hide the popup and all its children
        document.getElementById("tournesol-popup-div").className = "tournesol-popup-hidden";
        return;
      }
      document.getElementById("tournesol-popup-div").className = "tournesol-popup-visible";
      popupActive = true;
    }

    
    let popupholder = document.createElement("div");
    popupholder.className = "tournesol-hidden";
    loadPopup(popupholder);

    // Insert after like and dislike buttons
    let div = document.getElementById('menu-container').children['menu'].children[0].children['top-level-buttons-computed'];
    div.insertBefore(rateLaterButton, div.children[2]);
    div.insertBefore(rateNowButton, div.children[2]);
    div.insertBefore(popupholder, div.children[2]);
  }
}

function videoIdToImg(id){
  return `http://img.youtube.com/vi/${id}/mqdefault.jpg` 
}

async function loadPopup(div){
  // Load the popup and adds it to an adjacent html element
  // (it doesn't matter since it is of fixed position)
  let htmlPopupResponse = await fetch(chrome.runtime.getURL("ratePopup.html"));
  let htmlPopup = await htmlPopupResponse.text();
  div.innerHTML += htmlPopup;

  // Hide the popup if the user clicks on anything except the popup itself and the rating buttons
  let buttonsDiv = document.getElementById('menu-container').children['menu'].children[0].children['top-level-buttons-computed'];
  onClickOutside(buttonsDiv, () => {
    document.getElementById("tournesol-popup-div").className = "tournesol-popup-hidden";
    popupActive = false;
  })
  chrome.runtime.sendMessage(
    {
      message: 'loadVideosToCompare'
    },
    (data) => {
      videosToCompare = data;
      const videoIndex = Math.floor(videosToCompare.length * Math.random());
      comparedVideoId = videosToCompare[videoIndex].video.video_id;
      const thisVideoThumbnail = videoIdToImg(comparedVideoId);
      document.getElementById("right-video-img").setAttribute("src", thisVideoThumbnail);
      document.getElementById("right-video-title").innerText = videosToCompare[videoIndex].video.name;
    }
  );

  
  let thisVideoId = (new URL(location)).searchParams.get('v');
  let thisVideoThumbnail = videoIdToImg(thisVideoId);
  document.getElementById("left-video-img").setAttribute("src", thisVideoThumbnail);

  let videoTitle = document.getElementById('info-contents').getElementsByTagName('h1')[0].children[0].innerText;
  document.getElementById("left-video-title").innerText = videoTitle;

  let submitButton = document.getElementById("tournesol-submit-button");
  submitButton.onclick = () => {
    document.getElementById('tournesol-popup-div').className = "tournesol-popup-hidden";
    popupActive = false;

    let rateNowButton = document.getElementById('tournesol-rate-now-button')
    rateNowButton.disabled = true;
    rateNowButton.getElementsByTagName('td')[1].firstChild.replaceWith(document.createTextNode('Done!'))

    let score = document.getElementById('tournesol-rate-range').value;
    
    chrome.runtime.sendMessage(
      {
        message: 'compareVideos',
        videoA: thisVideoId,
        videoB: comparedVideoId,
        score
      },
      (data) => {}
    );
  }
  
}


// Based on https://stackoverflow.com/questions/152975/how-do-i-detect-a-click-outside-an-element
function onClickOutside(element, f) {
  const isVisible = elem => !!elem && !!( elem.offsetWidth || elem.offsetHeight || elem.getClientRects().length );

  const outsideClickListener = event => {
      if (!element.contains(event.target) && isVisible(element)) {
        f();
      }
  };
  document.addEventListener('click', outsideClickListener);
}