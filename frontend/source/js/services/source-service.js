import ApiObjectService from './object-service.js';

export const sourceTypes = {
  filesystem: 'Filesystem',
  git: 'Git',
  hackernews: 'Hacker News',
  reddit: 'Reddit',
  rss: 'RSS',
  rsync: 'Rsync',
  trakt: 'Trakt',
  twitter: 'Twitter',
};

export default class extends ApiObjectService {
  static getApiBase() {
    return super.getApiBase() + '/source';
  }

  static objectToFormData(source, attachedFiles) {
    const formData = new FormData();
    formData.append('key', source.key);
    formData.append('description', source.description);
    return formData;
  }
}