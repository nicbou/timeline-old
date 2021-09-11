const apiBase = `https://${window.location.hostname}/api/archive/`;

export default class {
  static async getArchives() {
    // Fetch archives from multiple endpoints. Return a list of archives of all types.
    const archiveEndpointsByType = await fetch(new URL('', apiBase)).then(response => response.json());

    delete archiveEndpointsByType.archivefile;

    const allArchives = [];
    for (const [archiveType, archivesOfTypeUrl] of Object.entries(archiveEndpointsByType)) {
      const archivesOfTypeResponse = await fetch(archivesOfTypeUrl);
      const archivesOfType = await archivesOfTypeResponse.json();
      archivesOfType.forEach(archive => archive.type = archiveType);
      allArchives.push(...archivesOfType);
    }

    return allArchives;
  }

  static async updateArchive(archive, newFiles) {
    const formData = new FormData();
    formData.append('key', archive.key);
    formData.append('description', archive.description);
    for (var i = 0; i < newFiles.length; i++) {
      formData.append('archive_files', newFiles[i], newFiles[i].name);
    }
    return fetch(archive.url, {
      method: 'PUT',
      body: formData,
    }).then(response => response.json());
  }

  static async deleteArchive(archive) {
    return fetch(archive.url, {
      method: 'DELETE',
    });
  }

  static async deleteArchiveFile(fileId) {
    return fetch(new URL(`archivefile/${fileId}/`, apiBase), {
      method: 'DELETE',
    });
  }
}