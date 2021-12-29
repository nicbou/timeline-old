//import EntryMap from './entryMap.js'
import EntryMap from './previews/geolocation.js'
import JournalEditorEntry from './entries/journalEditor.js'
import Preview from './preview.js';
import SpinnerComponent from './spinner.js';
import TimelineActivityEntry from './entries/activity.js';
import TimelineImageEntry from './entries/image.js';
import TimelineNav from './timeline-nav.js';
import TimelinePostEntry from './entries/post.js'
import TimelineTextEntry from './entries/text.js'
import TimelineMessageEntry from './entries/message.js';
import TimelineMotionEntry from './entries/motion.js';
import TimelineVideoEntry from './entries/video.js';
import TransactionsEntry from './entries/transactions.js';
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
        motion: {
          readableName: 'activities',
          iconClass: 'fas fa-running',
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

        if (entry.schema.startsWith('activity.exercise.session')) {
          groups.motion.entries.push(entry);
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
    entryType: function(entry) {
      const s = entry.schema;
      if (s.startsWith('file.image') || s.startsWith('file.document.pdf')) {
        return 'image-entry';
      }
      else if(s.startsWith('file.video')) {
        return 'video-entry';
      }
      else if(s.startsWith('social.')) {
        return 'post-entry';
      }
      else if(s.startsWith('file.text')) {
        return 'text-entry';
      }
      else if(s.startsWith('activity.browsing')) {
        return 'activity-entry';
      }
      else if(s.startsWith('message.')) {
        return 'message-entry';
      }
      else if(s.startsWith('activity.exercise.session')) {
        return 'motion-entry';
      }
    },
  },
  template: `
    <div id="timeline">
      <header>
        <timeline-nav id="timeline-nav"></timeline-nav>
        <router-link :to="{ name: 'settings'}" class="button"><i class="fas fa-cogs"></i></router-link>
      </header>
      <main class="content-with-sidebar">
        <div class="sidebar">
          <h1 class="current-date">{{ timelineDate.format('LL') }}</h1>
          <span class="subtitle">{{ timelineDate.format('dddd') }}, {{ relativeTimelineDate }}</span>
          <ul class="recap" v-if="!isLoading">
            <li v-for="group in entryGroups" v-if="group.entries.length">
              <i :class="group.iconClass"></i>
              {{ group.entries.length }} {{ group.readableName }}
            </li>
          </ul>
          <entry-map class="map" v-show="!isLoading" :entries="entries"></entry-map>
        </div>
        <spinner v-if="isLoading"></spinner>
        <div class="content entries">
          <journal-editor v-if="!isLoading"></journal-editor>
          <component
            :entry="entry"
            :is="entryType(entry)"
            :key="entry.id"
            @select="openPreview"
            class="entry"
            v-for="entry in entries"
            v-if="entryType(entry) && !isLoading"></component>
          <transactions-entry v-if="!isLoading" :entries="entryGroups.transactions.entries"></transactions-entry>
        </div>
      </main>
      <preview :entry="selectedEntry" v-if="selectedEntry" @close="closePreview"></preview>
    </div>
  `
});