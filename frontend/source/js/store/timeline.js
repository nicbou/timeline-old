import { RequestStatus } from './../models/requests.js';
import TimelineService from './../services/timeline-service.js';

export default {
  namespaced: true,
  state: {
    entries: [],
    entriesRequestStatus: RequestStatus.NONE,
    entriesRequestPromise: null,
  },
  mutations: {
    SET_ENTRIES(state, entries) {
      state.entries = entries;
    },
    ENTRIES_REQUEST_SUCCESS(state) {
      state.entriesRequestStatus = RequestStatus.SUCCESS;
    },
    ENTRIES_REQUEST_PENDING(state) {
      state.entriesRequestStatus = RequestStatus.PENDING;
    },
    ENTRIES_REQUEST_FAILURE(state) {
      state.entriesRequestStatus = RequestStatus.FAILURE;
    },
  },
  actions: {
    async getEntries(context, forceRefresh=false) {
      const timelineDate = moment(this.state.route.query.date, 'YYYY-MM-DD');
      if (context.state.entriesRequestStatus === RequestStatus.NONE || forceRefresh) {
        context.commit('ENTRIES_REQUEST_PENDING');
        const entriesRequestPromise = TimelineService.getEntries(timelineDate)
          .then(entries => {
            context.commit('SET_ENTRIES', entries);
            context.commit('ENTRIES_REQUEST_SUCCESS');
            return context.state.entries;
          })
          .catch(err => {
            context.commit('SET_ENTRIES', []);
            context.commit('ENTRIES_REQUEST_FAILURE');
            return context.state.entries;
          });
        context.commit('SET_ENTRIES_REQUEST_PROMISE', entriesRequestPromise);
        return entriesRequestPromise;
      }
      return context.state.entriesRequestPromise;
    },
  }
};