import TimelineEntryIcon from './entry-icon.js';

export default Vue.component('motion-entry', {
  props: ['entry'],
  computed: {
    period: function() {
      let hours = new Date(this.entry.date_on_timeline).getHours();
      if (hours < 12) {
        return 'morning';
      }
      else if (hours <= 18) {
        return 'afternoon';
      }
      else if (hours <= 24) {
        return 'evening';
      }
    },
    description: function() {
      return `${this.period} ${this.entry.title}`.toLowerCase()
        .split(' ')
        .map((s) => s.charAt(0).toUpperCase() + s.substring(1))
        .join(' ');
    },
    timeAndDistance: function() {
      let description = '';
      if (this.entry.extra_attributes.distance) {
        description += `${(parseFloat(this.entry.extra_attributes.distance)/1000).toFixed(1)} km`; 
      }
      if (this.entry.extra_attributes.duration) {
        description += ` in ${(parseFloat(this.entry.extra_attributes.duration)/60).toFixed(0)} min`;
      }
      return description;
    },
    iconClass: function() {
      if (this.entry.title == 'walking') {
        return 'fas fa-walking';
      }
      else if (this.entry.title == 'biking') {
        return 'fas fa-biking';
      }
      else if (this.entry.title == 'running') {
        return 'fas fa-running';
      }
      else if (this.entry.title == 'skiing') {
        return 'fas fa-skiing';
      }
      else if (this.entry.title == 'rowing') {
        return 'fas fa-rowing';
      }
      return 'fas fa-heart';
    },
  },
  template: `
    <div>
      <entry-icon :icon-class="iconClass" :entry="entry"></entry-icon>
      <div class="meta">Activity</div>
      <div class="content">
        {{ description }}
        <small v-if="timeAndDistance">{{ timeAndDistance }}</small>
      </div>
    </div>
  `
});