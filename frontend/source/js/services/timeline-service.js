import ApiService from './api-service.js';

export default class extends ApiService {
  static getApiBase(){
    return super.getApiBase() + '/timeline';
  }

  static getEntries(date, filters, accessToken) {
    const requestUrl = new URL(this.getApiBase() + '/entries/');
    requestUrl.search = new URLSearchParams({
      date_on_timeline__gte: moment(date).startOf('day').toJSON(),
      date_on_timeline__lt: moment(date).startOf('day').add(1, 'day').toJSON(),
      ...filters
    });
    return this.fetchWithToken(requestUrl, {}, accessToken).then((response) => {
      return response.json();
    });
  }

  static saveEntry(entry, accessToken){
    const isNewEntry = entry.id === null || entry.id === undefined;
    const relativeUrl = isNewEntry ? '/entries/' : `/entries/${entry.id}/`
    return this.fetchWithToken(
      this.getApiBase() + relativeUrl,
      { 
        method: isNewEntry ? 'POST' : 'PUT',
        headers: { 'Content-Type': 'application/json', },
        body: JSON.stringify(entry),
      },
      accessToken
    ).then((response) => {
      return response.json();
    });
  }

  static deleteEntry(entry, accessToken) {
    return this.fetchWithToken(
      this.getApiBase() + `/entries/${entry.id}/`,
      { method: 'DELETE' },
      accessToken
    );
  }
}