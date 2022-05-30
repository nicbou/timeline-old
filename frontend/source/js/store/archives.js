import { RequestStatus } from './../models/requests.js';
import ArchiveService from './../services/archive-service.js';

export default {
  namespaced: true,
  state: {
    archives: [],
    archiveEndpoints: [],
    archivesRequestStatus: RequestStatus.NONE,
    archivesRequestPromise: null,
  },
  mutations: {
    SET_ARCHIVE_ENDPOINTS(state, archiveEndpoints) {
      state.archiveEndpoints = archiveEndpoints;
    },
    SET_ARCHIVES(state, archives) {
      state.archives = archives;
    },
    ADD_ARCHIVE(state, archive) {
      state.archives.push(archive);
    },
    DELETE_ARCHIVE(state, archive) {
      state.archives = state.archives.filter(a => a !== archive);
    },
    UPDATE_ARCHIVE(state, archive) {
      Object.assign(state.archives.find(a => a.key === archive.key), archive);
    },
    SET_ARCHIVES_REQUEST_PROMISE(state, promise) {
      state.archivesRequestPromise = promise;
    },
    ARCHIVES_REQUEST_SUCCESS(state) {
      state.archivesRequestStatus = RequestStatus.SUCCESS;
    },
    ARCHIVES_REQUEST_PENDING(state) {
      state.archivesRequestStatus = RequestStatus.PENDING;
    },
    ARCHIVES_REQUEST_FAILURE(state) {
      state.archivesRequestStatus = RequestStatus.FAILURE;
    },
  },
  actions: {
    async getArchiveEndpoints(context) {
      return ArchiveService.getEndpoints(context.rootState.auth.accessToken)
        .then(archiveEndpoints => {
          context.commit('SET_ARCHIVE_ENDPOINTS', archiveEndpoints);
          return archiveEndpoints;
        });
    },
    async getArchives(context, forceRefresh=false) {
      if (context.state.archivesRequestStatus === RequestStatus.NONE || forceRefresh) {
        context.commit('ARCHIVES_REQUEST_PENDING');
        const archivesRequestPromise = ArchiveService.get(context.rootState.auth.accessToken)
          .then(archives => {
            context.commit('SET_ARCHIVES', archives);
            context.commit('ARCHIVES_REQUEST_SUCCESS');
            return context.state.archives;
          })
          .catch(async response => {
            context.commit('SET_ARCHIVES', []);
            context.commit('ARCHIVES_REQUEST_FAILURE');
            return Promise.reject(response);
          });
        context.commit('SET_ARCHIVES_REQUEST_PROMISE', archivesRequestPromise);
        return archivesRequestPromise;
      }
      return context.state.archivesRequestPromise;
    },
    async createArchive(context, {archive, files}) {
      return ArchiveService.create(archive, files, context.rootState.auth.accessToken)
        .then((updatedArchive) => {
          context.commit('ADD_ARCHIVE', updatedArchive);
          return context.state.archives;
        });
    },
    async updateArchive(context, {archive, newFiles}) {
      return ArchiveService.update(archive, newFiles, context.rootState.auth.accessToken)
        .then((updatedArchive) => {
          context.commit('UPDATE_ARCHIVE', updatedArchive);
          return context.state.archives;
        });
    },
    async deleteArchive(context, archive) {
      return ArchiveService.delete(archive, context.rootState.auth.accessToken)
        .then(() => {
          context.commit('DELETE_ARCHIVE', archive);
          return context.state.archives;
        });
    },
    async deleteArchiveFile(context, fileId) {
      return ArchiveService.deleteFile(fileId, context.rootState.auth.accessToken);
    }
  }
};