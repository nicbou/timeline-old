import ApiObjectService from './object-service.js';

export const archiveTypes = {
  facebook: 'Facebook',
  googletakeout: 'Google Takeout',
  gpx: 'GPX track',
  icalendar: 'iCalendar file',
  json: 'JSON entries',
  n26csv: 'N26 CSV export',
  reddit: 'Reddit',
  telegram: 'Telegram',
  twitter: 'Twitter',
};

export default class extends ApiObjectService{
  static getApiBase() {
    return super.getApiBase() + '/archive';
  }

  static objectToFormData(archive, attachedFiles) {
    const formData = new FormData();
    formData.append('key', archive.key);
    formData.append('description', archive.description);
    formData.append('date_from', archive.date_from || '');
    formData.append('date_until', archive.date_until || '');
    formData.append('date_processed', archive.date_processed || '');
    for (var i = 0; i < attachedFiles.length; i++) {
      formData.append('archive_files', attachedFiles[i], attachedFiles[i].name);
    }
    return formData;
  }

  static async getEndpoints(accessToken) {
    const archiveEndpointsByType = await super.getEndpoints(accessToken);
    delete archiveEndpointsByType.archivefile;
    return archiveEndpointsByType;
  }

  static deleteFile(fileId, accessToken) {
    return this.fetchJsonWithToken(this.getApiBase() + `/archivefile/${fileId}/`, { method: 'DELETE' }, accessToken);
  }
}