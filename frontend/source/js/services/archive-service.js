const apiBase = `https://${window.location.hostname}/api/archive/`;
import ApiObjectService from './object-service.js';

export const archiveTypes = {
  facebook: 'Facebook',
  googletakeout: 'Google Takeout',
  gpx: 'GPX track',
  json: 'JSON entries',
  n26csv: 'N26 CSV export',
  telegram: 'Telegram',
  twitter: 'Twitter',
};

export default class extends ApiObjectService{
  static getApiBase() {
    return super.getApiBase() + 'archive/';
  }

  static objectToFormData(archive, attachedFiles) {
    const formData = new FormData();
    formData.append('key', archive.key);
    formData.append('description', archive.description);
    for (var i = 0; i < attachedFiles.length; i++) {
      formData.append('archive_files', attachedFiles[i], attachedFiles[i].name);
    }
    return formData;
  }

  static async getEndpoints() {
    const archiveEndpointsByType = await super.getEndpoints();
    delete archiveEndpointsByType.archivefile;
    return archiveEndpointsByType;
  }

  static async deleteFile(fileId) {
    return fetch(new URL(`archivefile/${fileId}/`, apiBase), { method: 'DELETE' });
  }
}