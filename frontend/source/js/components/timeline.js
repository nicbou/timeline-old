import EntryMap from './entryMap.js'
import JournalEditorTile from './tiles/journalEditor.js'
import Preview from './preview.js';
import SpinnerComponent from './spinner.js';
import TimelineActivityTile from './tiles/activity.js';
import TimelineImageTile from './tiles/image.js';
import TimelineNav from './timeline-nav.js';
import TimelinePostTile from './tiles/post.js'
import TimelineTextTile from './tiles/text.js'
import TimelineMessageTile from './tiles/message.js';
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
    isLoading: function() {
      return this.$store.state.timeline.entriesRequestStatus === RequestStatus.PENDING;
    },
    entryGroups: function() {
      const emptyGroups = {
        blog: {
          readableName: 'blog posts',
          iconClass: 'fas fa-rss-square',
          entries: [],
        },
        browsingHistory: {
          readableName: 'browsing entries',
          iconClass: 'fas fa-globe-americas',
          entries: [],
        },
        files: {
          readableName: 'files',
          iconClass: 'fas fa-file',
          entries: [],
        },
        geolocation: {
          readableName: 'geolocation pings',
          iconClass: 'fas fa-map-marker-alt',
          entries: [],
        },
        hackerNews: {
          readableName: 'Hacker News comments',
          iconClass: 'fab fa-y-combinator',
          entries: [],
        },
        images: {
          readableName: 'images',
          iconClass: 'fas fa-image',
          entries: [],
        },
        messages: {
          readableName: 'messages',
          iconClass: 'fas fa-comments',
          entries: [],
        },
        reddit: {
          readableName: 'reddit comments',
          iconClass: 'fab fa-reddit',
          entries: [],
        },
        transactions: {
          readableName: 'transactions',
          iconClass: 'fas fa-piggy-bank',
          entries: [],
        },
        twitter: {
          readableName: 'tweets',
          iconClass: 'fab fa-twitter',
          entries: [],
        },
        videos: {
          readableName: 'videos',
          iconClass: 'fas fa-video',
          entries: [],
        },
      };

      return this.entries.reduce(function(groups, entry) {
        if (entry.schema.startsWith('social.blog.')) {
          groups.blog.entries.push(entry);
        }

        if (entry.schema.startsWith('activity.browsing')) {
          groups.browsingHistory.entries.push(entry);
        }

        if (entry.schema.startsWith('file.')) {
          groups.files.entries.push(entry);
        }

        if (entry.extra_attributes.location && entry.extra_attributes.location.latitude && entry.extra_attributes.location.longitude) {
          groups.geolocation.entries.push(entry);
        }

        if (entry.schema.startsWith('social.hackernews.')) {
          groups.hackerNews.entries.push(entry);
        }

        if (entry.schema.startsWith('file.image.')) {
          groups.images.entries.push(entry);
        }

        if (entry.schema.startsWith('message')) {
          groups.messages.entries.push(entry);
        }

        if (entry.schema.startsWith('social.reddit.')) {
          groups.reddit.entries.push(entry);
        }

        if (entry.schema === 'finance.income' || entry.schema === 'finance.expense') {
          groups.transactions.entries.push(entry);
        }

        if (entry.schema.startsWith('social.twitter.')) {
          groups.twitter.entries.push(entry);
        }

        if (entry.schema.startsWith('file.video.')) {
          groups.videos.entries.push(entry);
        }
        return groups;
      }, emptyGroups);
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
      else if(s.startsWith('activity.browsing')) {
        return 'activity-tile';
      }
      else if(s.startsWith('message.')) {
        return 'message-tile';
      }
    },
  },
  template: `
    <div id="timeline">
      <timeline-nav id="timeline-nav"></timeline-nav>
      <div class="content-with-sidebar">
        <div class="sidebar">
          <h1 class="current-date">{{ timelineDate.format('LL') }}</h1>
          <span class="subtitle">{{ timelineDate.format('dddd') }}, {{ relativeTimelineDate }}</span>
          <ul class="recap" v-if="!isLoading">
            <li v-for="group in entryGroups" v-if="group.entries.length">
              <i :class="group.iconClass"></i>
              {{ group.entries.length }} {{ group.readableName }}
            </li>
          </ul>
          <entry-map v-if="!isLoading" :entries="entries" width="300" height="200"></entry-map>
        </div>
        <spinner v-if="isLoading"></spinner>
        <div class="tiles">
          <journal-editor v-if="!isLoading"></journal-editor>
          <component
            :entry="entry"
            :is="tileType(entry)"
            :key="entry.id"
            @select="openPreview"
            class="tile"
            v-for="entry in entries"
            v-if="tileType(entry) && !isLoading"></component>
          <transactions-tile v-if="!isLoading" :entries="entryGroups.transactions.entries"></transactions-tile>
        </div>
      </div>
      <preview :entry="selectedEntry" v-if="selectedEntry" @close="closePreview"></preview>
    </div>
  `
});