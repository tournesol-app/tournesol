import { TalkEntry } from './TalkEntry';
import type { TalkEntryList } from './TalkEntryList';
import talksData from './talks-en.json';
import talksFrData from './talks-fr.json';

export class TalksService {
  static TalksService() {
    throw new Error('Method not implemented.');
  }
  /**
   * List all recorded or upcoming discussions.
   * @returns TalkEntryList
   */
  public static talksList(langage: string): TalkEntryList {
    let talks = talksData;
    if (langage == 'fr') {
      talks = talksFrData;
    }
    const entries: TalkEntry[] = talks.map((talk) => ({
      uid: talk.uid,
      title: talk.title,
      name: talk.name,
      abstract: talk.abstract,
      date: talk.date,
      invitation_link: talk.invitation_link,
      youtube_link: talk.youtube_link,
    }));

    return {
      results: entries,
    };
  }
}
