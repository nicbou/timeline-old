const apiBase = `https://${window.location.hostname}/api/archive/`;

const displayNames = {
  facebook: 'Facebook',
  googletakeout: 'Google Takeout',
  gpx: 'GPX track',
  json: 'JSON entries',
  n26csv: 'N26 CSV export',
  telegram: 'Telegram',
  twitter: 'Twitter',
};

function archiveToFormData(archive, files) {
  const formData = new FormData();
  formData.append('key', archive.key);
  formData.append('description', archive.description);
  for (var i = 0; i < files.length; i++) {
    formData.append('archive_files', files[i], files[i].name);
  }
  return formData;
}

export default class {
  static async getArchives() {
    // Fetch archives from multiple endpoints. Return a list of archives of all types.
    const archiveEndpointsByType = await this.getArchiveEndpoints();
    const allArchives = [];
    for (const [archiveType, archivesOfTypeUrl] of Object.entries(archiveEndpointsByType)) {
      const archivesOfTypeResponse = await fetch(archivesOfTypeUrl);
      const archivesOfType = await archivesOfTypeResponse.json();
      archivesOfType.forEach(archive => archive.type = archiveType);
      allArchives.push(...archivesOfType);
    }

    return allArchives;
  }

  static async getArchiveEndpoints() {
    const archiveEndpointsByType = await fetch(new URL('', apiBase)).then(response => response.json());
    delete archiveEndpointsByType.archivefile;
    return archiveEndpointsByType;
  }

  static async createArchive(archive, files) {
    return fetch(new URL(`${archive.type}/`, apiBase), {
      method: 'POST',
      body: archiveToFormData(archive, files),
    }).then(response => response.json()).then(createdArchive => {
      createdArchive.type = archive.type;
      return createdArchive;
    });
  }

  static async updateArchive(archive, newFiles) {
    return fetch(archive.url, {
      method: 'PUT',
      body: archiveToFormData(archive, newFiles),
    }).then(response => response.json()).then(updatedArchive => {
      updatedArchive.type = archive.type;
      return updatedArchive;
    });
  }

  static async deleteArchive(archive) {
    return fetch(archive.url, { method: 'DELETE' });
  }

  static async deleteArchiveFile(fileId) {
    return fetch(new URL(`archivefile/${fileId}/`, apiBase), { method: 'DELETE' });
  }

  static getDisplayName(archiveType){
    return displayNames[archiveType] || archiveType;
  }
}