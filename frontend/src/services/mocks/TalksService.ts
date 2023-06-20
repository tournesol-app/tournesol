import { TalkEntry } from './TalkEntry';
import type { TalkEntryList } from './TalkEntryList';

import talksData from './talks.json';

export class TalksService {
  static TalksService() {
    throw new Error('Method not implemented.');
  }
  /**
   * List all recorded or upcoming discussions.
   * @returns TalkEntryList
   */
  public static talksList(): TalkEntryList {
    const entries: TalkEntry[] = talksData.map((talk) => ({
      uid: talk.uid,
      title: talk.title,
      name: talk.name,
      abstract: talk.abstract,
      date: talk.date,
      speaker: talk.speaker,
      invitation_link: talk.invitation_link,
      youtube_link: talk.youtube_link,
    }));

    return {
      results: entries,
    };
  }
}
