export default Vue.component('new-journal-entry', {
  data: function() {
    return {
      unsavedDescription: '',
      isEditing: false,
      isSaving: false,
    };
  },
  methods: {
    edit: function() {
      this.isEditing = true;
      this.$nextTick(() => {
        this.$refs.editor.focus();
      });
    },
    saveChanges: function(){
      this.isSaving = true;

      // Use the current time, unless editing journal entries for a different day.
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
        this.isEditing = false;
        this.isSaving = false;
      });
    },
    cancelChanges: function() {
      this.isEditing = false;
    },
  },
  template: `
    <div class="journal journal-add">
      <i class="icon fas fa-pen-square"></i>
      <textarea ref="editor" class="journal-content" v-if="isEditing" v-model="unsavedDescription"></textarea>
      <div class="input-group" v-if="isEditing">
        <button class="button" @click.stop.prevent="saveChanges" :disabled="isSaving">Save changes</button>
        <button class="button" @click.stop.prevent="cancelChanges" :disabled="isSaving">Cancel</button>
      </div>
      <p v-if="!isEditing" class="placeholder" @click="edit">Add something to your journal...</p>
    </div>
  `
});