import EntryRecap from './entryRecap.js'
import JournalEditorTile from './tiles/journalEditor.js'
import Preview from './preview.js';
import SpinnerComponent from './spinner.js';
import TimelineImageTile from './tiles/image.js';
import TimelineNav from './timeline-nav.js';
import TimelinePostTile from './tiles/post.js'
import TimelineTextTile from './tiles/text.js'
import TimelineThreadTile from './tiles/thread.js';
import TimelineVideoTile from './tiles/video.js';
import TransactionsTile from './tiles/transactions.js';
import { RequestStatus } from './../models/requests.js';

function makeRouteValid(to, from, next) {
  // Enforce a valid current date in the route
  if (to.query.date) {
    const newDate = moment(to.query.date, 'YYYY-MM-DD', true);
    if(newDate.isValid()) {
      next();
      return;
    }
  }
  next({
    name: 'timeline', query: { date: moment().format('YYYY-MM-DD') }
  });
}

export default Vue.component('timeline', {
  data: function() {
    return {
      selectedEntry: null,
    }
  },
  created: function() {
    this.$store.dispatch('timeline/getEntries');
  },
  watch: {
    '$route.query.date': function() {
      this.$store.dispatch('timeline/getEntries', true)
    }
  },
  beforeRouteEnter: makeRouteValid,
  beforeRouteUpdate: makeRouteValid,
  computed: {
    timelineDate: function(){
      return moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true);
    },
    relativeTimelineDate: function() {
      const duration = this.timelineDate.diff(moment().startOf('day'));
      return duration !== 0 ? moment.duration(duration).humanize(true) : 'today';
    },
    entries: function() {
      return this.$store.state.timeline.entries;
    },
    messageEntries: function() {
      return this.entries.filter(e => e.schema.startsWith('message'));
    },
    transactionEntries: function() {
      return this.entries.filter(e => e.schema === 'finance.income' || e.schema === 'finance.expense');
    },
    threads: function() {
      return this.messageEntries.reduce((threads, entry) => {
        const key = [entry.extra_attributes.sender_id, entry.extra_attributes.recipient_id].sort().join('<>');
        threads[key] = threads[key] || [];
        threads[key].push(entry);
        return threads;
      }, {});
    },
    isLoading: function() {
      return this.$store.state.timeline.entriesRequestStatus === RequestStatus.PENDING;
    },
  },
  methods: {
    openPreview: function(entry) {
      this.selectedEntry = entry;
    },
    closePreview: function() {
      this.selectedEntry = null;
    },
    tileType: function(entry) {
      const s = entry.schema;
      if (s.startsWith('file.image') || s.startsWith('file.document.pdf')) {
        return 'image-tile';
      }
      else if(s.startsWith('file.video')) {
        return 'video-tile';
      }
      else if(s.startsWith('social.')) {
        return 'post-tile';
      }
      else if(s.startsWith('file.text')) {
        return 'text-tile';
      }
    },
  },
  template: `
    <div id="timeline">
      <timeline-nav id="timeline-nav"></timeline-nav>
      <div class="content-with-sidebar">
        <div class="sidebar">
          <h1 class="current-date">{{ timelineDate.format('LL') }}</h1>
          <span class="subtitle">{{ relativeTimelineDate }}</span>
          <entry-recap :entries="entries"></entry-recap>
        </div>
        <spinner v-if="isLoading"></spinner>
        <div class="tiles">
          <journal-editor v-if="!isLoading"></journal-editor>
          <thread-tile :thread="thread" v-for="thread in threads"></thread-tile>
          <transactions-tile :entries="transactionEntries"></transactions-tile>
          <component class="tile" :is="tileType(entry)" v-if="tileType(entry)" :entry="entry" v-for="entry in entries" :key="entry.id" @select="openPreview"></component>
        </div>
      </div>
      <preview :entry="selectedEntry" v-if="selectedEntry" @close="closePreview"></preview>
    </div>
  `
});