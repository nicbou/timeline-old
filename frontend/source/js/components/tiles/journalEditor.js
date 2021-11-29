export default Vue.component('journal-editor', {
  data: function() {
    return {
      currentlyEditingEntryId: null,
      currentEntryDescription: "", // Don't update the description directly, to allow users to cancel changes
      isEditingNewEntry: false,
      newEntryDescription: "",
      asMarkdown: "",
    }
  },
  computed: {
    journalEntries: function() {
      return this.$store.state.timeline.entries.filter(e => e.schema === 'journal');
    },
    currentlyEditingEntry: function() {
      return this.journalEntries.find(e => e.id === this.currentlyEditingEntryId) || null;
    },
    prettyDate: function() {
      return moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true).format('LL');
    },
  },
  methods: {
    editEntry: function(entry) {
      this.currentlyEditingEntryId = entry.id;
      this.currentEntryDescription = entry.description;
      this.isEditingNewEntry = false;
      this.$nextTick(() => {
        this.$refs.editor[0].focus();
      });
    },
    editNewEntry: function() {
      this.isEditingNewEntry = true;
      this.$nextTick(() => {
        this.$refs.newEntryEditor.focus();
      });
    },
    addEntry: function() {
      // Use the current time, unless editing journal entries for a different day.
      const now = moment();
      const lastMinuteOfTheDay = moment(this.$store.state.route.query.date, 'YYYY-MM-DD', true).add(1, 'd').subtract(1, 'm');
      let dateOnTimeline = now.isAfter(lastMinuteOfTheDay) ? lastMinuteOfTheDay : now;

      this.$store.dispatch('timeline/addEntry', {
        'schema': 'journal',
        'source': 'frontend/web',
        'title': '',
        'description': this.newEntryDescription,
        'extra_attributes': {},
        'date_on_timeline': dateOnTimeline.format(),
      }).then(e => this.newEntryDescription = "");
    },
    updateEntry: function(){
      this.currentlyEditingEntry.description = this.currentEntryDescription;
      this.$store.dispatch('timeline/updateEntry', this.currentlyEditingEntry).then(e => this.currentlyEditingEntryId = null);
    },
    cancelChanges: function() {
      this.currentlyEditingEntryId = null;
    },
    markdownToHtml: function(text) {
      return text ? marked(text) : '<p class="placeholder">Add something to your journal...</p>';
    },
  },
  template: `
    <article class="post tile journal">
      <header>
        <span class="post-icon">
          <i class="fas fa-pen-square"></i>
        </span>
        <span class="post-title">
          {{ prettyDate }}
        </span>
      </header>
      <main>
        <div v-for="entry in journalEntries">
          <textarea ref="editor" class="journal-content" v-if="currentlyEditingEntryId === entry.id" v-model="currentEntryDescription"></textarea>
          <div class="input-group" v-if="currentlyEditingEntryId === entry.id">
            <button class="button" @click.stop.prevent="updateEntry">Save changes</button>
            <button class="button" @click.stop.prevent="cancelChanges">Cancel</button>
          </div>
          <div v-html="markdownToHtml(entry.description)" class="journal-content" v-if="currentlyEditingEntryId != entry.id" @click="editEntry(entry)"></div>
        </div>
        <div>
          <div v-html="markdownToHtml(newEntryDescription)" class="journal-content" v-if="!isEditingNewEntry" @click="editNewEntry"></div>
          <textarea ref="newEntryEditor" class="journal-content" v-if="isEditingNewEntry" v-model="newEntryDescription"></textarea>
          <div class="input-group" v-if="isEditingNewEntry">
            <button class="button" @click.stop.prevent="addEntry" :disabled="!newEntryDescription">Add to journal</button>
            <button class="button" @click.stop.prevent="newEntryDescription = ''; isEditingNewEntry = false">Cancel</button>
          </div>
        </div>
      </main>
    </article>
  `
});