## Description

Server to display the webpage announcing that the site is offline and offering to submit an email address to be notified when it will be back up.

The server only logs the submitted emails for now.

## Build Server

`go build`

## Launch Server

`./offline-webpage`

## TODO

- store the submitted emails in a database along with client IP (for deduplication)
- limit the number of emails that can be submitted from a given IP per day
