export default Vue.component('journal-editor', {
  props: ['entry'],
  data: function() {
    return {
      unsavedDescription: '',
      isSaving: false,
    };
  },
  mounted: function() {
    this.$nextTick(() => {
      this.$refs.editor.focus();
    });
  },
  methods: {
    close: function(event) {
      this.$emit('close');
    },
    saveChanges: function(){
      this.isSaving = true;
      const now = moment();
      const lastMinuteOfTheDay = moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true).add(1, 'd').subtract(1, 'm');
      let dateOnTimeline = now.isAfter(lastMinuteOfTheDay) ? lastMinuteOfTheDay : now;
      this.$store.dispatch('timeline/addEntry', {
        'schema': 'journal',
        'source': 'frontend/web',
        'title': '',
        'description': this.unsavedDescription,
        'extra_attributes': {},
        'date_on_timeline': dateOnTimeline.format(),
      }).then(e => {
        this.unsavedDescription = null;
        this.isSaving = false;
        this.close();
      });
    },
  },
  template: `
    <div class="journal-editor modal">
      <textarea ref="editor" class="journal-content" v-model="unsavedDescription" placeholder="What are you up to?"></textarea>
      <div class="input-group">
        <button class="button" @click.stop.prevent="saveChanges" :disabled="isSaving">Save changes</button>
        <button class="button" @click.stop.prevent="close" :disabled="isSaving">Cancel</button>
      </div>
    </div>
  `
});